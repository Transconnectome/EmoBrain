#!/usr/bin/env python3
"""같은 영상의 밝기·채도·대비·색조·흐림·시간 순서를 바꾸면 시각 모델의 정서 예측이 얼마나 바뀌나 (2026-10-31, 자극 수준).

정서 예측기: 조작하지 않은 특징 (video_models/<model>/global.npy) → 34개 범주 비율 ridge, 분할 horikawa_rungroup6_v1 6겹.
영상마다 그 영상이 평가 fold 였던 예측기를 써서 (학습에 그 영상이 없음) 원래 특징과 조작한 특징 (video_models/<model>__<조작>/global.npy) 의
예측을 비교한다. 이것은 모델의 민감도이지 사람 평정의 변화가 아니다 (조작한 영상의 사람 평정은 없다).
지표 (조작 × 모델)
  feature_r    : 조작 전후 특징 벡터의 상관 (영상 평균)
  profile_r    : 조작 전후 34개 예측 프로필의 상관 (영상 평균)
  shift_sd     : |Δ 예측| 을 영상 사이 예측 SD 로 나눈 값의 범주 평균
  by_category  : 범주별 평균 Δ (영상 사이 예측 SD 단위, 부호 있음)
출력: <OUT>/13_perturbation/{summary.tsv, by_category.tsv}
사용: python perturbation_readout.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV

sys.path.insert(0, str(Path(__file__).parent))
import run_stage1 as rs  # noqa: E402

VM = Path("/pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026/video_models")
MODELS = {"clip_2fps": ("CLIP (이미지)", None), "dinov2_2fps": ("DINOv2 (이미지)", None), "siglip2_2fps": ("SigLIP 2 (이미지)", None),
          "xclip": ("X-CLIP (영상-언어)", None), "vjepa2_win": ("V-JEPA 2 블록 40 (영상)", 2), "videomae_win": ("VideoMAE (영상)", 0),
          "timesformer": ("TimeSformer 층 12 (영상)", 11)}
ALPHAS = np.logspace(-1, 6, 15)


def load(d, layer):
    G = np.load(d / "global.npy").astype(np.float64)
    ids = pd.read_csv(d / "video_id.tsv", sep="\t").video_id.values
    return pd.DataFrame(G if layer is None else G[:, layer], index=ids)


def main():
    od = rs.OUT / "13_perturbation"; od.mkdir(parents=True, exist_ok=True)
    split = pd.read_csv(rs.bb.SPLIT, sep="\t")
    split = split[split.analysis_row & ~split.exclude_duplicate & (split.video_id <= 2185)].set_index("video_id")
    vids = split.index.values; fold = pd.Series(split.fold.values, index=vids)
    cats, Y, _ = rs.cl.labels_for(vids); Y = pd.DataFrame(Y, index=vids, columns=cats)
    summ, bycat = [], []
    for m, (lab, layer) in MODELS.items():
        if not (VM / m / "global.npy").exists():
            print(f"{m}: 원래 특징 없음, 건너뜀"); continue
        X = load(VM / m, layer).loc[vids]
        fits, P0 = {}, pd.DataFrame(index=vids, columns=cats, dtype=float)
        for f in sorted(fold.unique()):
            tr, te = fold.index[fold != f], fold.index[fold == f]
            mu, sd = X.loc[tr].mean(), X.loc[tr].std().replace(0, 1)
            fits[f] = (mu, sd, RidgeCV(alphas=ALPHAS).fit(((X.loc[tr] - mu) / sd).values, Y.loc[tr].values))
            P0.loc[te] = fits[f][2].predict(((X.loc[te] - mu) / sd).values)
        between_sd = P0.std()
        for d in sorted(VM.glob(f"{m}__*")):
            if not (d / "global.npy").exists():
                continue
            pert = d.name.split("__")[1]; Xp = load(d, layer); ids = [v for v in Xp.index if v in fold.index]
            Pp = pd.DataFrame(index=ids, columns=cats, dtype=float)
            for v in ids:
                mu, sd, r = fits[fold[v]]
                Pp.loc[v] = r.predict(((Xp.loc[[v]] - mu) / sd).values)[0]
            D = (Pp - P0.loc[ids]) / between_sd
            fr = np.mean([np.corrcoef(Xp.loc[v], X.loc[v])[0, 1] for v in ids])
            pr = np.mean([np.corrcoef(Pp.loc[v].astype(float), P0.loc[v].astype(float))[0, 1] for v in ids])
            summ.append(dict(model=lab, perturb=pert, n=len(ids), feature_r=fr, profile_r=pr, shift_sd=D.abs().mean().mean()))
            bycat += [dict(model=lab, perturb=pert, category=c, mean_shift_sd=D[c].mean(), sem=D[c].std() / np.sqrt(len(ids))) for c in cats]
            print(summ[-1], flush=True)
    pd.DataFrame(summ).to_csv(od / "summary.tsv", sep="\t", index=False, float_format="%.4f")
    pd.DataFrame(bycat).to_csv(od / "by_category.tsv", sep="\t", index=False, float_format="%.4f")


if __name__ == "__main__":
    main()
