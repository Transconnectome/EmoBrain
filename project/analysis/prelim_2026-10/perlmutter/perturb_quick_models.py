#!/usr/bin/env python3
"""채도·밝기 조작 빠른 확인판을 영상·이미지 모델 일곱 개로 (2026-10-31, GPU 권장).

perturb_quick.py 와 같은 영상 79개 (13_perturbation/quick/videos.tsv) 와 같은 조작 (원본, 채도 0·0.5·1.5·2 배, 밝기 0.5·0.75·1.25·1.5 배).
특징은 build_video_model_features.py 와 같은 경로 (클립 전체: 영상 모델은 2초 창, 이미지 모델은 초당 2장) 로 조작한 프레임에서 다시 뽑는다.
정서 예측기: video_models/<모델>/global.npy (조작 안 한 2196개) → 34개 범주 비율 ridge, 분할 horikawa_rungroup6_v1.
영상마다 그 영상이 평가 fold 였던 예측기를 쓴다. 사람 평정은 바꾸지 않으며 조작한 영상의 평정은 없다 (모델 민감도).
출력: <OUT>/13_perturbation/quick/predictions_<모델 태그>.tsv (그림은 perturb_quick_figures.py)
사용: python perturb_quick_models.py --models vjepa2_win,videomae_win,timesformer,xclip,clip_2fps,dinov2_2fps,siglip2_2fps [--device cuda]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "features"))
import run_stage1 as rs  # noqa: E402
import build_video_model_features as bv  # noqa: E402

VM = Path("/pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026/video_models")
VIDEOS = Path("/pscratch/sd/s/sjmoon/EmoViS/data/raw/CowenEmotionVideos")
CONDS = [(None, "orig", 1.0)] + [(f"sat_{v}", "sat", v) for v in (0.0, 0.5, 1.5, 2.0)] + [(f"bright_{v}", "bright", v) for v in (0.5, 0.75, 1.25, 1.5)]
LAYER = {"vjepa2_win": [("vjepa2_l40", 2), ("vjepa2_l32", 1)], "videomae_win": [("videomae", 0)], "timesformer": [("timesformer_l12", 11)],
         "xclip": [("xclip", None)], "clip_2fps": [("clip_2fps", None)], "dinov2_2fps": [("dinov2_2fps", None)], "siglip2_2fps": [("siglip2_2fps", None)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="vjepa2_win,videomae_win,timesformer,xclip,clip_2fps,dinov2_2fps,siglip2_2fps")
    ap.add_argument("--device", default="cuda"); ap.add_argument("--limit", type=int, help="시험용: 앞의 영상 몇 개만"); a = ap.parse_args()
    od = rs.OUT / "13_perturbation" / "quick"
    sel = pd.read_csv(od / "videos.tsv", sep="\t").video_id.values
    sel = sel[: a.limit] if a.limit else sel
    split = pd.read_csv(rs.bb.SPLIT, sep="\t")
    split = split[split.analysis_row & ~split.exclude_duplicate & (split.video_id <= 2185)].set_index("video_id")
    vids = split.index.values; fold = pd.Series(split.fold.values, index=vids)
    cats, Y, _ = rs.cl.labels_for(vids)
    for m in a.models.split(","):
        G = np.load(VM / m / "global.npy").astype(np.float64)
        gid = pd.read_csv(VM / m / "video_id.tsv", sep="\t").video_id.values; pos = {v: i for i, v in enumerate(gid)}
        ext = bv.Extractor(m, a.device); feats = {}
        for v in sel:
            for pname, _, _ in CONDS:
                ext.perturb = pname
                feats[(v, pname)] = np.asarray(ext(VIDEOS / f"{v:04d}.mp4")["global_"], np.float64)
            print(m, v, flush=True)
        del ext
        for tagname, layer in LAYER[m]:
            take = (lambda g: g) if layer is None else (lambda g, L=layer: g[L])
            X = np.stack([take(G[pos[v]]) for v in vids]); fits = {}
            for f in sorted(fold.unique()):
                tr = (fold != f).values; mu, sd = X[tr].mean(0), X[tr].std(0); sd[sd == 0] = 1
                fits[f] = (mu, sd, RidgeCV(alphas=np.logspace(-1, 6, 15)).fit((X[tr] - mu) / sd, Y[tr]))
            preds, checks = [], []
            for v in sel:
                mu, sd, r = fits[fold[v]]
                for pname, kind, val in CONDS:
                    e = take(feats[(v, pname)])
                    if pname is None:
                        checks.append(np.corrcoef(e, take(G[pos[v]]))[0, 1])
                    p = r.predict(((e - mu) / sd)[None])[0]
                    preds += [dict(model=tagname, video_id=v, condition=kind, level=val, category=c, pred=p[k]) for k, c in enumerate(cats)]
            pd.DataFrame(preds).to_csv(od / f"predictions_{tagname}.tsv", sep="\t", index=False, float_format="%.5f")
            print(f"{tagname}: 원본 재계산과 저장 특징 r 중앙값 {np.median(checks):.4f}, 최소 {np.min(checks):.4f}", flush=True)


if __name__ == "__main__":
    main()
