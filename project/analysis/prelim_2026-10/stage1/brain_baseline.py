#!/usr/bin/env python3
"""EmoBrain 1단계 핵심 3: 현재 전처리(Horikawa v3_qc)의 뇌 단독 정서 기준선 (2026-10-24).

task 계약: stage1/01_task/task_contract.yaml (요약)
  - 관찰 단위: 피험자 1명 × 영상 1개의 블록 반응. 분석 행 = QC 통과 + 같은 내용 중복의 나중 제시 제외
  - 일반화: 같은 피험자가 처음 보는 영상. 분할 horikawa_rungroup6_v1 (run 묶음 6겹, 5명 공통), 안쪽 = 바깥 학습 fold 5개
  - 피험자별 모델. 결과는 피험자별로 보존 (다른 사람 예측을 이어 붙이지 않음)
  - A34: 34개 범주 응답 비율 [0,1], 합 강제 없음. 감정마다 독립인 L2 정규화 선형 sigmoid 출력 + soft BCE
  - A14: 14개 척도(1~9 평균, 관측된 영상만). 척도마다 ridge (target 은 train 평균·표준편차로 변환 후 되돌림)
  - 규제 강도: 차원마다 안쪽 검증 손실(A34 soft BCE, A14 MSE)로 선택. 평가 지표로 고르지 않음
입력 조건 (모두 같은 평가 영상, 같은 모델 계열·선택 절차)
  train_mean   : 학습 영상의 차원별 평균 (모델 없음)
  duration     : 영상 길이 구간 (학습 영상 분위수로 정한 구간의 원-핫)
  lowlevel_L   : 저수준 시각 특징 33개 (prelim/lowlevel_video_features.tsv)
  brain_global : 블록의 voxel 전체 평균·표준편차·log 표준편차 (prelim/block_stats, voxel 원자료에서 계산)
  brain_roi469 : 기본 지도 469개 영역 평균 반응 (prelim/roi_blocks, run 안 z 의 영역 평균). 유효하지 않은 영역 제외
출력 (stage1/02_brain/): predictions/sub-XX.tsv.gz (긴 형식 원예측), dimension_metrics_sub-XX.tsv,
      profile_metrics_sub-XX.tsv, selected_lambda_sub-XX.tsv, run_info_sub-XX.json
사용: python brain_baseline.py --sub 01 | --self-test
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

OUT = Path("/storage/bigdata/EmoBrain_response/stage1/02_brain")
PRE = Path("/storage/bigdata/EmoBrain_response/prelim")
SPLIT = Path("/storage/bigdata/EmoBrain_response/splits/horikawa_rungroup6_v1.tsv")
LAB = Path("/scratch/connectome/seokjin14/EmoBrain/project/shared/data")
META = Path("/storage/bigdata/Horikawa/metadata/horikawa_meta_data_with_dimension_binary.csv")
DIMS14 = ["valence", "arousal", "dominance", "approach", "attention", "certainty", "commitment", "control",
          "effort", "fairness", "identity", "obstruction", "safety", "upswing"]
LAM_BCE = np.logspace(1, -3, 9)         # soft BCE: (1/n)ΣBCE + (λ/2)||w||², 큰 값부터 (warm start). 1e-4 는 사실상 규제 없음이라 뺌
ALPHA_RIDGE = np.logspace(-1, 6, 15)     # ridge: ||y - Xw||² + α||w||² (표준화한 X, y)
NOT_DISTINCT7 = ["pride", "triumph", "contempt", "disappointment", "sympathy", "guilt", "envy"]   # Cowen & Keltner 2017. 27개 요약은 제안 상태
CONDITIONS = ["train_mean", "duration", "lowlevel_L", "brain_global", "brain_roi469"]
OPT_LOG = []                             # L-BFGS 결과 기록 (λ, 성공 여부, 반복 수, 종료 코드). run_info 에 요약
VERSIONS = dict(split_id="horikawa_rungroup6_v1",
                preprocessing_version="Horikawa v3_qc (common36, fieldmap 없는 보정, QC D22)",
                target_version="A34=horikawa_meta_data_with_dimension_binary.csv score_0-33 (cowen34_order.txt); "
                               "A14=cowen_horikawa_labels.csv *_score")


# ---------- 모델 ----------
def fit_softbce_path(X, Y, lams, W0=None):
    """34개 출력을 한 번에 최적화 (손실·규제가 출력별로 분리되므로 출력별 독립 모델과 같다). λ 경로를 큰 값부터."""
    n, p = X.shape; k = Y.shape[1]
    Xa = np.hstack([X, np.ones((n, 1))])
    theta = np.zeros((p + 1, k)) if W0 is None else W0.copy()
    if W0 is None:
        m = np.clip(Y.mean(0), 1e-4, 1 - 1e-4); theta[-1] = np.log(m / (1 - m))
    path = []
    for lam in lams:
        def f(t):
            T = t.reshape(p + 1, k); Z = Xa @ T
            loss = (np.logaddexp(0, Z) - Y * Z).sum() / n + 0.5 * lam * (T[:-1] ** 2).sum()
            G = Xa.T @ (expit(Z) - Y) / n; G[:-1] += lam * T[:-1]
            return loss, G.ravel()
        res = minimize(f, theta.ravel(), jac=True, method="L-BFGS-B", options=dict(maxiter=500, gtol=1e-6))
        OPT_LOG.append((float(lam), bool(res.success), int(res.nit), int(res.status), str(res.message)))
        theta = res.x.reshape(p + 1, k); path.append(theta.copy())
    return path


def convergence_summary():
    """지금까지의 L-BFGS fit 수렴 요약. status 1 = 반복 한도(500) 도달, 2 = 그 밖의 중단."""
    if not OPT_LOG:
        return dict(n_fits=0)
    bad = [r for r in OPT_LOG if not r[1]]
    msgs = sorted({r[4] for r in bad})
    return dict(n_fits=len(OPT_LOG), n_not_converged=len(bad),
                n_hit_maxiter=sum(r[3] == 1 for r in bad), max_nit=max(r[2] for r in OPT_LOG),
                not_converged_lambdas=sorted({r[0] for r in bad}), messages=msgs[:5])


def predict_softbce(X, theta):
    return expit(np.hstack([X, np.ones((len(X), 1))]) @ theta)


def softbce(Y, P):
    P = np.clip(P, 1e-7, 1 - 1e-7)
    return -(Y * np.log(P) + (1 - Y) * np.log(1 - P))


def ridge_path(X, Y, alphas):
    """표준화된 X, Y 에서 α 별 계수 (SVD)."""
    U, s, Vt = np.linalg.svd(X, full_matrices=False); UtY = U.T @ Y
    return [Vt.T @ ((s / (s ** 2 + a))[:, None] * UtY) for a in alphas]


# ---------- 입력 조건별 특징 (학습 영상에서만 변환을 정함) ----------
def make_features(cond, F, tr, te):
    if cond == "duration":
        d = F["duration"][:, 0]
        edges = np.unique(np.quantile(d[tr], np.linspace(0, 1, 11)))
        def onehot(x):
            b = np.clip(np.searchsorted(edges, x, side="right") - 1, 0, max(len(edges) - 2, 0))
            return np.eye(max(len(edges) - 1, 1))[b]
        return onehot(d[tr]), onehot(d[te])
    X = F[cond]; mu = X[tr].mean(0); sd = X[tr].std(0); sd[sd == 0] = 1
    return (X[tr] - mu) / sd, (X[te] - mu) / sd


def fit_predict_a34(Xtr, Ytr, Xte, inner_groups):
    """안쪽 fold 별로 λ 경로를 fit → 차원별 안쪽 검증 soft BCE 로 λ 선택 → 바깥 학습 전체로 다시 fit."""
    loss = np.zeros((len(LAM_BCE), Ytr.shape[1]))
    for g in np.unique(inner_groups):
        a, b = inner_groups != g, inner_groups == g
        mu, sd = Xtr[a].mean(0), Xtr[a].std(0); sd[sd == 0] = 1
        path = fit_softbce_path((Xtr[a] - mu) / sd, Ytr[a], LAM_BCE)
        for j, th in enumerate(path):
            loss[j] += softbce(Ytr[b], predict_softbce((Xtr[b] - mu) / sd, th)).sum(0)
    best = loss.argmin(0)
    path = fit_softbce_path(Xtr, Ytr, LAM_BCE)
    P = np.column_stack([predict_softbce(Xte, path[best[k]])[:, k] for k in range(Ytr.shape[1])])
    return P, LAM_BCE[best]


def fit_predict_a14(Xtr, Ytr, Xte, inner_groups):
    ym, ys = Ytr.mean(0), Ytr.std(0); ys[ys == 0] = 1
    Z = (Ytr - ym) / ys
    err = np.zeros((len(ALPHA_RIDGE), Ytr.shape[1]))
    for g in np.unique(inner_groups):
        a, b = inner_groups != g, inner_groups == g
        mu, sd = Xtr[a].mean(0), Xtr[a].std(0); sd[sd == 0] = 1
        zm = Z[a].mean(0)
        for j, W in enumerate(ridge_path((Xtr[a] - mu) / sd, Z[a] - zm, ALPHA_RIDGE)):
            err[j] += (((Xtr[b] - mu) / sd @ W + zm - Z[b]) ** 2).sum(0)
    best = err.argmin(0); zm = Z.mean(0)
    Ws = ridge_path(Xtr, Z - zm, ALPHA_RIDGE)
    P = np.column_stack([(Xte @ Ws[best[k]])[:, k] + zm[k] for k in range(Ytr.shape[1])])
    return P * ys + ym, ALPHA_RIDGE[best]


# ---------- 평가 ----------
def pearson(a, b):
    a = a - a.mean(); b = b - b.mean(); d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else np.nan


def evaluate(pred, sub):
    """같은 원예측에서 차원별 r·오차와 영상별 프로필 상관을 계산."""
    dim_rows, prof_rows = [], []
    for (cond, space, dim), g in pred.groupby(["input_condition", "target_space", "dimension"], sort=False):
        y, yh, mu = g.y_true.values, g.y_pred.values, g.train_mean.values
        r = pearson(y, yh) if np.std(yh) > 0 and np.std(y) > 0 else np.nan
        fr = [pearson(f.y_true.values, f.y_pred.values) for _, f in g.groupby("outer_fold")
              if np.std(f.y_pred.values) > 0 and np.std(f.y_true.values) > 0]
        sse, sse0 = ((y - yh) ** 2).sum(), ((y - mu) ** 2).sum()
        row = dict(participant_id=f"sub-{sub}", input_condition=cond, target_space=space, dimension=dim,
                   n_eval=len(g), n_nonzero=int((y > 0).sum()) if space == "A34" else np.nan,
                   r_oof=r, r_fold_mean=float(np.mean(fr)) if fr else np.nan, n_folds_r=len(fr),
                   mse=sse / len(g), mse_train_mean=sse0 / len(g),
                   error_reduction=1 - sse / sse0 if sse0 > 0 else np.nan,
                   soft_bce=float(softbce(y, yh).mean()) if space == "A34" else np.nan,
                   status="ok" if np.isfinite(r) else "na", na_reason="" if np.isfinite(r) else "예측 또는 실제값이 상수")
        dim_rows.append(row)
    for (cond, space), g in pred.groupby(["input_condition", "target_space"], sort=False):
        W = g.pivot_table(index="video_id", columns="dimension", values=["y_true", "y_pred", "train_mean"])
        Yt, Yp, Ym = W["y_true"].values, W["y_pred"].values, W["train_mean"].values
        rs = np.array([pearson(Yt[i], Yp[i]) if np.std(Yp[i]) > 0 and np.std(Yt[i]) > 0 else np.nan for i in range(len(Yt))])
        rm = np.array([pearson(Yt[i], Ym[i]) if np.std(Ym[i]) > 0 and np.std(Yt[i]) > 0 else np.nan for i in range(len(Yt))])
        prof_rows.append(dict(participant_id=f"sub-{sub}", input_condition=cond, target_space=space, n_videos=len(rs),
                              n_valid=int(np.isfinite(rs).sum()), profile_r_mean=float(np.nanmean(rs)),
                              profile_r_median=float(np.nanmedian(rs)),
                              train_mean_profile_r_mean=float(np.nanmean(rm)),
                              gain_over_mean_profile=float(np.nanmean(rs - rm))))
    return pd.DataFrame(dim_rows), pd.DataFrame(prof_rows)


# ---------- 자료 ----------
def load_subject(sub):
    rows = pd.read_csv(PRE / f"roi_blocks/Horikawa_sub-{sub}_roi469_rows.tsv", sep="\t")
    R = np.load(PRE / f"roi_blocks/Horikawa_sub-{sub}_roi469_runz.npy")
    info = pd.read_csv(PRE / f"roi_blocks/Horikawa_sub-{sub}_roi469_info.tsv", sep="\t")
    assert len(rows) == len(R)
    split = pd.read_csv(SPLIT, sep="\t").set_index("video_id")
    keep = ~rows.exclude_duplicate.astype(bool).values
    rows = rows[keep].reset_index(drop=True); R = R[keep]
    assert (split.loc[rows.video_id, "run_index"].values == rows.run_index.values).all(), "분할 표와 run_index 불일치"
    fold = split.loc[rows.video_id, "fold"].values
    valid = info.roi_valid.values & np.isfinite(R).all(0)
    bs = pd.read_csv(PRE / f"block_stats_Horikawa_sub-{sub}.tsv", sep="\t").set_index("qc_row")
    g = bs.loc[rows.qc_row]
    assert (g.video_id.values == rows.video_id.values).all()
    low = pd.read_csv(PRE / "lowlevel_video_features.tsv", sep="\t", index_col=0)
    F = {"brain_roi469": R[:, valid].astype(np.float64),
         "brain_global": np.column_stack([g["raw_평균"].values, g["raw_표준편차"].values, np.log(g["raw_표준편차"].values)]),
         "lowlevel_L": low.loc[rows.video_id].values.astype(np.float64),
         "duration": rows.duration_sec.values.astype(np.float64)[:, None]}
    names = [l.strip() for l in open(LAB / "cowen34_order.txt") if l.strip()]
    D = pd.read_csv(META); D.index = D.stimulus_num.str.replace("stimulus_", "").astype(int)
    Y34 = D.loc[rows.video_id, [f"score_{i}" for i in range(34)]].values.astype(np.float64)
    C = pd.read_csv(LAB / "cowen_horikawa_labels.csv"); C.index = C.stim_num_int
    Y14 = C.reindex(rows.video_id)[[f"{d}_score" for d in DIMS14]].values.astype(np.float64)
    assert np.all((Y34 >= 0) & (Y34 <= 1)), "A34 가 [0,1] 비율이 아님"
    meta = dict(n_rows=int(len(rows)), n_roi_valid=int(valid.sum()), n_roi_total=int(len(valid)),
                n_a14_observed=int(np.isfinite(Y14).all(1).sum()), fold_sizes={int(k): int((fold == k).sum()) for k in np.unique(fold)})
    return rows, fold, F, Y34, names, Y14, meta


def run_subject(sub):
    t0 = time.time(); OUT.mkdir(parents=True, exist_ok=True); (OUT / "predictions").mkdir(exist_ok=True)
    rows, fold, F, Y34, names, Y14, meta = load_subject(sub)
    print(f"sub-{sub}: {meta}", flush=True)
    OPT_LOG.clear()
    obs14 = np.isfinite(Y14).all(1)
    preds, lams = [], []
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        inner = fold[tr]
        for cond in CONDITIONS:
            for space, Y, mask, dims in [("A34", Y34, np.ones(len(fold), bool), names), ("A14", Y14, obs14, DIMS14)]:
                trm, tem = tr & mask, te & mask
                mu_tr = Y[trm].mean(0)
                if cond == "train_mean":
                    P = np.tile(mu_tr, (tem.sum(), 1)); sel = np.full(len(dims), np.nan)
                else:
                    Xtr, Xte = make_features(cond, F, trm, tem)
                    fitf = fit_predict_a34 if space == "A34" else fit_predict_a14
                    P, sel = fitf(Xtr, Y[trm], Xte, fold[trm])
                idx = np.flatnonzero(tem)
                for k, d in enumerate(dims):
                    preds.append(pd.DataFrame(dict(participant_id=f"sub-{sub}", video_id=rows.video_id.values[idx],
                                                   run_index=rows.run_index.values[idx], outer_fold=int(f),
                                                   input_condition=cond, target_space=space, dimension=d,
                                                   y_true=Y[idx, k], y_pred=P[:, k], train_mean=mu_tr[k])))
                    lams.append(dict(participant_id=f"sub-{sub}", outer_fold=int(f), input_condition=cond,
                                     target_space=space, dimension=d, selected_regularization=sel[k]))
        print(f"  fold {f} 완료 ({time.time() - t0:.0f}초)", flush=True)
    pred = pd.concat(preds, ignore_index=True)
    for k, v in VERSIONS.items():
        pred[k] = v
    pred["feature_version"] = pred.input_condition.map({
        "train_mean": "없음", "duration": "samples duration_sec, 학습 분위 구간 원-핫",
        "lowlevel_L": "prelim/lowlevel_video_features.tsv (33개)", "brain_global": "prelim/block_stats raw 평균·표준편차·log 표준편차",
        "brain_roi469": f"prelim/roi_blocks roi469 run 안 z 영역 평균 ({meta['n_roi_valid']}개 유효)"})
    pred.insert(0, "analysis_id", "stage1_core3_brain_baseline_v1")
    pred.to_csv(OUT / f"predictions/sub-{sub}.tsv.gz", sep="\t", index=False, float_format="%.6g")
    dim, prof = evaluate(pred, sub)
    dim.to_csv(OUT / f"dimension_metrics_sub-{sub}.tsv", sep="\t", index=False, float_format="%.5f")
    prof.to_csv(OUT / f"profile_metrics_sub-{sub}.tsv", sep="\t", index=False, float_format="%.5f")
    pd.DataFrame(lams).to_csv(OUT / f"selected_lambda_sub-{sub}.tsv", sep="\t", index=False)
    meta.update(seconds=round(time.time() - t0), conditions=CONDITIONS, softbce_convergence=convergence_summary(), **VERSIONS)
    print("L-BFGS 수렴:", meta["softbce_convergence"], flush=True)
    (OUT / f"run_info_sub-{sub}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    s = dim.groupby(["target_space", "input_condition"], sort=False).agg(
        r_mean=("r_oof", "mean"), r_median=("r_oof", "median"), err_red_mean=("error_reduction", "mean"),
        n_dims=("r_oof", "count")).reset_index()
    pd.set_option("display.width", 200)
    print(s.round(4).to_string(index=False)); print(prof.round(4).to_string(index=False))
    print(f"sub-{sub} 완료 ({time.time() - t0:.0f}초)")


def self_test():
    rng = np.random.RandomState(0); n, p, k = 400, 20, 5
    X = rng.randn(n, p); W = rng.randn(p, k) * 0.5
    Y = expit(X @ W + rng.randn(n, k) * 0.3)                     # 0~1 의 soft target
    g = np.repeat(np.arange(5), n // 5)
    P, sel = fit_predict_a34(X[g != 0], Y[g != 0], X[g == 0], g[g != 0])
    r = [pearson(Y[g == 0][:, j], P[:, j]) for j in range(k)]
    assert min(r) > 0.8, f"soft BCE 회복 실패 {r}"
    th = fit_softbce_path(np.zeros((n, 1)), Y, [1.0])[0]          # 특징 없음 → 평균과 같아야
    assert np.allclose(expit(th[-1]), Y.mean(0), atol=1e-4)
    Z = X @ W + rng.randn(n, k) * 0.5
    P2, _ = fit_predict_a14(X[g != 0], Z[g != 0], X[g == 0], g[g != 0])
    r2 = [pearson(Z[g == 0][:, j], P2[:, j]) for j in range(k)]
    assert min(r2) > 0.8, f"ridge 회복 실패 {r2}"
    print("[self-test] 통과: soft BCE r", np.round(r, 3), "| ridge r", np.round(r2, 3), "| 절편만 = 평균 확인")


def lambda_edges(out_dir):
    """선택된 규제 강도가 격자 끝에 걸린 비율 (조건 × target 공간). 끝 선택이 많으면 격자를 넓혀야 한다."""
    files = sorted(Path(out_dir).glob("selected_lambda_sub-*.tsv"))
    if not files:
        return None
    L = pd.concat([pd.read_csv(f, sep="\t") for f in files]).dropna(subset=["selected_regularization"])
    grid = {"A34": LAM_BCE, "A14": ALPHA_RIDGE}
    L["at_max"] = [np.isclose(v, grid[s].max()) for v, s in zip(L.selected_regularization, L.target_space)]
    L["at_min"] = [np.isclose(v, grid[s].min()) for v, s in zip(L.selected_regularization, L.target_space)]
    return L.groupby(["target_space", "input_condition"], sort=False).agg(
        n_selections=("at_max", "size"), frac_at_max=("at_max", "mean"), frac_at_min=("at_min", "mean")).reset_index()


def summarize():
    """5명 결과를 합쳐 표로. 피험자별 값을 보존하고, 요약은 피험자별 값의 평균·범위."""
    dims = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(OUT.glob("dimension_metrics_sub-*.tsv"))])
    prof = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(OUT.glob("profile_metrics_sub-*.tsv"))])
    dims.to_csv(OUT / "dimension_metrics.tsv", sep="\t", index=False, float_format="%.5f")
    prof.to_csv(OUT / "profile_metrics.tsv", sep="\t", index=False, float_format="%.5f")
    per_sub = dims.groupby(["target_space", "input_condition", "participant_id"], sort=False).agg(
        r_mean=("r_oof", "mean"), err_red_mean=("error_reduction", "mean"), n_dims=("r_oof", "count")).reset_index()
    S = per_sub.groupby(["target_space", "input_condition"], sort=False).agg(
        r_mean_5명평균=("r_mean", "mean"), r_mean_최소=("r_mean", "min"), r_mean_최대=("r_mean", "max"),
        오차감소_5명평균=("err_red_mean", "mean"), 차원수=("n_dims", "first")).reset_index()
    S.to_csv(OUT / "summary_by_condition.tsv", sep="\t", index=False, float_format="%.4f")
    D = dims.groupby(["target_space", "input_condition", "dimension"], sort=False).agg(
        r_5명평균=("r_oof", "mean"), r_최소=("r_oof", "min"), r_최대=("r_oof", "max"), 오차감소_5명평균=("error_reduction", "mean")).reset_index()
    D.to_csv(OUT / "summary_by_dimension.tsv", sep="\t", index=False, float_format="%.4f")
    P = prof.groupby(["target_space", "input_condition"], sort=False).agg(
        프로필r_5명평균=("profile_r_mean", "mean"), 평균프로필_기준=("train_mean_profile_r_mean", "mean"),
        평균프로필대비_증가=("gain_over_mean_profile", "mean")).reset_index()
    P.to_csv(OUT / "summary_profile.tsv", sep="\t", index=False, float_format="%.4f")
    E = lambda_edges(OUT)
    if E is not None:
        E.to_csv(OUT / "selected_lambda_edges.tsv", sep="\t", index=False, float_format="%.4f")
        print(E.to_string(index=False))
    pd.set_option("display.width", 220); pd.set_option("display.max_rows", 200)
    print(f"피험자 {dims.participant_id.nunique()}명"); print(S.round(4).to_string(index=False)); print(P.round(4).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sub"); ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
    elif a.summarize:
        summarize()
    else:
        run_subject(a.sub)
