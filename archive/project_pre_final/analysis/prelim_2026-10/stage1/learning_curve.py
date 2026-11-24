#!/usr/bin/env python3
"""학습 곡선: 학습 영상 수를 줄였을 때 뇌 → 정서 예측이 얼마나 떨어지나 (Horikawa, 2026-10-24).

목적: 한국인 fMRI 재현에서 영상을 몇 개 보여 줄지 정할 근거.
규칙
  - 평가(시험) 영상은 기준선과 같다: horikawa_rungroup6_v1 의 바깥 fold. 모든 학습량에서 같은 시험 영상을 쓴다.
  - 학습 영상은 바깥 학습 fold 들에서 run 째로 줄인다 (새 실험에서 "run 을 몇 개 찍나"와 같은 상황). run 하나 ≈ 영상 36개.
  - 한 반복 안에서 작은 학습량은 큰 학습량의 부분집합이다 (곡선이 우연으로 들쭉날쭉하지 않게).
  - 반복 4번 (run 순서를 바꾸는 seed 0~3). 'all' 은 학습 fold 전체 = 기준선과 같은 조건 (검산용, 1번만).
  - 모델·선택 절차는 기준선과 같다 (A34 soft BCE 선형, A14 ridge, 안쪽 = 남은 학습 영상의 바깥 fold 묶음).
  - 입력: 469개 영역 평균 (brain_roi469). 다른 입력의 곡선은 다를 수 있다 (특히 voxel 패턴).
  - 오차 감소율 두 가지. error_reduction 은 모든 학습량에서 같은 기준(바깥 학습 fold 전체의 평균 예측) 대비,
    error_reduction_subset_mean 은 그 학습량의 학습 영상 평균 예측 대비 (같은 라벨 예산으로 얻는 평균 예측과의 비교).
  - 이 곡선은 이 입력과 이 피험자의 학습 영상 수를 줄인 결과다. 새 촬영의 영상 수, 평정자 수, 개인 간 일반화를 정하지 않는다.
출력: stage1/05_learning_curve/lc_sub-XX.tsv (학습량 × 반복 × 차원별 r·오차 감소), lc_run_info_sub-XX.json, summary
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import brain_baseline as bb  # noqa: E402

OUT = Path("/storage/bigdata/EmoBrain_response/stage1/05_learning_curve")
SIZES = [150, 300, 600, 900, 1200, 1500]
REPEATS = 4
NOT_DISTINCT7 = bb.NOT_DISTINCT7
FALLBACK = []      # 안쪽 검증 묶음이 하나뿐이라 run 을 반씩 나눈 fit (학습량, 반복, fold, target 공간)


def run_subject(sub):
    t0 = time.time(); OUT.mkdir(parents=True, exist_ok=True)
    rows, fold, F, Y34, names, Y14, meta = bb.load_subject(sub)
    B = F["brain_roi469"]; run = rows.run_index.values; obs14 = np.isfinite(Y14).all(1)
    plans = [(n, r) for r in range(REPEATS) for n in SIZES] + [("all", 0)]
    preds = {p: {"A34": np.full(Y34.shape, np.nan), "A14": np.full(Y14.shape, np.nan),
                 "mu_A34": np.full(Y34.shape, np.nan), "mu_A14": np.full(Y14.shape, np.nan)} for p in plans}
    FALLBACK.clear(); bb.OPT_LOG.clear()
    n_actual = {p: [] for p in plans}
    for f in np.unique(fold):
        te = fold == f; pool_runs = np.unique(run[fold != f])
        for rep in range(REPEATS):
            order = np.random.RandomState(1000 * rep + int(f)).permutation(pool_runs)
            cum = np.cumsum([(run[fold != f] == r_).sum() for r_ in order])
            for n in SIZES:
                k = int(np.searchsorted(cum, n) + 1)          # n 개 이상이 되는 최소 run 수
                tr = np.isin(run, order[:k]) & (fold != f)
                n_actual[(n, rep)].append(int(tr.sum()))
                fit_one(B, Y34, Y14, obs14, fold, run, tr, te, preds[(n, rep)], tag=(n, rep, int(f)))
            print(f"  fold {f} 반복 {rep} 완료 ({time.time() - t0:.0f}초)", flush=True)
        tr = fold != f; n_actual[("all", 0)].append(int(tr.sum()))
        fit_one(B, Y34, Y14, obs14, fold, run, tr, te, preds[("all", 0)], tag=("all", 0, int(f)))
    out = []
    for (n, rep), P in preds.items():
        for space, Y, dims, mask in [("A34", Y34, names, np.ones(len(fold), bool)), ("A14", Y14, bb.DIMS14, obs14)]:
            for k, d in enumerate(dims):
                y, yh = Y[mask, k], P[space][mask, k]
                mu = np.array([Y[(fold != f) & mask, k].mean() for f in fold[mask]])   # 각 평가 영상의 (전체) 학습 fold 평균
                mu_sub = P["mu_" + space][mask, k]                                      # 이 학습량의 학습 영상 평균
                sse, sse0, sse_sub = ((y - yh) ** 2).sum(), ((y - mu) ** 2).sum(), ((y - mu_sub) ** 2).sum()
                out.append(dict(participant_id=f"sub-{sub}", n_train_target=str(n), n_train_actual=float(np.mean(n_actual[(n, rep)])),
                                repeat=rep, target_space=space, dimension=d,
                                distinct27=(space == "A34" and d not in NOT_DISTINCT7),
                                r_oof=bb.pearson(y, yh) if np.std(yh) > 0 else np.nan,
                                error_reduction=1 - sse / sse0 if sse0 > 0 else np.nan,
                                error_reduction_subset_mean=1 - sse / sse_sub if sse_sub > 0 else np.nan))
    df = pd.DataFrame(out); df.to_csv(OUT / f"lc_sub-{sub}.tsv", sep="\t", index=False, float_format="%.5f")
    info = dict(n_fits=len(plans) * len(np.unique(fold)) * 2, n_inner_fallback=len(FALLBACK),
                inner_fallback=[list(map(str, t)) for t in FALLBACK], softbce_convergence=bb.convergence_summary(),
                n_train_actual={f"{n}/{r}": v for (n, r), v in n_actual.items()})
    (OUT / f"lc_run_info_sub-{sub}.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))
    print(f"안쪽 묶음 fallback {len(FALLBACK)}회 / fit {info['n_fits']}회 | L-BFGS 수렴: {info['softbce_convergence']}")
    s = summarize_df(df); print(s.round(3).to_string(index=False)); print(f"sub-{sub} 완료 ({time.time() - t0:.0f}초)")


def fit_one(B, Y34, Y14, obs14, fold, run, tr, te, store, tag=None):
    for space, Y, mask in [("A34", Y34, np.ones(len(fold), bool)), ("A14", Y14, obs14)]:
        trm, tem = tr & mask, te & mask
        Xtr, Xte = bb.make_features("brain_roi469", {"brain_roi469": B}, trm, tem)
        groups = fold[trm]
        if len(np.unique(groups)) < 2:      # 안쪽 검증 묶음이 하나뿐이면 run 을 반씩 나눔 (run 을 쪼개지 않음)
            r_ = run[trm]; u = np.unique(r_)
            assert len(u) >= 2, f"학습 run 이 하나뿐: {tag}"
            groups = np.isin(r_, u[::2]).astype(int)
            FALLBACK.append((*tag, space))
        fitf = bb.fit_predict_a34 if space == "A34" else bb.fit_predict_a14
        P, _ = fitf(Xtr, Y[trm], Xte, groups)
        store[space][tem] = P
        store["mu_" + space][tem] = Y[trm].mean(0)


def summarize_df(df):
    rows = []
    for (pid, n, rep), g in df.groupby(["participant_id", "n_train_target", "repeat"], sort=False):
        for label, sel in [("A34 전체 34개", g.target_space == "A34"), ("A34 27개 (기술 요약)", g.distinct27), ("A14 척도 14개", g.target_space == "A14")]:
            rows.append(dict(participant_id=pid, n_train_target=n, repeat=rep, n_train_actual=g.n_train_actual.iloc[0],
                             묶음=label, r_mean=g[sel].r_oof.mean(), err_red_mean=g[sel].error_reduction.mean(),
                             err_red_subset_mean=g[sel].error_reduction_subset_mean.mean() if "error_reduction_subset_mean" in g else np.nan))
    return pd.DataFrame(rows)


def summarize():
    df = pd.concat([pd.read_csv(f, sep="\t", dtype={"n_train_target": str}) for f in sorted(OUT.glob("lc_sub-*.tsv"))])
    s = summarize_df(df)
    full = s[s.n_train_target == "all"].set_index(["participant_id", "묶음"]).r_mean
    s["전체대비_비율"] = [r / full.loc[(p, m)] for p, m, r in zip(s.participant_id, s.묶음, s.r_mean)]
    S = s.groupby(["묶음", "n_train_target"], sort=False).agg(학습영상수=("n_train_actual", "mean"), r_평균=("r_mean", "mean"),
                                                            r_최소=("r_mean", "min"), r_최대=("r_mean", "max"),
                                                            오차감소_전체평균기준=("err_red_mean", "mean"), 오차감소_subset평균기준=("err_red_subset_mean", "mean"),
                                                            전체대비_평균=("전체대비_비율", "mean"), 전체대비_최소=("전체대비_비율", "min")).reset_index()
    S.to_csv(OUT / "summary_learning_curve.tsv", sep="\t", index=False, float_format="%.4f")
    s.to_csv(OUT / "summary_by_subject_repeat.tsv", sep="\t", index=False, float_format="%.4f")
    pd.set_option("display.width", 200); print(S.round(3).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sub"); ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args()
    summarize() if a.summarize else run_subject(a.sub)
