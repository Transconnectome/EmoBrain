#!/usr/bin/env python3
"""EmoBrain 1단계 핵심 4·5 + 비교 사다리: 내용 특징 → 정서, 뇌 → 내용, 뇌 → 내용 → 정서, 뇌+내용 → 정서 (2026-10-24).

기준선(brain_baseline.py)과 같은 분할(horikawa_rungroup6_v1), 같은 모델(A34 soft BCE 선형, A14 ridge), 같은 선택 절차를 쓴다.

--stimulus : 내용 특징 → 정서 (영상 단위, 피험자와 무관. 분석 영상 2,181개). 뇌 QC 로 빠진 영상도 들어 있어
             피험자별 행과 학습·평가 영상이 다르다. 뇌 조건과의 비교에는 --sub 의 같은 행 결과를 쓴다.
--sub XX   : 피험자별. 아래 조건은 모두 그 피험자의 같은 학습·평가 영상(같은 fold)에서 계산한다.
             brain_roi469 : 뇌만 (02_brain 의 같은 이름 조건과 같은 계산)
             <특징>       : 내용만 (같은 피험자 행)
             뇌 → 내용 : 469개 영역 → 각 특징 (ridge, 특징 열마다 영상 간 r)
             뇌 → 내용 → 정서 : 뇌에서 예측한 특징을, 학습 영상의 실제 특징으로 배운 "특징 → 정서" 모델에 넣음.
                              정서 모델은 학습 영상의 실제 특징과 정서 라벨을 본다. 평가 영상에서만 뇌 예측 특징을 쓴다.
             뇌+내용 → 정서 : 469개 영역과 특징을 열마다 표준화해 이어 붙이고, 출력마다 규제 강도 하나
--summarize : 피험자별 같은 행 비교표 (04_brain_features/ladder_same_rows*.tsv)
특징 (FEATURES): 표준 형식 /storage/bigdata/EmoBrain_response/features/<이름>.npy + <이름>_video_id.tsv 가 있으면 자동으로 추가된다.
  lowlevel_L      : 저수준 시각 33개 (0단계)
  hk_vision1000   : Horikawa 원자료 시각 특징 (VGG19 fc8, ImageNet 1000개 범주, 영상 평균)
  hk_semantic73   : Horikawa 원자료 의미 특징 (73개 개념, 평정자 이진 응답 평균)
출력: stage1/03_stimulus/ (내용 → 정서), stage1/04_brain_features/ (뇌 → 내용, 사다리)
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

S1 = Path("/storage/bigdata/EmoBrain_response/stage1")
FEAT_DIR = Path("/storage/bigdata/EmoBrain_response/features")
META_DIR = Path("/storage/bigdata/Horikawa/metadata")


def load_features():
    """영상 번호(1~2196)를 행 이름으로 하는 특징 표들."""
    F = {}
    F["lowlevel_L"] = pd.read_csv(bb.PRE / "lowlevel_video_features.tsv", sep="\t", index_col=0)
    for name, fn in [("hk_vision1000", "vision_features.csv"), ("hk_semantic73", "semantic_features.csv")]:
        d = pd.read_csv(META_DIR / fn); d.index = d.pop("stimulus_num").str.replace("stimulus_", "").astype(int)
        F[name] = d.astype(np.float64)
    for p in sorted(FEAT_DIR.glob("*.npy")) if FEAT_DIR.exists() else []:
        ids = pd.read_csv(p.with_name(p.stem + "_video_id.tsv"), sep="\t").video_id.values
        F[p.stem] = pd.DataFrame(np.load(p).astype(np.float64), index=ids)
    return F


def std_fit(Xtr, Xte):
    mu, sd = Xtr.mean(0), Xtr.std(0); sd[sd == 0] = 1
    return (Xtr - mu) / sd, (Xte - mu) / sd


def emotion_fit(space, Xtr, Ytr, Xte, groups):
    return (bb.fit_predict_a34 if space == "A34" else bb.fit_predict_a14)(Xtr, Ytr, Xte, groups)


def labels_for(vids):
    names = [l.strip() for l in open(bb.LAB / "cowen34_order.txt") if l.strip()]
    D = pd.read_csv(bb.META); D.index = D.stimulus_num.str.replace("stimulus_", "").astype(int)
    Y34 = D.loc[vids, [f"score_{i}" for i in range(34)]].values.astype(np.float64)
    C = pd.read_csv(bb.LAB / "cowen_horikawa_labels.csv"); C.index = C.stim_num_int
    Y14 = C.reindex(vids)[[f"{d}_score" for d in bb.DIMS14]].values.astype(np.float64)
    return names, Y34, Y14


def emotion_cv(X_of, fold, vids, Y34, Y14, names, cond, pid, extra=None):
    """X_of(tr, te) -> (Xtr, Xte) 를 받아 정서 두 공간의 바깥 6겹 예측을 긴 형식으로."""
    obs14 = np.isfinite(Y14).all(1); out = []
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        for space, Y, mask, dims in [("A34", Y34, np.ones(len(fold), bool), names), ("A14", Y14, obs14, bb.DIMS14)]:
            trm, tem = tr & mask, te & mask
            Xtr, Xte = X_of(trm, tem)
            P, _ = emotion_fit(space, Xtr, Y[trm], Xte, fold[trm])
            mu = Y[trm].mean(0); idx = np.flatnonzero(tem)
            for k, d in enumerate(dims):
                out.append(pd.DataFrame(dict(participant_id=pid, video_id=vids[idx], outer_fold=int(f), input_condition=cond,
                                             target_space=space, dimension=d, y_true=Y[idx, k], y_pred=P[:, k], train_mean=mu[k])))
    return out


def run_stimulus():
    t0 = time.time(); od = S1 / "03_stimulus"; (od / "predictions").mkdir(parents=True, exist_ok=True)
    split = pd.read_csv(bb.SPLIT, sep="\t"); split = split[split.analysis_row].reset_index(drop=True)
    vids, fold = split.video_id.values, split.fold.values
    names, Y34, Y14 = labels_for(vids)
    F = load_features()
    combos = {k: [k] for k in F}
    combos["hk_vision1000+hk_semantic73"] = ["hk_vision1000", "hk_semantic73"]
    combos["lowlevel_L+hk_vision1000+hk_semantic73"] = ["lowlevel_L", "hk_vision1000", "hk_semantic73"]
    for extra in [k for k in F if k not in ("lowlevel_L", "hk_vision1000", "hk_semantic73")]:
        combos[f"{extra}+hk_semantic73"] = [extra, "hk_semantic73"]
    combos = {k: v for k, v in combos.items() if all(p in F for p in v)}   # 있는 특징으로만 조합
    print("내용 조건:", list(combos), flush=True)
    preds = []
    for cond, parts in combos.items():
        X = np.hstack([F[p].loc[vids].values for p in parts])
        preds += emotion_cv(lambda tr, te: std_fit(X[tr], X[te]), fold, vids, Y34, Y14, names, cond, "영상 단위")
        print(f"  {cond} ({X.shape[1]}차원) 완료 ({time.time() - t0:.0f}초)", flush=True)
    pred = pd.concat(preds, ignore_index=True); pred["split_id"] = "horikawa_rungroup6_v1"
    pred.to_csv(od / "predictions/stimulus.tsv.gz", sep="\t", index=False, float_format="%.6g")
    dim, prof = bb.evaluate(pred, "stim"); dim["participant_id"] = "영상 단위"; prof["participant_id"] = "영상 단위"
    dim.to_csv(od / "dimension_metrics.tsv", sep="\t", index=False, float_format="%.5f")
    prof.to_csv(od / "profile_metrics.tsv", sep="\t", index=False, float_format="%.5f")
    s = dim.groupby(["target_space", "input_condition"], sort=False).agg(r_mean=("r_oof", "mean"), err_red=("error_reduction", "mean")).reset_index()
    pd.set_option("display.width", 200); print(s.round(4).to_string(index=False)); print(f"완료 ({time.time() - t0:.0f}초)")


def run_subject(sub):
    t0 = time.time(); od = S1 / "04_brain_features"; (od / "predictions").mkdir(parents=True, exist_ok=True)
    rows, fold, FB, Y34, names, Y14, meta = bb.load_subject(sub)
    vids = rows.video_id.values; B = FB["brain_roi469"]; pid = f"sub-{sub}"
    F = load_features()
    bb.OPT_LOG.clear()
    feat_rows = []
    # 뇌만: 아래 내용 조건과 같은 행·fold
    preds = emotion_cv(lambda tr, te: std_fit(B[tr], B[te]), fold, vids, Y34, Y14, names, "brain_roi469", pid)
    for name, T in F.items():
        Z = T.loc[vids].values
        # 1) 뇌 → 내용 (특징 열마다 ridge; 열은 train 평균·표준편차로 표준화 후 학습)
        Zhat = np.zeros_like(Z)
        for f in np.unique(fold):
            tr, te = fold != f, fold == f
            Btr, Bte = std_fit(B[tr], B[te])
            Zhat[te], _ = bb.fit_predict_a14(Btr, Z[tr], Bte, fold[tr])
        rs = np.array([bb.pearson(Z[:, j], Zhat[:, j]) if Z[:, j].std() > 0 else np.nan for j in range(Z.shape[1])])
        # 영상 짝 구별: 같은 fold 안에서 예측 특징이 자기 영상의 실제 특징과 더 닮았는지 (우연 0.5)
        acc = []
        for f in np.unique(fold):
            te = fold == f; a = Zhat[te] - Z[fold != f].mean(0); b_ = Z[te] - Z[fold != f].mean(0)
            a /= np.linalg.norm(a, axis=1, keepdims=True) + 1e-12; b_ /= np.linalg.norm(b_, axis=1, keepdims=True) + 1e-12
            S = a @ b_.T; d = np.diag(S); acc.append(np.mean([(d[i] > np.delete(S[i], i)).mean() for i in range(len(S))]))
        feat_rows.append(dict(participant_id=pid, feature=name, n_dims=Z.shape[1], r_mean=float(np.nanmean(rs)),
                              r_median=float(np.nanmedian(rs)), frac_r_gt_0p1=float(np.nanmean(rs > 0.1)),
                              pair_identification=float(np.mean(acc))))
        np.save(od / f"predictions/{pid}_{name}_brain_predicted.npy", Zhat.astype(np.float32))
        # 0) 내용만, 같은 피험자 행
        preds += emotion_cv(lambda tr, te: std_fit(Z[tr], Z[te]), fold, vids, Y34, Y14, names, name, pid)
        # 2) 뇌 → 내용 → 정서: 정서 모델은 학습 영상의 실제 특징으로, 평가 영상에는 뇌에서 예측한 특징을 넣는다
        preds += emotion_cv(lambda tr, te: std_fit(Z[tr], Zhat[te]), fold, vids, Y34, Y14, names, f"brain→{name}→emotion", pid)
        # 3) 뇌 + 내용 → 정서
        X = np.hstack([B, Z])
        preds += emotion_cv(lambda tr, te: std_fit(X[tr], X[te]), fold, vids, Y34, Y14, names, f"brain+{name}", pid)
        print(f"  {name}: 뇌→내용 r 평균 {np.nanmean(rs):.3f}, 짝 구별 {np.mean(acc):.3f} ({time.time() - t0:.0f}초)", flush=True)
    pd.DataFrame(feat_rows).to_csv(od / f"brain_to_feature_sub-{sub}.tsv", sep="\t", index=False, float_format="%.5f")
    pred = pd.concat(preds, ignore_index=True); pred["split_id"] = "horikawa_rungroup6_v1"
    pred.to_csv(od / f"predictions/sub-{sub}_ladder.tsv.gz", sep="\t", index=False, float_format="%.6g")
    dim, prof = bb.evaluate(pred, sub)
    dim.to_csv(od / f"ladder_dimension_metrics_sub-{sub}.tsv", sep="\t", index=False, float_format="%.5f")
    prof.to_csv(od / f"ladder_profile_metrics_sub-{sub}.tsv", sep="\t", index=False, float_format="%.5f")
    s = dim.groupby(["target_space", "input_condition"], sort=False).agg(r_mean=("r_oof", "mean")).reset_index()
    pd.set_option("display.width", 200); print(pd.DataFrame(feat_rows).round(3).to_string(index=False)); print(s.round(4).to_string(index=False))
    conv = bb.convergence_summary(); print("L-BFGS 수렴:", conv, flush=True)
    (od / f"run_info_sub-{sub}.json").write_text(json.dumps(dict(features=list(F), seconds=round(time.time() - t0),
                                                                 softbce_convergence=conv, **meta), ensure_ascii=False, indent=1))
    print(f"sub-{sub} 완료 ({time.time() - t0:.0f}초)")


def summarize():
    """피험자별 같은 학습·평가 영상에서 내용만, 뇌만, 뇌 → 내용 → 정서, 뇌 + 내용을 비교한다.

    r 의 비율(뇌 → 내용 → 정서 / 뇌만)은 두 예측의 성능 비율이다. 공유 정보나 설명 분산의 비율이 아니다.
    """
    od = S1 / "04_brain_features"
    dims = pd.concat([pd.read_csv(f, sep="\t") for f in sorted(od.glob("ladder_dimension_metrics_sub-*.tsv"))])
    n_eval = dims.groupby(["participant_id", "target_space", "dimension"]).n_eval.nunique()
    assert (n_eval == 1).all(), f"같은 피험자·차원에서 조건마다 평가 행 수가 다름: {n_eval[n_eval > 1].head()}"
    sets = [("A34 전체 34개", lambda d: d.target_space == "A34"),
            ("A34 27개 (기술 요약)", lambda d: (d.target_space == "A34") & ~d.dimension.isin(bb.NOT_DISTINCT7)),
            ("A14 척도 14개", lambda d: d.target_space == "A14")]
    feats = [c for c in dims.input_condition.unique() if f"brain+{c}" in set(dims.input_condition)]
    rows = []
    for pid, g in dims.groupby("participant_id"):
        for label, sel in sets:
            h = g[sel(g)].pivot_table(index="dimension", columns="input_condition", values="r_oof")
            for name in feats:
                c, b, via, both = h[name], h["brain_roi469"], h[f"brain→{name}→emotion"], h[f"brain+{name}"]
                rows.append(dict(participant_id=pid, 묶음=label, feature=name, n_dims=len(h),
                                 n_eval_rows=int(g[sel(g)].n_eval.max()),
                                 r_content_only=c.mean(), r_brain_only=b.mean(), r_brain_via_content=via.mean(), r_brain_plus_content=both.mean(),
                                 plus_minus_content=(both - c).mean(), n_dims_plus_gt_content=int((both > c).sum()),
                                 via_over_brain_ratio=via.mean() / b.mean()))
    D = pd.DataFrame(rows)
    D.to_csv(od / "ladder_same_rows_by_subject.tsv", sep="\t", index=False, float_format="%.4f")
    cols = ["r_content_only", "r_brain_only", "r_brain_via_content", "r_brain_plus_content", "plus_minus_content", "via_over_brain_ratio"]
    S = D.groupby(["묶음", "feature"], sort=False)[cols].agg(["mean", "min", "max"])
    S.columns = [f"{a}_{b}" for a, b in S.columns]
    S["n_subjects_plus_gt_content"] = D.assign(pos=D.plus_minus_content > 0).groupby(["묶음", "feature"], sort=False).pos.sum()
    S = S.reset_index(); S.to_csv(od / "ladder_same_rows_summary.tsv", sep="\t", index=False, float_format="%.4f")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    print(S[["묶음", "feature"] + [f"{c}_mean" for c in cols] + ["n_subjects_plus_gt_content"]].round(4).to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--stimulus", action="store_true"); ap.add_argument("--sub")
    ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args()
    run_stimulus() if a.stimulus else summarize() if a.summarize else run_subject(a.sub)
