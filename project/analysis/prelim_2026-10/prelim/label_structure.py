#!/usr/bin/env python3
"""EmoBrain 선행 점검 0-1~0-4, 0-9: 라벨 구조 (영상 단위 표만 사용, 2026-10-22).

대상 영상: Horikawa(주 데이터)의 분석 영상 2,181개 (같은 내용 중복의 나중 제시 15개 제외).
  0-1 34개 감정이 서로 얼마나 겹치나: 상관, 주성분 누적 설명, 유효 차원 수(participation ratio)
  0-2 34개와 14개 척도의 관계: 서로를 선형으로 얼마나 설명하나 (5겹 교차검증 R²)
  0-3 드문 감정: 감정별 평균, 0 이 아닌 영상 비율, 1위 영상 수, 0.3 이상 영상 수
  0-4 라벨 안정성: 영상별 평정자 수를 점수 분모로 추정 → 이항 잡음 대비 영상 간 분산 = 라벨 신뢰도
  0-9 영상 길이가 라벨을 얼마나 설명하나 (길이 구간 평균, 5겹 교차검증 R²)
출력: /storage/bigdata/EmoBrain_response/prelim/label_structure_*.tsv, label_structure_summary.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("/storage/bigdata/EmoBrain_response/prelim")
LAB = Path("/scratch/connectome/seokjin14/EmoBrain/project/shared/data")
META = Path("/storage/bigdata/Horikawa/metadata/horikawa_meta_data_with_dimension_binary.csv")
DIMS14 = ["valence", "arousal", "dominance", "approach", "attention", "certainty", "commitment", "control",
          "effort", "fairness", "identity", "obstruction", "safety", "upswing"]


def cv_r2(X, y, k=5, seed=0, ridge=1e-3):
    """선형 회귀(아주 약한 ridge) 5겹 교차검증 R²."""
    rng = np.random.RandomState(seed); idx = rng.permutation(len(y)); folds = np.array_split(idx, k)
    pred = np.zeros_like(y, dtype=float)
    for te in folds:
        tr = np.setdiff1d(idx, te)
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-12; A = (X[tr] - mu) / sd; ym = y[tr].mean()
        w = np.linalg.solve(A.T @ A + ridge * len(tr) * np.eye(A.shape[1]), A.T @ (y[tr] - ym))
        pred[te] = ((X[te] - mu) / sd) @ w + ym
    return 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def cv_r2_binned(x, y, bins=10, k=5, seed=0):
    """x 를 분위 구간으로 나눠 구간 평균으로 예측 (비선형 관계 포함), 5겹 교차검증 R²."""
    rng = np.random.RandomState(seed); idx = rng.permutation(len(y)); folds = np.array_split(idx, k)
    pred = np.zeros_like(y, dtype=float)
    for te in folds:
        tr = np.setdiff1d(idx, te)
        edges = np.unique(np.quantile(x[tr], np.linspace(0, 1, bins + 1)))
        btr = np.clip(np.searchsorted(edges, x[tr], side="right") - 1, 0, len(edges) - 2)
        bte = np.clip(np.searchsorted(edges, x[te], side="right") - 1, 0, len(edges) - 2)
        means = pd.Series(y[tr]).groupby(btr).mean()
        pred[te] = pd.Series(bte).map(means).fillna(y[tr].mean()).values
    return 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def infer_raters(p, nmax=80, tol=0.02):
    """한 영상의 34개 비율이 모두 k/n 꼴이 되는 가장 작은 n (평정자 수 추정)."""
    p = p[p > 0]
    for n in range(1, nmax + 1):
        if np.all(np.abs(p * n - np.round(p * n)) < tol * n / 10 + 1e-6):
            return n
    return np.nan


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = [l.strip() for l in open(LAB / "cowen34_order.txt") if l.strip()]
    D = pd.read_csv(META); D.index = D.stimulus_num.str.replace("stimulus_", "").astype(int)
    Y = D[[f"score_{i}" for i in range(34)]].copy(); Y.columns = names
    C = pd.read_csv(LAB / "cowen_horikawa_labels.csv"); C.index = C.stim_num_int
    Z = C[[f"{d}_score" for d in DIMS14]].copy(); Z.columns = DIMS14
    T = pd.read_csv("/storage/bigdata/Horikawa/response_t1w/sub-01/v3/sub-01_samples.tsv", sep="\t")
    T = T[~T.exclude_duplicate.astype(bool)].drop_duplicates("video_id")
    vids = T.video_id.values; dur = T.duration_sec.values.astype(float)
    Y = Y.loc[vids]; Zv = Z.reindex(vids)
    print(f"영상 {len(vids)}개 (14개 척도 있는 영상 {int(Zv.notna().all(1).sum())}개)")
    summ = {"영상수": int(len(vids))}

    # 0-1 감정끼리 겹침
    R = Y.corr(); R.to_csv(OUT / "label_structure_emotion_corr.tsv", sep="\t", float_format="%.3f")
    up = R.where(np.triu(np.ones(R.shape, bool), 1)).stack().sort_values()
    ev = np.linalg.eigvalsh(np.corrcoef(Y.values.T))[::-1]; ev = np.clip(ev, 0, None); cum = np.cumsum(ev) / ev.sum()
    pr = ev.sum() ** 2 / (ev ** 2).sum()
    summ["0-1"] = {"상관_양의_상위5": [f"{a}-{b}: {v:+.2f}" for (a, b), v in up.tail(5)[::-1].items()],
                   "상관_음의_상위5": [f"{a}-{b}: {v:+.2f}" for (a, b), v in up.head(5).items()],
                   "주성분_50/80/90%_필요개수": [int(np.searchsorted(cum, q) + 1) for q in (0.5, 0.8, 0.9)],
                   "유효차원수(participation_ratio)": round(float(pr), 1), "첫주성분_설명": round(float(cum[0]), 3)}
    # 0-2 34 ↔ 14
    ok = Zv.notna().all(1).values
    r2_14 = {d: cv_r2(Y.values[ok], Zv[d].values[ok]) for d in DIMS14}
    r2_34 = {e: cv_r2(Zv.values[ok], Y[e].values[ok]) for e in names}
    t02 = pd.DataFrame({"대상": list(r2_14) + list(r2_34), "종류": ["14개 척도 ← 34개 감정"] * 14 + ["34개 감정 ← 14개 척도"] * 34,
                        "교차검증_R2": list(r2_14.values()) + list(r2_34.values())})
    t02.to_csv(OUT / "label_structure_34_vs_14.tsv", sep="\t", index=False, float_format="%.3f")
    summ["0-2"] = {"14개 척도를 34개 감정으로 설명(R²)": {k: round(v, 2) for k, v in sorted(r2_14.items(), key=lambda x: -x[1])},
                   "34개 감정을 14개 척도로 설명(R²) 중앙값": round(float(np.median(list(r2_34.values()))), 2),
                   "34개 감정을 14개 척도로 설명(R²) 하위5": {k: round(v, 2) for k, v in sorted(r2_34.items(), key=lambda x: x[1])[:5]}}
    # 0-3 드문 감정
    top = Y.values == Y.values.max(1, keepdims=True)
    t03 = pd.DataFrame({"감정": names, "평균": Y.mean().values, "0아닌_영상비율": (Y > 0).mean().values,
                        "1위인_영상수": top.sum(0), "0.3이상_영상수": (Y >= 0.3).sum().values, "0.5이상_영상수": (Y >= 0.5).sum().values})
    t03 = t03.sort_values("평균", ascending=False)
    t03.to_csv(OUT / "label_structure_frequency.tsv", sep="\t", index=False, float_format="%.4f")
    rare = t03[(t03["1위인_영상수"] < 20) | (t03["0.3이상_영상수"] < 20)]
    summ["0-3"] = {"1위인_영상수_또는_0.3이상_영상수가_20개_미만": rare.감정.tolist()}
    # 0-4 라벨 안정성
    n_r = np.array([infer_raters(p) for p in Y.values])
    noise = (Y.values * (1 - Y.values)) / np.maximum(n_r[:, None] - 1, 1)
    rel = 1 - np.nanmean(noise, 0) / Y.var(0, ddof=1).values
    t04 = pd.DataFrame({"감정": names, "라벨신뢰도": rel, "예측상관_상한(√신뢰도)": np.sqrt(np.clip(rel, 0, 1))}).sort_values("라벨신뢰도", ascending=False)
    t04.to_csv(OUT / "label_structure_reliability.tsv", sep="\t", index=False, float_format="%.3f")
    summ["0-4"] = {"평정자수_추정_성공비율": round(float(np.isfinite(n_r).mean()), 3),
                   "평정자수_분위(최소/25/50/75/최대)": [float(np.nanpercentile(n_r, q)) for q in (0, 25, 50, 75, 100)],
                   "라벨신뢰도_중앙값": round(float(np.median(rel)), 2),
                   "신뢰도_상위5": {r.감정: round(r.라벨신뢰도, 2) for r in t04.head(5).itertuples()},
                   "신뢰도_하위5": {r.감정: round(r.라벨신뢰도, 2) for r in t04.tail(5).itertuples()}}
    # 0-9 영상 길이
    r2d = {f"감정:{e}": cv_r2_binned(dur, Y[e].values) for e in names}
    r2d.update({f"척도:{d}": cv_r2_binned(dur[ok], Zv[d].values[ok]) for d in DIMS14})
    t09 = pd.DataFrame({"라벨": list(r2d), "영상길이로_설명_R2": list(r2d.values())}).sort_values("영상길이로_설명_R2", ascending=False)
    t09.to_csv(OUT / "label_structure_duration_r2.tsv", sep="\t", index=False, float_format="%.4f")
    summ["0-9"] = {"영상길이_분위(최소/25/50/75/최대)": [float(np.percentile(dur, q)) for q in (0, 25, 50, 75, 100)],
                   "10초인_영상비율": round(float((dur == 10).mean()), 3),
                   "R2_상위8": {r.라벨: round(r.영상길이로_설명_R2, 3) for r in t09.head(8).itertuples()},
                   "R2_0.02넘는_라벨수": int((t09.영상길이로_설명_R2 > 0.02).sum())}
    (OUT / "label_structure_summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1))
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    pd.set_option("display.width", 200)
    print(t03.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
