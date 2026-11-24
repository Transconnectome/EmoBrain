#!/usr/bin/env python3
"""채도·밝기를 바꾸면 이미지 모델의 정서 예측이 어떻게 움직이나: 빠른 확인판 (2026-10-31, 자극 수준, CPU).

영상: 4초 이하이고 한 감정이 가장 높은 평정 비율(≥ 0.4)을 받은 영상을 감정 10개에서 각각 비율 상위 8개 (중복 제외).
조작: 채도 0·0.5·1·1.5·2 배, 밝기 0.5·0.75·1·1.25·1.5 배 (PIL ImageEnhance, 원본 1 배는 공통).
특징: 기존 특징과 같은 방식 (EmoViS study1_07·08: 프레임 25·50·75% 지점 3장, CLIP ViT-L/14 pooler, DINOv2-giant CLS, 3장 평균).
정서 예측기: 기존 특징 (clip_vitl14 / dinov2) → 34개 범주 비율 ridge, 분할 horikawa_rungroup6_v1. 영상마다 그 영상이 평가 fold 였던 예측기.
모델이 배운 연관의 민감도이며, 조작한 영상의 사람 평정은 없다.
출력: <OUT>/13_perturbation/quick/{videos.tsv, predictions_<모델>.tsv, feature_check_<모델>.tsv}
사용: python perturb_quick.py [--models clip,dinov2]
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV

sys.path.insert(0, str(Path(__file__).parent))
import run_stage1 as rs  # noqa: E402

FFMPEG = "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffmpeg"
FFPROBE = "/pscratch/sd/s/sjmoon/swift_PTL2/bin/ffprobe"
VIDEOS = Path("/pscratch/sd/s/sjmoon/EmoViS/data/raw/CowenEmotionVideos")
DUR = "/pscratch/sd/s/sjmoon/MindCaptioning/manifests/video_dur_md5.csv"
EMOTIONS = ["amusement", "fear", "disgust", "adoration", "aesthetic appreciation", "awe", "sadness", "horror", "joy", "calmness"]
CONDS = [("orig", 1.0)] + [("sat", v) for v in (0, 0.5, 1.5, 2.0)] + [("bright", v) for v in (0.5, 0.75, 1.25, 1.5)]
HF = {"clip": ("openai/clip-vit-large-patch14", "clip_vitl14"), "dinov2": ("facebook/dinov2-giant", "dinov2")}


def frames3(path):
    dur = float(subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                               capture_output=True, text=True, check=True).stdout)
    w, h = map(int, subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                    "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout.strip().split(","))
    out = []
    for pos in (0.25, 0.5, 0.75):
        raw = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{pos * dur:.3f}", "-i", str(path), "-frames:v", "1",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        out.append(np.frombuffer(raw, np.uint8)[: h * w * 3].reshape(h, w, 3))
    return out


def perturb(img, kind, val):
    from PIL import Image, ImageEnhance
    im = Image.fromarray(img)
    if kind == "sat":
        im = ImageEnhance.Color(im).enhance(val)
    elif kind == "bright":
        im = ImageEnhance.Brightness(im).enhance(val)
    return im


def select_videos(vids, Y, cats):
    d = pd.read_csv(DUR, header=None, names=["video_id", "dur", "md5"]).set_index("video_id").dur
    Yd = pd.DataFrame(Y, index=vids, columns=cats)
    short = Yd[d.reindex(Yd.index).values <= 4.0]
    rows = []
    for e in EMOTIONS:
        top = short[(short.idxmax(axis=1) == e) & (short[e] >= 0.4)][e].sort_values(ascending=False).head(8)
        rows += [dict(video_id=int(v), emotion=e, rating=float(r), duration=float(d[v])) for v, r in top.items()]
    return pd.DataFrame(rows).drop_duplicates("video_id")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default="clip,dinov2"); a = ap.parse_args()
    import torch
    import transformers as T
    torch.set_num_threads(32)
    od = rs.OUT / "13_perturbation" / "quick"; od.mkdir(parents=True, exist_ok=True)
    split = pd.read_csv(rs.bb.SPLIT, sep="\t")
    split = split[split.analysis_row & ~split.exclude_duplicate & (split.video_id <= 2185)].set_index("video_id")
    vids = split.index.values; fold = pd.Series(split.fold.values, index=vids)
    cats, Y, _ = rs.cl.labels_for(vids)
    sel = select_videos(vids, Y, cats); sel.to_csv(od / "videos.tsv", sep="\t", index=False)
    print(f"영상 {len(sel)}개: " + ", ".join(f"{e} {n}" for e, n in sel.emotion.value_counts().items()), flush=True)
    frames = {v: frames3(VIDEOS / f"{v:04d}.mp4") for v in sel.video_id}
    F = rs.load_features(); preds, checks = [], []
    for m in a.models.split(","):
        hf, feat = HF[m]
        proc = T.CLIPImageProcessor.from_pretrained(hf) if m == "clip" else T.AutoImageProcessor.from_pretrained(hf)
        model = (T.CLIPVisionModel if m == "clip" else T.Dinov2Model).from_pretrained(hf).eval()
        X = F[feat].loc[vids].values.astype(np.float64); fits = {}
        for f in sorted(fold.unique()):
            tr = (fold != f).values; mu, sd = X[tr].mean(0), X[tr].std(0); sd[sd == 0] = 1
            fits[f] = (mu, sd, RidgeCV(alphas=np.logspace(-1, 6, 15)).fit((X[tr] - mu) / sd, Y[tr]))
        for v in sel.video_id:
            mu, sd, r = fits[fold[v]]
            for kind, val in CONDS:
                ims = [perturb(fr, kind, val) for fr in frames[v]]
                with torch.no_grad():
                    o = model(**proc(images=ims, return_tensors="pt"))
                    e = (o.pooler_output if m == "clip" else o.last_hidden_state[:, 0]).mean(0).numpy().astype(np.float64)
                if kind == "orig":
                    checks.append(dict(model=m, video_id=v, r_with_stored=np.corrcoef(e, F[feat].loc[v].values)[0, 1]))
                p = r.predict(((e - mu) / sd)[None])[0]
                preds += [dict(model=m, video_id=v, condition=kind, level=val, category=c, pred=p[k]) for k, c in enumerate(cats)]
            print(m, v, flush=True)
    tagm = a.models.replace(",", "_")
    pd.DataFrame(preds).to_csv(od / f"predictions_{tagm}.tsv", sep="\t", index=False, float_format="%.5f")
    ck = pd.DataFrame(checks); ck.to_csv(od / f"feature_check_{tagm}.tsv", sep="\t", index=False, float_format="%.4f")
    print(ck.groupby("model").r_with_stored.describe().to_string())


if __name__ == "__main__":
    main()
