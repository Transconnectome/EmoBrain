#!/usr/bin/env python3
"""S3 시각 모델 특징: V-JEPA 2(주), VideoMAE, TimeSformer, CLIP (04 S3, 01 3-1, 3-2, O10, O11, O14, O15, 2026-11-05).

사용: s3_vision.py --model vjepa2 [--ids 1-20] [--device cuda]
저장: project/output/final_2026-11/s3_features/<모델>/parts/v0001.npz. 사양이 같은 조각은 건너뛰고, 다르면 멈춘다. 파일로 모으는 일은 s3_collect.py가 한다.

층 번호는 1부터 센다. hidden_states[i]가 i번째 block의 출력이고 0번(embedding)은 쓰지 않는다(O15).
V-JEPA 2의 hidden_states[40]은 마지막 정규화층을 거친 값이다(transformers 4.57 VJEPA2Encoder). VideoMAE와 TimeSformer의 hidden_states에는 정규화층이 없다.
화면: 짧은 변을 입력 크기로 줄이고 가운데를 자른다(3-2). 화소 정규화와 보간 방식은 체크포인트의 전처리 설정 값을 쓴다. 공식 전처리 전체와 같지는 않다. ex) V-JEPA 2 공식 설정은 짧은 변 292에서 256을 자르지만 3-2의 공통 화면 범위를 위해 256으로 바로 줄인다.
"""
import argparse

import numpy as np
import torch
from torchvision.transforms import InterpolationMode
from torchvision.transforms.v2 import functional as TF

import s3_common as c

CONFIG = dict(
    vjepa2=dict(checkpoint="facebook/vjepa2-vitg-fpc64-256", fps=4, window=64, size=256, layers=list(range(1, 41))),
    videomae=dict(checkpoint="MCG-NJU/videomae-base", fps=4, window=16, size=224, layers=[3, 6, 9, 12]),
    timesformer=dict(checkpoint="facebook/timesformer-base-finetuned-k400", clip_frames=8, native_stride=32, size=224, layers=list(range(1, 13))),
    clip=dict(checkpoint="openai/clip-vit-base-patch16", fps=4, size=224),
)
INTERPOLATION = {2: InterpolationMode.BILINEAR, 3: InterpolationMode.BICUBIC}


def official_values(path):
    """체크포인트 전처리 설정의 평균, 표준편차, 보간 방식(PIL 번호)."""
    from transformers import AutoImageProcessor, AutoVideoProcessor
    try:
        p = AutoVideoProcessor.from_pretrained(path, local_files_only=True)
    except Exception:
        p = AutoImageProcessor.from_pretrained(path, local_files_only=True)
    return np.asarray(p.image_mean, np.float32), np.asarray(p.image_std, np.float32), int(p.resample)


def resize_short(frames, size, resample):
    """(T, H, W, 3) uint8 → (T, 3, nh, nw) uint8. 짧은 변을 size로 줄인다."""
    x = torch.from_numpy(frames).permute(0, 3, 1, 2)
    nh, nw = c.scaled_shape(x.shape[2], x.shape[3], size)
    return TF.resize(x, [nh, nw], interpolation=INTERPOLATION[resample], antialias=True)


def crop_at(x, size, offset):
    """긴 변을 따라 offset에서 자른다."""
    return x[:, :, offset:offset + size, :size] if x.shape[2] >= x.shape[3] else x[:, :, :size, offset:offset + size]


def normalize(x, mean, std, device):
    m, s = torch.tensor(mean).view(1, 3, 1, 1), torch.tensor(std).view(1, 3, 1, 1)
    return ((x.float().div(255.0).clamp(0, 1) - m) / s).to(device)


def to_input(frames, size, mean, std, resample, device):
    """짧은 변을 줄이고 가운데를 자른 뒤 정규화한다."""
    x = resize_short(frames, size, resample)
    spare = max(x.shape[2], x.shape[3]) - size
    return normalize(crop_at(x, size, spare // 2), mean, std, device)


def timesformer_clips(pts, duration, stride=32, length=8):
    """O14. 공개 코드에 추출 부분이 없어(04 S1) 01의 서술대로 구성하고 반복 재현 영상의 프레임 순서에 적용한다."""
    seq = c.presented_native_sequence(pts, duration)
    pos = np.arange(0, len(seq), stride)
    if len(pos) < length:
        return [seq[np.linspace(0, len(seq) - 1, length).round().astype(int)]]
    starts = list(range(0, len(pos) - length + 1, length))
    if starts[-1] != len(pos) - length:
        starts.append(len(pos) - length)
    return [seq[pos[s:s + length]] for s in starts]


def three_crops(frames, size, resample):
    """세 위치(왼쪽, 가운데, 오른쪽 또는 위, 가운데, 아래)."""
    x = resize_short(frames, size, resample)
    spare = max(x.shape[2], x.shape[3]) - size
    return [crop_at(x, size, off) for off in (0, spare // 2, spare)]


def load_model(name, path, device):
    if name == "vjepa2":
        from transformers import VJEPA2Model as M
    elif name == "videomae":
        from transformers import VideoMAEModel as M
    elif name == "timesformer":
        from transformers import TimesformerModel as M
    else:
        from transformers import CLIPModel as M
    return M.from_pretrained(path, local_files_only=True).to(device).eval()


def block_means(model, name, x, layers):
    """(T, 3, S, S) → (층, 폭). 입력 안의 시공간 token 평균."""
    if name == "vjepa2":
        h = model(pixel_values_videos=x[None], skip_predictor=True, output_hidden_states=True).hidden_states
        if len(h) != 41:
            raise ValueError(f"block 수가 40이 아니다: {len(h) - 1}")
    else:
        h = model(pixel_values=x[None], output_hidden_states=True).hidden_states
    return torch.stack([h[i].mean(1)[0] for i in layers]).cpu().numpy().astype(np.float32)


def extract(a):
    import transformers
    cfg = CONFIG[a.model]
    snap = c.hf_snapshot(cfg["checkpoint"])
    path = snap["path"]
    mean, std, resample = official_values(path)
    settings = dict(cfg, **{k: snap[k] for k in ("revision", "weights_sha256")}, normalize_mean=mean.tolist(), normalize_std=std.tolist(), resample_pil=resample, screen="짧은 변을 size로 줄인 뒤 긴 변의 0, floor(남는 길이 / 2), 남는 길이 세 위치에서 자름, 크기는 round, antialias" if a.model == "timesformer" else "짧은 변을 size로 줄인 뒤 가운데를 자름, 크기는 round, 자르는 위치는 floor((긴 변 − size) / 2), antialias", odd_frames="N이 window 이하이면 홀수일 때 마지막 한 장을 뺌. N이 window를 넘으면 빼지 않고 마지막 창을 끝에 맞춤(O11)" if "window" in cfg else "해당 없음", pooling=dict(vjepa2="입력 안 token 평균, 창이 여럿이면 창 평균", videomae="입력 안 token 평균, 창 평균", timesformer="CLS를 뺀 token 평균, 클립과 세 위치에 걸쳐 평균", clip="프레임별 투영 벡터를 L2 정규화해 평균하고 다시 정규화")[a.model], transformers=transformers.__version__, torch=torch.__version__)
    spec_id = c.make_spec(a.model, ["s3_common.py", "s3_vision.py"], allow_dirty=a.allow_dirty, **settings)
    table = c.stimulus_table()
    model = load_model(a.model, path, a.device)
    ids = c.todo_ids(a.model, c.parse_ids(a.ids), spec_id)
    print(a.model, "사양", spec_id, "할 영상", len(ids), flush=True)
    for n, v in enumerate(ids):
        c.check_video(table, v)
        vpath, duration = table.path[v], float(table.container_duration_s[v])
        pts = c.frame_pts(vpath)
        info = dict(n_native_frames=len(pts), duration_s=duration)
        with torch.no_grad():
            if a.model in ("vjepa2", "videomae"):
                idx = c.pick_by_time(pts, duration, cfg["fps"])
                frames = c.read_frames(vpath, idx)
                win = c.windows(len(idx), cfg["window"])
                per = np.stack([block_means(model, a.model, to_input(frames[s:e], cfg["size"], mean, std, resample, a.device), cfg["layers"]) for s, e in win])
                c.save_part(a.model, v, spec_id, mean=per.mean(0), per_window=per, n_frames=len(idx), windows=np.array(win), **info)
            elif a.model == "timesformer":
                clips = timesformer_clips(pts, duration, cfg["native_stride"], cfg["clip_frames"])
                out = []
                for clip in clips:
                    for crop in three_crops(c.read_frames(vpath, clip), cfg["size"], resample):
                        h = model(pixel_values=normalize(crop, mean, std, a.device)[None], output_hidden_states=True).hidden_states
                        out.append(torch.stack([h[i][:, 1:].mean(1)[0] for i in cfg["layers"]]).cpu().numpy().astype(np.float32))  # CLS token은 뺀다
                c.save_part(a.model, v, spec_id, mean=np.mean(out, 0), n_clips=len(clips), **info)
            else:
                idx = c.pick_by_time(pts, duration, cfg["fps"])
                x = to_input(c.read_frames(vpath, idx), cfg["size"], mean, std, resample, a.device)
                out = torch.cat([model.get_image_features(pixel_values=x[i:i + 64]) for i in range(0, len(x), 64)])
                out = torch.nn.functional.normalize(torch.nn.functional.normalize(out, dim=1).mean(0), dim=0)
                c.save_part(a.model, v, spec_id, mean=out.cpu().numpy().astype(np.float32), n_frames=len(idx), **info)
        if n % 50 == 0:
            print(n, "/", len(ids), "영상", v, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=list(CONFIG), required=True)
    ap.add_argument("--ids", default="")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--allow-dirty", action="store_true", help="시험용. 커밋 전 코드로 돌린다")
    extract(ap.parse_args())
