#!/usr/bin/env python3
"""영상·이미지 모델 특징을 같은 시간 정보로 다시 뽑기 (2026-10-30).

기존 특징은 이미지 모델(CLIP, DINOv2)이 프레임 3장 평균, 영상 모델(V-JEPA 2, VideoMAE)이 클립 전체에 흩은 16프레임 1회 입력 후
시공간 token 전체 평균이었다. 여기서는 모든 모델이 클립 전체를 촘촘히 보고, "언제"를 남기는 시간 4구간(클립 길이의 4등분) 특징을 함께 저장한다.

모델 (--model)
  vjepa2_win    facebook/vjepa2-vitg-fpc64-256. 초당 8장, 16프레임(2초) 창을 1초 간격으로. 블록 20·32·40 출력 token 을
                창마다 시간 평균 + 공간 2×2 구간으로 줄인 뒤 클립의 시간 4구간으로 모음 → (층 3, 시간 4, 공간 4, 1408)
  videomae_win  MCG-NJU/videomae-huge-finetuned-kinetics (픽셀 복원 사전학습 + Kinetics 동작 라벨 미세조정). 같은 창 방식, 마지막 층
                → (층 1, 시간 4, 공간 4, 1280)
  timesformer   facebook/timesformer-base-finetuned-k400. MindCaptioning (Horikawa 2025) 방식: 32프레임 간격 위치, 8곳보다 적으면
                균등 8장, 많으면 8장씩 창. 짧은 변 224 로 줄인 뒤 긴 변 방향 crop 3개. 층마다 token 평균 → (층 12, 768)
  xclip         microsoft/xclip-large-patch14 (영상-언어 대조 학습, 8프레임). 클립 전체 균등 8장 1개 + 시간 4구간마다 8장 → (1+4, 768)
  clip_2fps     openai/clip-vit-large-patch14 영상 부호화기 CLS (기존과 같은 출력), 초당 2장 (4~64장)
  dinov2_2fps   facebook/dinov2-giant CLS, 초당 2장
  siglip2_2fps  google/siglip2-so400m-patch14-384 이미지 임베딩, 초당 2장
  (이미지 모델 출력: 전체 평균 (D) + 시간 4구간 (4, D))

--perturb <조작> : 같은 영상의 프레임을 바꿔서 뽑는다 (출력 폴더 <model>__<조작>). 화면 조작 bright_0.6 bright_1.4 sat_0 sat_0.5 sat_1.5
  contrast_0.6 contrast_1.4 hue_90 blur_3 (PIL ImageEnhance·HSV·GaussianBlur), 시간 조작 reverse shuffle freeze (클립 전체 프레임 순서를
  뒤집기·섞기·가운데 프레임으로 고정). 원래 특징으로 학습한 정서 예측기가 예측을 얼마나 바꾸는지 보는 실험용 (perturbation_readout.py).
generate : 영상 1~2196 (--ids 가능), --shard k --nshards n. 영상마다 <out>/video_models/<model>/parts/<vid>.npz, 다시 돌리면 건너뜀
merge    : parts 를 모아 <out>/video_models/<model>/{global.npy, tbins.npy (있으면), video_id.tsv, info.json} 과
           특징 폴더 표준 형식 <out>/<이름>.npy + _video_id.tsv (전체 평균; 다층 모델은 층마다 따로)
사용: python build_video_model_features.py generate|merge --model <이름> --videos <mp4 폴더> --out <특징 폴더> [--device cuda]
"""
import argparse
import json
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd

N_VIDEOS = 2196
FFMPEG = "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffmpeg"  # 시스템 ffmpeg 에는 h264 디코더가 없다
FFPROBE = "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffprobe"
HF = {"vjepa2_win": "facebook/vjepa2-vitg-fpc64-256", "videomae_win": "MCG-NJU/videomae-huge-finetuned-kinetics",
      "timesformer": "facebook/timesformer-base-finetuned-k400", "xclip": "microsoft/xclip-large-patch14",
      "clip_2fps": "openai/clip-vit-large-patch14", "dinov2_2fps": "facebook/dinov2-giant",
      "siglip2_2fps": "google/siglip2-so400m-patch14-384"}
VJEPA_LAYERS = (20, 32, 40)
WIN, WIN_FPS, STRIDE = 16, 8.0, 8      # 창 16프레임, 초당 8장, 1초 간격
IMG_FPS, IMG_MIN, IMG_MAX = 2.0, 4, 64
N_TBIN = 4


def probe(path):
    out = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out); s = j["streams"][0]; num, den = s["r_frame_rate"].split("/")
    return s["width"], s["height"], float(j["format"]["duration"]), float(num) / float(den)


def decode(path, fps=None, short=None):
    """RGB 프레임 (T, H, W, 3). fps 를 주면 그 간격으로, short 를 주면 짧은 변을 그 크기로."""
    w, h, dur, nfps = probe(path)
    vf = []
    if fps:
        vf.append(f"fps={fps}")
    if short and min(w, h) > short:  # 큰 영상만 줄이고 작은 영상은 키우지 않는다
        s = short / min(w, h); w, h = max(2, int(round(w * s / 2)) * 2), max(2, int(round(h * s / 2)) * 2); vf.append(f"scale={w}:{h}")
    cmd = [FFMPEG, "-v", "error", "-i", str(path)] + (["-vf", ",".join(vf)] if vf else []) + ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    if len(fr) == 0:
        raise ValueError(f"프레임 없음: {path}")
    return fr, dur, nfps


def decode_exact_short(path, short):
    """짧은 변을 정확히 short 로 (키우기 포함)."""
    w, h, dur, nfps = probe(path)
    s = short / min(w, h); W, H = max(2, int(round(w * s / 2)) * 2), max(2, int(round(h * s / 2)) * 2)
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3), dur, nfps


PERTURB = ["bright_0.6", "bright_1.4", "sat_0", "sat_0.5", "sat_1.5", "contrast_0.6", "contrast_1.4", "hue_90", "blur_3",
           "reverse", "shuffle", "freeze"]


def perturb_frames(fr, name):
    """프레임 배열 (T, H, W, 3) uint8 에 조작을 건다."""
    if not name:
        return fr
    if name == "reverse":
        return fr[::-1].copy()
    if name == "shuffle":
        return fr[np.random.default_rng(0).permutation(len(fr))].copy()
    if name == "freeze":
        return np.repeat(fr[len(fr) // 2][None], len(fr), 0)
    from PIL import Image, ImageEnhance, ImageFilter
    kind, val = name.split("_"); val = float(val); out = []
    for f in fr:
        im = Image.fromarray(f)
        if kind == "bright":
            im = ImageEnhance.Brightness(im).enhance(val)
        elif kind == "sat":
            im = ImageEnhance.Color(im).enhance(val)
        elif kind == "contrast":
            im = ImageEnhance.Contrast(im).enhance(val)
        elif kind == "hue":
            h, s_, v = im.convert("HSV").split()
            h = h.point(lambda x: (x + int(round(val / 360 * 255))) % 256)
            im = Image.merge("HSV", (h, s_, v)).convert("RGB")
        elif kind == "blur":
            im = im.filter(ImageFilter.GaussianBlur(radius=val))
        out.append(np.asarray(im))
    return np.stack(out)


def tbin_of(times, dur):
    return np.minimum((np.asarray(times) / max(dur, 1e-6) * N_TBIN).astype(int), N_TBIN - 1)


def bin_mean(X, bins):
    """시간 구간마다 평균. 빈 구간은 가장 가까운 구간 값을 쓴다."""
    out = np.full((N_TBIN,) + X.shape[1:], np.nan, np.float32)
    for b in range(N_TBIN):
        if (bins == b).any():
            out[b] = X[bins == b].mean(0)
    have = [b for b in range(N_TBIN) if np.isfinite(out[b]).all()]
    for b in range(N_TBIN):
        if b not in have:
            out[b] = out[min(have, key=lambda c: abs(c - b))]
    return out


class Extractor:
    def __init__(self, name, device, perturb=None):
        self.perturb = perturb
        import torch
        import transformers as T
        self.torch, self.name, self.device, mid = torch, name, device, HF[name]
        dt = torch.bfloat16 if device.startswith("cuda") else torch.float32
        if name == "vjepa2_win":
            self.proc = T.AutoVideoProcessor.from_pretrained(mid); self.model = T.VJEPA2Model.from_pretrained(mid, dtype=dt)
        elif name == "videomae_win":
            self.proc = T.AutoImageProcessor.from_pretrained(mid); self.model = T.VideoMAEModel.from_pretrained(mid, dtype=dt)
        elif name == "timesformer":
            self.proc = T.AutoImageProcessor.from_pretrained(mid); self.model = T.TimesformerModel.from_pretrained(mid, dtype=dt)
        elif name == "xclip":
            self.proc = T.AutoProcessor.from_pretrained(mid); self.model = T.XCLIPModel.from_pretrained(mid, dtype=dt)
        elif name == "clip_2fps":
            self.proc = T.CLIPImageProcessor.from_pretrained(mid); self.model = T.CLIPVisionModel.from_pretrained(mid, dtype=dt)
        elif name == "dinov2_2fps":
            self.proc = T.AutoImageProcessor.from_pretrained(mid); self.model = T.Dinov2Model.from_pretrained(mid, dtype=dt)
        elif name == "siglip2_2fps":
            self.proc = T.AutoProcessor.from_pretrained(mid); self.model = T.AutoModel.from_pretrained(mid, dtype=dt)
        self.model = self.model.to(device).eval(); self.dt = dt

    def _decode(self, path, **kw):
        fr, dur, nfps = decode(path, **kw)
        return perturb_frames(fr, self.perturb), dur, nfps

    def _to(self, x):
        return x.to(self.device, self.dt)

    def video_windows(self, path):
        fr, dur, _ = self._decode(path, fps=WIN_FPS, short=256 if self.name == "vjepa2_win" else 224)
        starts = list(range(0, max(1, len(fr) - WIN + 1), STRIDE))
        if starts[-1] + WIN < len(fr):
            starts.append(len(fr) - WIN)
        per_win, centers = [], []
        for s in starts:
            clip = fr[s:s + WIN]
            if len(clip) < WIN:
                clip = np.concatenate([clip, np.repeat(clip[-1:], WIN - len(clip), 0)])
            per_win.append(self._window_tokens(clip)); centers.append((s + min(WIN, len(fr) - s) / 2) / WIN_FPS)
        W = np.stack(per_win)                                   # (창, 층, 1 + 공간 4, D)
        glob = W[:, :, 0].mean(0)                               # (층, D)
        tb = bin_mean(W[:, :, 1:], tbin_of(centers, dur))       # (시간 4, 층, 공간 4, D)
        return dict(global_=glob.astype(np.float16), tbins=np.transpose(tb, (1, 0, 2, 3)).astype(np.float16),
                    n_windows=len(starts), duration=dur)

    def _window_tokens(self, clip):
        torch = self.torch
        with torch.no_grad():
            if self.name == "vjepa2_win":
                x = self.proc(videos=[list(clip)], return_tensors="pt")["pixel_values_videos"]
                out = self.model(pixel_values_videos=self._to(x), skip_predictor=True, output_hidden_states=True)
                hs = [out.hidden_states[L] for L in VJEPA_LAYERS]; t, g = WIN // 2, x.shape[-1] // 16
            else:
                x = self.proc(list(clip), return_tensors="pt")["pixel_values"]
                out = self.model(pixel_values=self._to(x)); hs = [out.last_hidden_state]; t, g = WIN // 2, x.shape[-1] // 16
        res = []
        for h in hs:
            h = h[0].float().reshape(t, g, g, -1).mean(0)       # 창 안 시간 평균 → (g, g, D)
            q = g // 2
            sp = [h[:q, :q], h[:q, q:], h[q:, :q], h[q:, q:]]
            res.append(np.stack([h.mean((0, 1)).cpu().numpy()] + [s.mean((0, 1)).cpu().numpy() for s in sp]))
        return np.stack(res)                                    # (층, 5, D)

    def timesformer(self, path):
        torch = self.torch
        fr, dur, nfps = self._decode(path, short=224)
        if min(fr.shape[1:3]) < 224:  # 작은 영상은 짧은 변 224 로 키워야 crop 이 된다 (MindCaptioning 방식)
            fr, dur, nfps = decode_exact_short(path, 224); fr = perturb_frames(fr, self.perturb)
        pos = np.arange(0, len(fr), 32)
        groups = [np.linspace(0, len(fr) - 1, 8).round().astype(int)] if len(pos) < 8 else \
            [pos[i:i + 8] if len(pos[i:i + 8]) == 8 else np.r_[pos[i:], np.repeat(pos[-1], 8 - len(pos[i:]))] for i in range(0, len(pos), 8)]
        H, W = fr.shape[1:3]; L = max(H, W); offs = [0, (L - 224) // 2, L - 224]
        feats = []
        for gi in groups:
            for o in offs:
                crop = fr[gi][:, :, o:o + 224] if W >= H else fr[gi][:, o:o + 224, :]  # 긴 변 방향으로 세 위치
                crop = crop[:, :224, :224]
                x = self.proc(list(crop), return_tensors="pt", do_resize=False, do_center_crop=False)["pixel_values"]
                with torch.no_grad():
                    out = self.model(pixel_values=self._to(x), output_hidden_states=True)
                feats.append(np.stack([h[0].float().mean(0).cpu().numpy() for h in out.hidden_states[1:]]))
        return dict(global_=np.mean(feats, 0).astype(np.float16), n_windows=len(groups), duration=dur)

    def xclip(self, path):
        torch = self.torch
        fr, dur, _ = self._decode(path, fps=WIN_FPS, short=224)
        t = np.arange(len(fr)) / max(len(fr), 1) * dur
        sets = [np.linspace(0, len(fr) - 1, 8).round().astype(int)]
        for b in range(N_TBIN):
            idx = np.flatnonzero(tbin_of(t, dur) == b); idx = idx if len(idx) else np.arange(len(fr))
            sets.append(idx[np.linspace(0, len(idx) - 1, 8).round().astype(int)])
        embs = []
        for s in sets:
            x = self.proc.image_processor(list(fr[s]), return_tensors="pt")["pixel_values"]  # XCLIPProcessor(videos=) 는 4.57 에서 빈 결과
            with torch.no_grad():  # get_video_features 와 같은 계산. 4.57 에서는 하위 모듈이 tuple 을 돌려 직접 따라 쓴다
                pv = self._to(x); B, Tn, C, H, W_ = pv.shape
                vo = self.model.vision_model(pixel_values=pv.reshape(-1, C, H, W_), return_dict=True)
                ve = self.model.visual_projection(vo.pooler_output).view(B, Tn, -1)
                mo = self.model.mit(ve, return_dict=True)
                embs.append(mo.pooler_output[0].float().cpu().numpy())
        E = np.stack(embs)
        return dict(global_=E[0].astype(np.float16), tbins=E[1:].astype(np.float16), duration=dur)

    def frames(self, path):
        torch = self.torch
        _, _, dur0, _ = probe(path)
        n = int(np.clip(round(dur0 * IMG_FPS), IMG_MIN, IMG_MAX))
        fr, dur, _ = self._decode(path, fps=max(IMG_FPS, 2 * n / max(dur0, 1e-3)), short=384 if self.name == "siglip2_2fps" else 256)
        idx = np.linspace(0, len(fr) - 1, n).round().astype(int)
        times = idx / max(len(fr) - 1, 1) * dur; embs = []
        for i in range(0, n, 16):
            batch = list(fr[idx[i:i + 16]])
            with torch.no_grad():
                if self.name == "siglip2_2fps":
                    inp = self.proc(images=batch, return_tensors="pt")
                    inp = {k: (self._to(v) if v.is_floating_point() else v.to(self.device)) for k, v in inp.items()}
                    e = self.model.get_image_features(**inp)
                else:
                    x = self.proc(images=batch, return_tensors="pt")["pixel_values"]
                    o = self.model(pixel_values=self._to(x))
                    e = o.pooler_output if self.name == "clip_2fps" else o.last_hidden_state[:, 0]
            embs.append(e.float().cpu().numpy())
        E = np.concatenate(embs)
        return dict(global_=E.mean(0).astype(np.float16), tbins=bin_mean(E, tbin_of(times, dur)).astype(np.float16),
                    n_frames=n, duration=dur)

    def __call__(self, path):
        if self.name in ("vjepa2_win", "videomae_win"):
            return self.video_windows(path)
        if self.name == "timesformer":
            return self.timesformer(path)
        if self.name == "xclip":
            return self.xclip(path)
        return self.frames(path)


def tag(a):
    return a.model + (f"__{a.perturb}" if a.perturb else "")


def perturb_ids(out, n=240, seed=20261031):
    """조작 실험용 영상 목록 (분석 행 1~2185 중 무작위 n 개, 한 번 정하면 파일로 고정)."""
    p = out / "video_models" / "perturb_ids.txt"
    if not p.exists():
        sp = pd.read_csv("/pscratch/sd/s/sjmoon/EmoBrain/docs/reports/prelim_2026-10/splits/horikawa_rungroup6_v1.tsv", sep="\t")
        pool = sp[sp.analysis_row & ~sp.exclude_duplicate & (sp.video_id <= 2185)].video_id.values
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(map(str, sorted(np.random.default_rng(seed).choice(pool, n, replace=False)))))
    return [int(x) for x in p.read_text().split()]


def generate(a):
    root = a.out / "video_models" / tag(a) / "parts"; root.mkdir(parents=True, exist_ok=True)
    ids = [int(x) for x in a.ids.split(",")] if a.ids else (perturb_ids(a.out) if a.perturb else list(range(1, N_VIDEOS + 1)))
    ids = [v for i, v in enumerate(ids) if i % a.nshards == a.shard]
    todo = [v for v in ids if not (root / f"{v:04d}.npz").exists()]
    print(f"{a.model} shard {a.shard}/{a.nshards}: 대상 {len(ids)}, 남은 것 {len(todo)}", flush=True)
    if not todo:
        return
    ext = Extractor(a.model, a.device, a.perturb); t0 = time.time()
    for k, v in enumerate(todo):
        try:
            r = ext(a.videos / f"{v:04d}.mp4")
            np.savez(root / f"{v:04d}.npz", **{k_: np.asarray(x) for k_, x in r.items()})
        except Exception as e:  # 영상 하나가 실패해도 계속, 기록만
            (root.parent / "errors.log").open("a").write(f"{v}\t{type(e).__name__}: {e}\n")
        if k % 50 == 0:
            print(f"[{k + 1}/{len(todo)}] video {v} ({time.time() - t0:.0f}초)", flush=True)


def merge(a):
    d = a.out / "video_models" / tag(a); parts = sorted((d / "parts").glob("*.npz"))
    vids = [int(p.stem) for p in parts]
    missing = sorted(set(perturb_ids(a.out) if a.perturb else range(1, N_VIDEOS + 1)) - set(vids))
    if missing:
        print(f"아직 {len(missing)}개 없음 (예: {missing[:10]}). 다 모인 뒤 merge 한다."); return
    zs = [np.load(p) for p in parts]
    G = np.stack([z["global_"] for z in zs]).astype(np.float32); np.save(d / "global.npy", G)
    if "tbins" in zs[0].files:
        np.save(d / "tbins.npy", np.stack([z["tbins"] for z in zs]).astype(np.float16))
    pd.DataFrame(dict(video_id=vids)).to_csv(d / "video_id.tsv", sep="\t", index=False)
    if a.perturb:  # 조작 실험은 표준 특징 파일을 만들지 않는다
        (d / "info.json").write_text(json.dumps(dict(model=a.model, perturb=a.perturb, n=len(vids), global_shape=list(G.shape)), indent=1))
        print(f"{tag(a)}: {len(vids)}개 합침"); return
    names = []
    if a.model == "vjepa2_win":
        for i, L in enumerate(VJEPA_LAYERS):
            names.append((f"vjepa2win_l{L}", G[:, i]))
    elif a.model == "videomae_win":
        names.append(("videomaewin", G[:, 0]))
    elif a.model == "timesformer":
        names += [("timesformer_l12", G[:, 11]), ("timesformer_l6", G[:, 5])]
    else:
        names.append((a.model.replace("_2fps", "2fps"), G))
    for n, X in names:
        np.save(a.out / f"{n}.npy", X.astype(np.float32))
        pd.DataFrame(dict(video_id=vids)).to_csv(a.out / f"{n}_video_id.tsv", sep="\t", index=False)
    info = dict(model=a.model, hf=HF[a.model], n=len(vids), global_shape=list(G.shape), features=[n for n, _ in names])
    (d / "info.json").write_text(json.dumps(info, indent=1)); print(json.dumps(info, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["generate", "merge"]); ap.add_argument("--model", required=True, choices=list(HF))
    ap.add_argument("--videos", type=Path, default=Path("/pscratch/sd/s/sjmoon/EmoViS/data/raw/CowenEmotionVideos"))
    ap.add_argument("--out", type=Path, default=Path("/pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026"))
    ap.add_argument("--ids"); ap.add_argument("--shard", type=int, default=0); ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--device", default="cuda"); ap.add_argument("--perturb", choices=PERTURB)
    a = ap.parse_args()
    generate(a) if a.cmd == "generate" else merge(a)


if __name__ == "__main__":
    main()
