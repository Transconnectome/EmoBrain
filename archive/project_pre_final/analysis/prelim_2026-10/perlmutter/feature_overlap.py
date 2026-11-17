#!/usr/bin/env python3
"""시각 특징과 캡션 특징이 얼마나 겹치는가 (2026-10-30, 자극 수준, 뇌 없음).

대상: 분할 표 horikawa_rungroup6_v1 의 분석 행 (같은 내용 중복 제외). fold 는 같은 분할 표를 쓴다.
특징: 영상 V-JEPA 2, VideoMAE / 이미지 CLIP, DINOv2, Horikawa VGG19 fc8 / 의미 사람 캡션(mpnet), Horikawa 의미 73, VLM 캡션(v1, 점검에서 핵심 사건 오류 29%)

1. 표상 유사도 (대칭)
   linear CKA : 열을 표준화한 두 특징 행렬의 CKA. 영상 순서를 섞은 null 20회 평균을 같이 낸다 (차원이 높으면 기본값이 0보다 크다)
   RSA        : 영상 쌍마다 1 − Pearson 거리로 만든 RDM 두 개의 Spearman 상관
2. 서로 예측 (비대칭) : 학습 fold 로 표준화·RidgeCV(GCV) 를 맞추고 평가 fold 예측. 대상 특징 전체 분산 중 설명된 비율 (분산 가중 R²)
3. 정서 예측에서 겹치는 정보 : 34개 범주 비율을 시각만, 의미만, 둘 다(안쪽 OOF 예측을 범주마다 선형 결합하는 stacking) 로 예측.
   단독도 같은 보정(안쪽 OOF 예측에 범주별 선형 회귀)을 거친 R² (학습 fold 평균 대비) 를 쓴다.
   시각에만 있는 정보 = R²(둘) − R²(의미), 의미에만 있는 정보 = R²(둘) − R²(시각), 둘 다 가진 정보 = R²(시각) + R²(의미) − R²(둘)
   --partition-only : 3번만 다시 계산
출력: <OUT>/12_feature_overlap/{cka.tsv, rsa.tsv, cross_prediction.tsv, emotion_partition.tsv, emotion_partition_by_category.tsv}
사용: python feature_overlap.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.linear_model import LinearRegression, RidgeCV

sys.path.insert(0, str(Path(__file__).parent))
import run_stage1 as rs  # noqa: E402

VISUAL = ["vjepa2_vitg_final", "videomae", "clip_vitl14", "dinov2", "hk_vision1000"]
SEMANTIC = ["caption_human_mpnet", "hk_semantic73", "caption_vlm_mpnet"]
LABEL = {"vjepa2_vitg_final": "V-JEPA 2 (영상)", "videomae": "VideoMAE (영상)", "clip_vitl14": "CLIP (이미지)",
         "dinov2": "DINOv2 (이미지)", "hk_vision1000": "VGG19 fc8 (이미지)", "caption_human_mpnet": "사람 캡션",
         "hk_semantic73": "의미 73 (사람 개념)", "caption_vlm_mpnet": "VLM 캡션 v1"}
ALPHAS = np.logspace(-1, 6, 15)
N_NULL, SEED = 20, 0


def zscore(X):
    X = X - X.mean(0); s = X.std(0); return X / np.where(s > 0, s, 1)


def cka(X, Y):
    return np.linalg.norm(X.T @ Y) ** 2 / (np.linalg.norm(X.T @ X) * np.linalg.norm(Y.T @ Y))


def rdm_ranks(X):
    C = np.corrcoef(X); iu = np.triu_indices(len(X), 1)
    return rankdata(1 - C[iu])


def ridge_oof(X, Y, fold):
    P = np.zeros_like(Y, dtype=np.float64); base = np.zeros_like(Y, dtype=np.float64)
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        mx, sx = X[tr].mean(0), X[tr].std(0); sx = np.where(sx > 0, sx, 1)
        m = RidgeCV(alphas=ALPHAS).fit((X[tr] - mx) / sx, Y[tr])
        P[te] = m.predict((X[te] - mx) / sx); base[te] = Y[tr].mean(0)
    return P, base


def r2(Y, P, base):
    return 1 - ((Y - P) ** 2).sum(0) / ((Y - base) ** 2).sum(0)


def fit_predict(Xtr, Ytr, Xte):
    mx, sx = Xtr.mean(0), Xtr.std(0); sx = np.where(sx > 0, sx, 1)
    return RidgeCV(alphas=ALPHAS).fit((Xtr - mx) / sx, Ytr).predict((Xte - mx) / sx)


def stack_parts(X, Y, fold):
    """바깥 fold 마다 (안쪽 OOF 예측, 바깥 학습 전체로 맞춘 평가 fold 예측). 특징 쌍마다 다시 맞추지 않게 미리 계산."""
    out = {}
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        out[f] = (ridge_oof(X[tr], Y[tr], fold[tr])[0], fit_predict(X[tr], Y[tr], X[te]))
    return out


def stacked_one(p, Y, fold):
    """단독 특징도 stacking 과 같은 보정(안쪽 OOF 예측에 범주별 선형 회귀)을 거친다. 결합 이득에서 보정 효과를 빼기 위함."""
    P = np.zeros_like(Y)
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        p_in, p_out = p[f]
        for d in range(Y.shape[1]):
            P[te, d] = LinearRegression().fit(p_in[:, [d]], Y[tr, d]).predict(p_out[:, [d]])
    return P


def stacked(pv, ps, Y, fold):
    """안쪽 OOF 로 범주마다 두 예측의 선형 결합을 맞추고 평가 fold 예측에 적용 (stacking)."""
    P = np.zeros_like(Y)
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        (v_in, v_out), (s_in, s_out) = pv[f], ps[f]
        for d in range(Y.shape[1]):
            lr = LinearRegression().fit(np.c_[v_in[:, d], s_in[:, d]], Y[tr, d])
            P[te, d] = lr.predict(np.c_[v_out[:, d], s_out[:, d]])
    return P


def partition(vids, fold, X, names, od):
    cats, Y, _ = rs.cl.labels_for(vids); rows, bycat = [], []
    base = np.zeros_like(Y)
    for f in np.unique(fold):
        base[fold == f] = Y[fold != f].mean(0)
    parts = {n: stack_parts(X[n], Y, fold) for n in names}
    single = {n: r2(Y, stacked_one(parts[n], Y, fold), base) for n in names}
    for s in SEMANTIC:
        for v in VISUAL:
            rv, rsem, rb = single[v], single[s], r2(Y, stacked(parts[v], parts[s], Y, fold), base)
            rows.append(dict(semantic=LABEL[s], visual=LABEL[v], r2_visual=rv.mean(), r2_semantic=rsem.mean(), r2_both=rb.mean(),
                             unique_visual=(rb - rsem).mean(), unique_semantic=(rb - rv).mean(), shared=(rv + rsem - rb).mean()))
            bycat += [dict(semantic=LABEL[s], visual=LABEL[v], category=c, r2_visual=rv[k], r2_semantic=rsem[k], r2_both=rb[k])
                      for k, c in enumerate(cats)]
            print(rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(od / "emotion_partition.tsv", sep="\t", index=False, float_format="%.4f")
    pd.DataFrame(bycat).to_csv(od / "emotion_partition_by_category.tsv", sep="\t", index=False, float_format="%.4f")
    print("정서 분할 완료", flush=True)


def main():
    split = pd.read_csv(rs.bb.SPLIT, sep="\t")
    split = split[split.analysis_row & ~split.exclude_duplicate].set_index("video_id")
    vids = split.index.values; fold = split.fold.values
    F = rs.load_features(); names = VISUAL + SEMANTIC
    X = {n: F[n].loc[vids].values.astype(np.float64) for n in names}
    od = rs.OUT / "12_feature_overlap"; od.mkdir(parents=True, exist_ok=True)
    print(f"영상 {len(vids)}개, fold {np.bincount(fold)}", flush=True)

    if "--partition-only" in sys.argv:
        return partition(vids, fold, X, names, od)
    Z = {n: zscore(X[n]) for n in names}; rng = np.random.default_rng(SEED)
    rows = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            null = np.mean([cka(Z[a], Z[b][rng.permutation(len(vids))]) for _ in range(N_NULL)])
            rows.append(dict(a=LABEL[a], b=LABEL[b], cka=cka(Z[a], Z[b]), cka_null=null))
    pd.DataFrame(rows).to_csv(od / "cka.tsv", sep="\t", index=False, float_format="%.4f"); print("CKA 완료", flush=True)

    R = {n: rdm_ranks(Z[n]) for n in names}; rows = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            rows.append(dict(a=LABEL[a], b=LABEL[b], rsa_spearman=np.corrcoef(R[a], R[b])[0, 1]))
    pd.DataFrame(rows).to_csv(od / "rsa.tsv", sep="\t", index=False, float_format="%.4f"); del R; print("RSA 완료", flush=True)

    rows = []
    for a in names:
        for b in names:
            if a == b:
                continue
            P, base = ridge_oof(X[a], X[b], fold)
            sse = ((X[b] - P) ** 2).sum(); sst = ((X[b] - base) ** 2).sum()
            rows.append(dict(source=LABEL[a], target=LABEL[b], explained_variance=1 - sse / sst))
    pd.DataFrame(rows).to_csv(od / "cross_prediction.tsv", sep="\t", index=False, float_format="%.4f"); print("서로 예측 완료", flush=True)

    partition(vids, fold, X, names, od)
    print("완료", flush=True)


if __name__ == "__main__":
    main()
