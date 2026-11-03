#!/usr/bin/env python3
"""같은 대상(맥락) 안에서 저수준 특징이 정서를 가르나 (2026-10-31, 자극 수준).

semantic_matched_pairs.py 는 모든 맥락에 하나의 선형 규칙을 맞춰서, 맥락마다 방향이 반대인 저수준 효과는 상쇄되고 일부 맥락에만 있는 효과는 묻힌다.
여기서는 맥락마다 따로 맞춘다.
맥락: Horikawa 의미 73 개념 중 해당 묶음의 최댓값 ≥ 0.5 (평정자 절반 이상이 체크) 인 영상.
모델 (맥락 안 10겹 교차검증, ridge, 예측과 실제의 Pearson r)
  저수준        : build_lowlevel_motion.py 28개 (색 12, 밝기·선명도 6, 움직임 10)
  캡션          : 정서·평가어를 지운 사람 캡션 임베딩 (caption_human_noemo_mpnet)
  캡션 뒤 저수준 : 캡션 예측 (OOF) 을 뺀 나머지 정서를 저수준으로 예측
  CLIP, V-JEPA 2 : 참고 (clip_vitl14, vjepa2_vitg_final)
유의성: 저수준·캡션 뒤 저수준은 맥락 안에서 정서를 섞은 null 200회의 오른쪽 꼬리 비율.
특징 상관: 맥락마다 저수준 특징 각각과 정서의 Pearson r (부호가 맥락마다 바뀌는지 보려는 것).
출력: <OUT>/15_within_context/{model_r.tsv, feature_corr.tsv}
사용: python within_context_lowlevel.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold

sys.path.insert(0, str(Path(__file__).parent))
import run_stage1 as rs  # noqa: E402

CONTEXTS = {
    "음식": (["Food"], ["craving", "disgust", "satisfaction", "amusement"]),
    "동물": (["Aquatic animals", "Birds", "Cats", "Dogs", "Insects", "Land animals", "Large animals", "Small animals"],
             ["adoration", "disgust", "fear", "amusement"]),
    "피·상처·배설물": (["Blood", "Injuries", "Dead bodies", "Feces/urine/vomit"], ["disgust", "horror", "empathic pain", "fear"]),
    "자연·풍경": (["Nature", "Vast landscapes", "Mountains", "Clouds", "Plants", "Snow", "Underwater scenes"],
                ["awe", "aesthetic appreciation", "calmness", "fear"]),
    "노출·성": (["Naked people", "Sexual activity", "Genitalia"], ["sexual desire", "disgust", "amusement", "romance"]),
    "아기": (["Babies"], ["adoration", "amusement", "joy", "empathic pain"]),
    "스포츠·묘기": (["Sports", "Stunts"], ["excitement", "fear", "amusement", "awe"]),
    "탈것": (["Automobiles", "Planes", "Boats", "Roads"], ["fear", "excitement", "horror", "awe"]),
}
ALPHAS = np.logspace(-2, 5, 15)
N_PERM, SEED = 200, 20261031


def zs(X):
    sd = X.std(0); return (X - X.mean(0)) / np.where(sd > 0, sd, 1)


def oof(X, y, seed=0):
    p = np.zeros_like(y)
    for tr, te in KFold(10, shuffle=True, random_state=seed).split(X):
        p[te] = RidgeCV(alphas=ALPHAS).fit(X[tr], y[tr]).predict(X[te])
    return p


def r(a, b):
    return np.corrcoef(a, b)[0, 1] if a.std() > 0 and b.std() > 0 else np.nan


def main():
    od = rs.OUT / "15_within_context"; od.mkdir(parents=True, exist_ok=True); rng = np.random.default_rng(SEED)
    split = pd.read_csv(rs.bb.SPLIT, sep="\t")
    split = split[split.analysis_row & ~split.exclude_duplicate & (split.video_id <= 2185)]
    vids = split.video_id.values; F = rs.load_features()
    cats, Y, _ = rs.cl.labels_for(vids); Yd = pd.DataFrame(Y, index=vids, columns=cats)
    C = F["hk_semantic73"].loc[vids]
    cols = (Path(rs.FEAT_DIR) / "lowlevel_motion_columns.txt").read_text().split()
    LL = F["lowlevel_motion"].loc[vids]; LL.columns = cols
    CAP = F["caption_human_noemo_mpnet"].loc[vids]; CLIP = F["clip_vitl14"].loc[vids]; VJ = F["vjepa2_vitg_final"].loc[vids]
    rows, corr = [], []
    for ctx, (concepts, emos) in CONTEXTS.items():
        m = (C[concepts].max(axis=1) >= 0.5).values; ids = vids[m]
        Xl, Xc = zs(LL.values[m].astype(float)), zs(CAP.values[m].astype(float))
        Xclip, Xvj = zs(CLIP.values[m].astype(float)), zs(VJ.values[m].astype(float))
        for e in emos:
            y = Yd.loc[ids, e].values.astype(float)
            if (y > 0).sum() < 10:
                continue
            p_cap = oof(Xc, y); resid = y - p_cap
            res = dict(context=ctx, n=len(ids), emotion=e, mean_rating=y.mean(),
                       r_lowlevel=r(oof(Xl, y), y), r_caption=r(p_cap, y), r_lowlevel_after_caption=r(oof(Xl, resid), resid),
                       r_clip=r(oof(Xclip, y), y), r_vjepa2=r(oof(Xvj, y), y))
            nl, nr = [], []
            for k in range(N_PERM):
                yp = rng.permutation(y); rp = rng.permutation(resid)
                nl.append(r(oof(Xl, yp, seed=k + 1), yp)); nr.append(r(oof(Xl, rp, seed=k + 1), rp))
            res["p_lowlevel"] = (np.sum(np.array(nl) >= res["r_lowlevel"]) + 1) / (N_PERM + 1)
            res["p_lowlevel_after_caption"] = (np.sum(np.array(nr) >= res["r_lowlevel_after_caption"]) + 1) / (N_PERM + 1)
            rows.append(res); print(res, flush=True)
            corr += [dict(context=ctx, emotion=e, feature=c, r=r(LL.loc[ids, c].values.astype(float), y)) for c in cols]
    pd.DataFrame(rows).to_csv(od / "model_r.tsv", sep="\t", index=False, float_format="%.4f")
    pd.DataFrame(corr).to_csv(od / "feature_corr.tsv", sep="\t", index=False, float_format="%.4f")


if __name__ == "__main__":
    main()
