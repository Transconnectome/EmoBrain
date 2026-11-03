#!/usr/bin/env python3
"""의미를 맞춘 영상 쌍에서, 정서 차이를 저수준 특징·층별 시각 특징의 차이가 설명하나 (2026-10-31, 자극 수준, 34개 감정).

질문: 시각이 정서에 작용할 때, 그것이 대상의 정체(무엇이 있나) 때문인지 생김새·움직임(어떻게 보이나) 때문인지.
방법
  1. 의미 공간: 정서·평가어 181개를 지운 사람 캡션 임베딩 (caption_human_noemo_mpnet). 영상마다 cosine 이 가장 큰 영상과 짝.
     겹치는 쌍은 하나로. 유사도가 가장 가까운 짝 유사도의 중앙값 이상인 쌍만 '의미가 같은 쌍' 으로 쓴다.
     비교 기준: 같은 수의 무작위 쌍.
  2. 쌍마다 정서 평정 차이 ΔY (34개) 와 특징 차이 ΔX. 특징은 열마다 전체 영상 기준으로 표준화.
  3. ΔX → ΔY ridge (절편 없음), 쌍 그래프의 연결 성분 단위 6겹 교차검증. 평가 쌍에서 R² = 1 − SSE / Σ ΔY² (예측 0 이 기준).
     의미가 같은 쌍에서 설명되는 정서 차이는 대상의 정체가 아니라 생김새·움직임 차이로 생긴 것으로 본다 (남은 의미 차이는
     ΔS 를 함께 넣은 모델과의 비교로 따로 확인).
특징 묶음: 저수준 (색 12 · 밝기와 선명도 6 · 움직임 10, build_lowlevel_motion.py; Sadeghi 142 정지 화면), V-JEPA 2 블록 8·16·24·32·40,
  CLIP 블록 6·12·18·24 (EmoViS 층별, 공간 평균), DINOv2, VideoMAE, 남은 의미 차이 ΔS (같은 캡션 임베딩).
출력: <OUT>/14_matched_pairs/{pairs.tsv, r2_by_emotion.tsv, r2_summary.tsv, examples.tsv}
사용: python semantic_matched_pairs.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import GroupKFold
from scipy.sparse.csgraph import connected_components
from scipy.sparse import coo_matrix

sys.path.insert(0, str(Path(__file__).parent))
import run_stage1 as rs  # noqa: E402

EMB = Path("/pscratch/sd/s/sjmoon/EmoViS/study1/results/00_embeddings")
ALPHAS = np.logspace(-1, 6, 15)
SEED = 20261031


def feature_sets(F, vids):
    L = F["lowlevel_motion"].loc[vids].values
    sad = np.load(EMB / "sadeghi/sadeghi_low_level.npy")[vids - 1]
    sets = {"저수준: 색": L[:, :12], "저수준: 밝기·선명도": L[:, 12:18], "저수준: 움직임": L[:, 18:28],
            "저수준: 전체 (+정지 화면 Gabor·대칭)": np.hstack([L, sad])}
    for b in (8, 16, 24, 32, 40):
        sets[f"V-JEPA 2 블록 {b}"] = np.load(EMB / f"vjepa2_layerwise/vjepa2_layer_{b:02d}.npy")[vids - 1]
    for b in (6, 12, 18, 24):
        sets[f"CLIP 블록 {b}"] = np.load(EMB / f"clip_layerwise/clip_layer_{b:02d}.npy")[vids - 1]
    sets["DINOv2"] = F["dinov2"].loc[vids].values
    sets["VideoMAE"] = F["videomae"].loc[vids].values
    sets["남은 의미 차이 (캡션)"] = F["caption_human_noemo_mpnet"].loc[vids].values
    out = {}
    for k, X in sets.items():
        X = np.asarray(X, np.float64); sd = X.std(0); out[k] = (X - X.mean(0)) / np.where(sd > 0, sd, 1)
    return out


def make_pairs(S, rng):
    n = len(S); M = S.copy(); np.fill_diagonal(M, -np.inf)
    nn = M.argmax(1); sim = M[np.arange(n), nn]
    pairs = {tuple(sorted((i, int(j)))) for i, j in enumerate(nn)}
    P = pd.DataFrame(sorted(pairs), columns=["i", "j"]); P["sim"] = S[P.i, P.j]
    matched = P[P.sim >= np.median(sim)].reset_index(drop=True)
    ri = rng.permutation(n)[: 2 * len(matched)]
    rand = pd.DataFrame(dict(i=ri[0::2], j=ri[1::2])); rand["sim"] = S[rand.i, rand.j]
    return matched, rand


def groups(P, n):
    A = coo_matrix((np.ones(len(P)), (P.i, P.j)), shape=(n, n))
    _, lab = connected_components(A, directed=False)
    return lab[P.i.values]


def cv_r2(dX, dY, g):
    pred = np.zeros_like(dY)
    for tr, te in GroupKFold(n_splits=6).split(dX, dY, g):
        pred[te] = RidgeCV(alphas=ALPHAS, fit_intercept=False).fit(dX[tr], dY[tr]).predict(dX[te])
    return 1 - ((dY - pred) ** 2).sum(0) / (dY ** 2).sum(0)


def main():
    od = rs.OUT / "14_matched_pairs"; od.mkdir(parents=True, exist_ok=True); rng = np.random.default_rng(SEED)
    split = pd.read_csv(rs.bb.SPLIT, sep="\t")
    split = split[split.analysis_row & ~split.exclude_duplicate & (split.video_id <= 2185)]
    vids = split.video_id.values; F = rs.load_features()
    cats, Y, _ = rs.cl.labels_for(vids)
    sem = F["caption_human_noemo_mpnet"].loc[vids].values.astype(np.float64)
    sem /= np.linalg.norm(sem, axis=1, keepdims=True); S = sem @ sem.T
    matched, rand = make_pairs(S, rng)
    sets = feature_sets(F, vids)
    cap = pd.read_csv("/pscratch/sd/s/sjmoon/transfer/emobrain_stimulus_features_20261025/captions/caption_ck20.csv", encoding="utf-8-sig")
    first = cap.groupby("video_id").description.first()
    pd.concat([matched.assign(kind="matched"), rand.assign(kind="random")]).assign(
        video_i=lambda d: vids[d.i], video_j=lambda d: vids[d.j]).to_csv(od / "pairs.tsv", sep="\t", index=False, float_format="%.4f")
    print(f"의미가 같은 쌍 {len(matched)}개 (유사도 {matched.sim.min():.2f}~{matched.sim.max():.2f}, 중앙값 {matched.sim.median():.2f}), "
          f"무작위 쌍 {len(rand)}개 (유사도 중앙값 {rand.sim.median():.2f})", flush=True)
    rows = []
    for kind, P in [("matched", matched), ("random", rand)]:
        g = groups(P, len(vids)); dY = Y[P.i] - Y[P.j]
        flip = rng.choice([-1, 1], len(P))[:, None]; dY = dY * flip
        for name, X in sets.items():
            dX = (X[P.i] - X[P.j]) * flip
            r2 = cv_r2(dX, dY, g)
            rows += [dict(pairs=kind, features=name, category=c, r2=r2[k]) for k, c in enumerate(cats)]
            print(kind, name, f"평균 R² {r2.mean():.3f}", flush=True)
        if kind == "matched":
            dS = (sets["남은 의미 차이 (캡션)"][P.i] - sets["남은 의미 차이 (캡션)"][P.j]) * flip
            for name in ["저수준: 전체 (+정지 화면 Gabor·대칭)", "V-JEPA 2 블록 8", "V-JEPA 2 블록 40", "CLIP 블록 6", "CLIP 블록 24", "DINOv2"]:
                dX = np.hstack([dS, (sets[name][P.i] - sets[name][P.j]) * flip])
                r2 = cv_r2(dX, dY, g)
                rows += [dict(pairs=kind, features=f"남은 의미 + {name}", category=c, r2=r2[k]) for k, c in enumerate(cats)]
                print(kind, f"남은 의미 + {name}", f"평균 R² {r2.mean():.3f}", flush=True)
            ex = []
            for c in ["disgust", "craving", "adoration", "fear", "horror", "amusement", "aesthetic appreciation", "sadness"]:
                k = cats.index(c); d = np.abs(Y[P.i, k] - Y[P.j, k]); top = np.argsort(-d)[:3]
                ex += [dict(category=c, video_i=vids[P.i[t]], video_j=vids[P.j[t]], rating_i=Y[P.i[t], k], rating_j=Y[P.j[t], k],
                            sim=P.sim[t], caption_i=first.get(vids[P.i[t]], ""), caption_j=first.get(vids[P.j[t]], "")) for t in top]
            pd.DataFrame(ex).to_csv(od / "examples.tsv", sep="\t", index=False, float_format="%.3f")
    R = pd.DataFrame(rows); R.to_csv(od / "r2_by_emotion.tsv", sep="\t", index=False, float_format="%.4f")
    summ = R.groupby(["pairs", "features"], sort=False).r2.mean().unstack(0)
    summ.to_csv(od / "r2_summary.tsv", sep="\t", float_format="%.4f"); print(summ.round(3).to_string())


if __name__ == "__main__":
    main()
