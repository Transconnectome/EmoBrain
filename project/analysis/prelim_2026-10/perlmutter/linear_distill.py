#!/usr/bin/env python3
"""선형 teacher–student pilot: 내용 teacher 의 예측을 보조 target 으로 섞어 뇌 단독 ridge student 를 학습 (2026-10-28).

질문: 내용 정보로 안내하면, 평가 때 뇌만 쓰는 student 의 정서 예측이 좋아지나?
  teacher : 내용 (V-JEPA 2 + 사람 캡션 임베딩) → 정서, ridge
  student : 뇌 469개 영역 → 정서, ridge. 학습 target = (1 - w) · 실제 평정 + w · teacher 예측
누출 방지
  - 분할·행은 비교 사다리와 같다 (horikawa_rungroup6_v1, 피험자별, 같은 내용은 같은 fold).
  - 학습 영상의 teacher 예측은 바깥 학습 fold 안에서의 교차검증 밖 예측 (teacher 는 평가 영상 라벨을 보지 않는다).
  - w 와 규제 강도는 차원마다 안쪽 검증으로 고른다. 검증 오차는 실제 평정으로 재고, 안쪽 검증 fold 를 뺀 자료로 teacher 를 다시 만든다.
  - 평가 영상에서 student 는 뇌만 쓴다.
pilot 단순화: 34개 범주도 ridge (비율을 그대로 target). 랩서버 soft BCE 기준선과 숫자가 다르며 비교는 이 pilot 안에서만 한다.
조건: student_w0 (뇌 단독 ridge), student_wsel (안쪽에서 고른 w), student_w<값> (w 고정, 참고용), teacher_content (내용만, 참고)
대조 (--labelpca): teacher 대신 학습 라벨의 주성분 k 개 smoothing. 내용 없이 target 만 매끄럽게 해도 같은 이득이 나는지 본다.
사용: python linear_distill.py --sub 01 | --summarize
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import run_stage1 as rs  # noqa: E402  (Perlmutter 경로·load_subject·load_features)

bb, cl = rs.bb, rs.cl
OUT = rs.OUT / "06_linear_distill"
TEACHER = ["vjepa2_vitg_final", "caption_human_mpnet"]
WS = [0.0, 0.25, 0.5, 0.75, 1.0]
ALPHAS = bb.ALPHA_RIDGE


def teacher_oof(C, Y, groups):
    """groups 묶음마다 나머지로 teacher 를 학습해 그 묶음을 예측 (교차검증 밖 예측)."""
    out = np.zeros_like(Y)
    for g in np.unique(groups):
        a, b = groups != g, groups == g
        Ca, Cb = cl.std_fit(C[a], C[b])
        out[b], _ = bb.fit_predict_a14(Ca, Y[a], Cb, groups[a])
    return out


def student_paths(Btr, Ymix, Bte):
    """표준화된 뇌 입력에서 α 격자별 예측 (출력 열마다 독립 ridge)."""
    U, s, Vt = np.linalg.svd(Btr, full_matrices=False)
    mu = Ymix.mean(0); UtY = U.T @ (Ymix - mu); BV = Bte @ Vt.T
    return np.stack([BV @ ((s / (s ** 2 + a))[:, None] * UtY) + mu for a in ALPHAS])   # (α, n_te, k)


def select_w_alpha(B, C, Y, groups):
    """안쪽 검증으로 차원별 (w, α) 선택. 오차는 실제 Y 로, teacher 는 검증 묶음을 뺀 자료로 다시 만든다."""
    err = np.zeros((len(WS), len(ALPHAS), Y.shape[1]))
    for g in np.unique(groups):
        a, b = groups != g, groups == g
        T = teacher_oof(C[a], Y[a], groups[a])
        Ba, Bb = cl.std_fit(B[a], B[b])
        for i, w in enumerate(WS):
            P = student_paths(Ba, (1 - w) * Y[a] + w * T, Bb)
            err[i] += ((P - Y[b][None]) ** 2).sum(1)
    flat = err.reshape(-1, Y.shape[1]).argmin(0)
    wi, ai = np.unravel_index(flat, err.shape[:2])
    a_fixed = err.argmin(1)                    # w 고정 시 α 선택 (w, k)
    return wi, ai, a_fixed


def run_subject(sub):
    t0 = time.time(); OUT.mkdir(parents=True, exist_ok=True)
    rows, fold, FB, Y34, names, Y14, meta = rs.load_subject(sub)
    vids = rows.video_id.values; B = FB["brain_roi469"]; pid = f"sub-{sub}"
    F = rs.load_features(); C = np.hstack([F[n].loc[vids].values for n in TEACHER])
    obs14 = np.isfinite(Y14).all(1); preds, sel = [], []
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        for space, Y, mask, dims in [("A34", Y34, np.ones(len(fold), bool), names), ("A14", Y14, obs14, bb.DIMS14)]:
            trm, tem = tr & mask, te & mask
            g = fold[trm]; Ytr = Y[trm]; idx = np.flatnonzero(tem)
            wi, ai, a_fixed = select_w_alpha(B[trm], C[trm], Ytr, g)
            T = teacher_oof(C[trm], Ytr, g)                                   # 학습 영상의 teacher 예측
            Btr, Bte = cl.std_fit(B[trm], B[tem])
            P_by_w = [student_paths(Btr, (1 - w) * Ytr + w * T, Bte) for w in WS]
            k = np.arange(Ytr.shape[1])
            conds = {"student_wsel": np.stack([P_by_w[wi[j]][ai[j], :, j] for j in k], 1)}
            for i, w in enumerate(WS):
                conds["student_w0" if w == 0 else f"student_w{w:g}"] = np.stack([P_by_w[i][a_fixed[i, j], :, j] for j in k], 1)
            Ctr, Cte = cl.std_fit(C[trm], C[tem])
            conds["teacher_content"], _ = bb.fit_predict_a14(Ctr, Ytr, Cte, g)
            mu = Ytr.mean(0)
            for cond, P in conds.items():
                for j, d in enumerate(dims):
                    preds.append(pd.DataFrame(dict(participant_id=pid, video_id=vids[idx], outer_fold=int(f), input_condition=cond,
                                                   target_space=space, dimension=d, y_true=Y[idx, j], y_pred=P[:, j], train_mean=mu[j])))
            sel += [dict(participant_id=pid, outer_fold=int(f), target_space=space, dimension=d,
                         w_selected=WS[wi[j]], alpha_selected=float(ALPHAS[ai[j]])) for j, d in enumerate(dims)]
        print(f"  {pid} fold {f} 완료 ({time.time() - t0:.0f}초)", flush=True)
    pred = pd.concat(preds, ignore_index=True)
    pred.to_csv(OUT / f"predictions_{pid}.tsv.gz", sep="\t", index=False, float_format="%.6g")
    pd.DataFrame(sel).to_csv(OUT / f"selected_w_{pid}.tsv", sep="\t", index=False)
    dim, _ = bb.evaluate(pred, sub)
    dim.to_csv(OUT / f"dimension_metrics_{pid}.tsv", sep="\t", index=False, float_format="%.5f")
    (OUT / f"run_info_{pid}.json").write_text(json.dumps(dict(teacher=TEACHER, ws=WS, seconds=round(time.time() - t0), **meta),
                                                       ensure_ascii=False, indent=1))
    print(dim.groupby(["target_space", "input_condition"], sort=False).r_oof.mean().round(4).to_string())
    print(f"{pid} 완료 ({time.time() - t0:.0f}초)")


KS = [1, 2, 3, 5, 8]


def label_smooth(Y, k):
    """내용 없는 대조 teacher: 학습 라벨을 학습 라벨의 주성분 k 개로 투영 (라벨 공간 smoothing)."""
    mu = Y.mean(0); Vt = np.linalg.svd(Y - mu, full_matrices=False)[2][:k]
    return (Y - mu) @ Vt.T @ Vt + mu


def run_subject_labelpca(sub):
    """대조: teacher 를 라벨 주성분 smoothing 으로 바꾼 같은 student. (k, w, α) 는 안쪽 검증으로 선택."""
    t0 = time.time(); od = OUT / "labelpca"; od.mkdir(parents=True, exist_ok=True)
    rows, fold, FB, Y34, names, Y14, meta = rs.load_subject(sub)
    vids = rows.video_id.values; B = FB["brain_roi469"]; pid = f"sub-{sub}"
    obs14 = np.isfinite(Y14).all(1); preds, sel = [], []
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        for space, Y, mask, dims in [("A34", Y34, np.ones(len(fold), bool), names), ("A14", Y14, obs14, bb.DIMS14)]:
            trm, tem = tr & mask, te & mask
            g = fold[trm]; Ytr = Y[trm]; idx = np.flatnonzero(tem); K = Ytr.shape[1]
            err = np.zeros((len(KS), len(WS), len(ALPHAS), K))
            for h in np.unique(g):
                a, b = g != h, g == h
                Ba, Bb = cl.std_fit(B[trm][a], B[trm][b])
                for ki, k in enumerate(KS):
                    T = label_smooth(Ytr[a], k)
                    for wi, w in enumerate(WS):
                        err[ki, wi] += ((student_paths(Ba, (1 - w) * Ytr[a] + w * T, Bb) - Ytr[b][None]) ** 2).sum(1)
            ki, wi, ai = np.unravel_index(err.reshape(-1, K).argmin(0), err.shape[:3])
            Btr, Bte = cl.std_fit(B[trm], B[tem])
            P = np.zeros((len(idx), K))
            for j in range(K):
                T = label_smooth(Ytr, KS[ki[j]]); w = WS[wi[j]]
                P[:, j] = student_paths(Btr, (1 - w) * Ytr[:, [j]] + w * T[:, [j]], Bte)[ai[j], :, 0]
            P0 = student_paths(Btr, Ytr, Bte)[err[0, 0].argmin(0), :, np.arange(K)].T     # w = 0 (k 와 무관)
            mu = Ytr.mean(0)
            for cond, PP in [("student_w0", P0), ("labelpca_wsel", P)]:
                for j, d in enumerate(dims):
                    preds.append(pd.DataFrame(dict(participant_id=pid, video_id=vids[idx], outer_fold=int(f), input_condition=cond,
                                                   target_space=space, dimension=d, y_true=Y[idx, j], y_pred=PP[:, j], train_mean=mu[j])))
            sel += [dict(participant_id=pid, outer_fold=int(f), target_space=space, dimension=d, k_selected=KS[ki[j]],
                         w_selected=WS[wi[j]], alpha_selected=float(ALPHAS[ai[j]])) for j, d in enumerate(dims)]
    pred = pd.concat(preds, ignore_index=True)
    dim, _ = bb.evaluate(pred, sub)
    dim.to_csv(od / f"dimension_metrics_{pid}.tsv", sep="\t", index=False, float_format="%.5f")
    pd.DataFrame(sel).to_csv(od / f"selected_w_{pid}.tsv", sep="\t", index=False)
    print(dim.groupby(["target_space", "input_condition"], sort=False).r_oof.mean().round(4).to_string())
    print(f"{pid} labelpca 완료 ({time.time() - t0:.0f}초)")


def summarize(out=None):
    out = out or OUT
    D = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(out.glob("dimension_metrics_sub-*.tsv"))])
    W = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(out.glob("selected_w_sub-*.tsv"))])
    rows = []
    for space, g in D.groupby("target_space", sort=False):
        h = g.pivot_table(index=["participant_id", "dimension"], columns="input_condition", values="r_oof")
        per = h.groupby("participant_id").mean()
        for cond in [c for c in per.columns if c != "student_w0"]:
            dlt = per[cond] - per["student_w0"]; dd = (h[cond] - h["student_w0"]).groupby("dimension").mean()
            rows.append(dict(target_space=space, condition=cond, r_mean=per[cond].mean(), r_min=per[cond].min(), r_max=per[cond].max(),
                             r_w0=per["student_w0"].mean(), delta_vs_w0=dlt.mean(), delta_min=dlt.min(), delta_max=dlt.max(),
                             n_subjects_gain=int((dlt > 0).sum()), n_dims_gain=int((dd > 0).sum()), n_dims=len(dd)))
    S = pd.DataFrame(rows); S.to_csv(out / "summary.tsv", sep="\t", index=False, float_format="%.4f")
    wsum = W.groupby("target_space").w_selected.agg(["mean", lambda x: (x == 0).mean(), lambda x: (x == 1).mean()])
    wsum.columns = ["w_mean", "frac_w0", "frac_w1"]; wsum.to_csv(out / "selected_w_summary.tsv", sep="\t", float_format="%.3f")
    pd.set_option("display.width", 220); print(S.round(4).to_string(index=False)); print(wsum.round(3))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sub"); ap.add_argument("--summarize", action="store_true")
    ap.add_argument("--labelpca", action="store_true", help="내용 없는 대조 teacher (라벨 주성분 smoothing)")
    a = ap.parse_args()
    if a.summarize:
        summarize(OUT / "labelpca" if a.labelpca else OUT)
    else:
        run_subject_labelpca(a.sub) if a.labelpca else run_subject(a.sub)
