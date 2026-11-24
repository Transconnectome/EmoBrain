#!/usr/bin/env python3
"""랩서버 1단계 비교 사다리를 Perlmutter 자료로 실행 (2026-10-27).

랩서버 코드(stage1/brain_baseline.py, content_ladder.py)의 모델·분할·선택 절차를 그대로 쓰고 경로만 바꾼다.
  roi        : v3_qc 블록 반응(run 안 z)에서 469개 영역 평균을 만든다 (prelim/brain_reliability.py 1단계와 같은 계산).
  stimulus   : 내용 특징 → 정서 (영상 단위)
  sub XX     : 피험자별 뇌만, 내용만, 뇌 → 내용, 뇌 → 내용 → 정서, 뇌 + 내용 (모두 같은 행·fold)
  summarize  : 같은 행 비교표 + 랩서버 뇌 기준선과의 재현 대조
랩서버와 다른 점: 저수준 시각(lowlevel_L)과 블록 통계 기준선은 Perlmutter 에 입력이 없어 뺀다.
출력: project/output/prelim_2026-10/ (git 에 올리지 않음)
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/pscratch/sd/s/sjmoon/EmoBrain")
sys.path.insert(0, str(REPO / "project/analysis/prelim_2026-10/stage1"))
import brain_baseline as bb  # noqa: E402
import content_ladder as cl  # noqa: E402

HK = Path("/pscratch/sd/s/sjmoon/Horikawa")
OUT = REPO / "project/output/prelim_2026-10"
FEAT_DIR = Path("/pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026")
META_DIR = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata")
ATLAS = "Schaefer400x7N+TianS3+HypoBNST+Cereb7N+Brainstem"
LAB_REPORT = REPO / "docs/reports/prelim_2026-10/stage1"

bb.SPLIT = REPO / "docs/reports/prelim_2026-10/splits/horikawa_rungroup6_v1.tsv"
bb.LAB = REPO / "project/shared/data"
bb.META = META_DIR / "horikawa_meta_data_with_dimension_binary.csv"
bb.PRE = OUT
bb.OUT = OUT / "02_brain"
cl.S1 = OUT
cl.FEAT_DIR = FEAT_DIR
cl.META_DIR = META_DIR


def make_roi(sub):
    import nibabel as nib
    q, base = HK / f"sub-{sub}/v3_qc", HK / f"sub-{sub}/v3"
    T = pd.read_csv(q / f"sub-{sub}_samples_qc_usable.tsv", sep="\t")
    Y = np.load(q / f"sub-{sub}_blocks_common36_qc_runz.npy", mmap_mode="r")
    mimg = nib.load(str(q / f"sub-{sub}_mask_qc.nii.gz")); M = np.asarray(mimg.dataobj) > 0
    aimg = nib.load(str(base / "atlas" / f"sub-{sub}_space-T1w_atlas-{ATLAS}_dseg.nii.gz"))
    assert aimg.shape == M.shape and np.allclose(aimg.affine, mimg.affine, atol=1e-4), "지도 격자 다름"
    assert Y.shape == (len(T), M.sum()), f"모양 불일치 {Y.shape} vs {(len(T), M.sum())}"
    lab = pd.read_csv(base / "atlas" / f"sub-{sub}_atlas-{ATLAS}_labels.tsv", sep="\t")
    valid = pd.read_csv(q / f"sub-{sub}_roi_valid.tsv", sep="\t"); valid = valid[valid.atlas == ATLAS].set_index("roi_id")
    roi_of = np.asarray(aimg.dataobj)[M].astype(int)
    ids = lab.roi_id.values
    order = np.argsort(roi_of, kind="stable"); sorted_roi = roi_of[order]
    starts = np.searchsorted(sorted_roi, ids); ends = np.searchsorted(sorted_roi, ids, side="right"); nvox = ends - starts
    R = np.full((len(T), len(ids)), np.nan, np.float32)
    for i0 in range(0, len(T), 64):
        sl = slice(i0, min(i0 + 64, len(T)))
        X = np.asarray(Y[sl], np.float64)[:, order]
        cs = np.concatenate([np.zeros((X.shape[0], 1)), np.cumsum(X, 1)], 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            R[sl] = ((cs[:, ends] - cs[:, starts]) / np.where(nvox > 0, nvox, np.nan)).astype(np.float32)
    od = OUT / "roi_blocks"; od.mkdir(parents=True, exist_ok=True)
    np.save(od / f"Horikawa_sub-{sub}_roi469_runz.npy", R)
    info = lab[["roi_id", "name", "hemi", "network"]].copy(); info["n_vox_qc"] = nvox
    info["roi_valid"] = [bool(valid.roi_valid.get(r, False)) for r in ids]
    info.to_csv(od / f"Horikawa_sub-{sub}_roi469_info.tsv", sep="\t", index=False)
    T.to_csv(od / f"Horikawa_sub-{sub}_roi469_rows.tsv", sep="\t", index=False)
    print(f"sub-{sub}: 블록 {len(T)}, 영역 {len(ids)}, 유효 {int(info.roi_valid.sum())}", flush=True)


def load_subject(sub):
    """bb.load_subject 와 같은 행·fold·라벨. 블록 통계와 저수준 시각은 넣지 않는다."""
    rows = pd.read_csv(OUT / f"roi_blocks/Horikawa_sub-{sub}_roi469_rows.tsv", sep="\t")
    R = np.load(OUT / f"roi_blocks/Horikawa_sub-{sub}_roi469_runz.npy")
    info = pd.read_csv(OUT / f"roi_blocks/Horikawa_sub-{sub}_roi469_info.tsv", sep="\t")
    assert len(rows) == len(R)
    split = pd.read_csv(bb.SPLIT, sep="\t").set_index("video_id")
    keep = ~rows.exclude_duplicate.astype(bool).values
    rows = rows[keep].reset_index(drop=True); R = R[keep]
    assert (split.loc[rows.video_id, "run_index"].values == rows.run_index.values).all(), "분할 표와 run_index 불일치"
    fold = split.loc[rows.video_id, "fold"].values
    valid = info.roi_valid.values & np.isfinite(R).all(0)
    F = {"brain_roi469": R[:, valid].astype(np.float64), "duration": rows.duration_sec.values.astype(np.float64)[:, None]}
    names, Y34, Y14 = cl.labels_for(rows.video_id.values)
    assert np.all((Y34 >= 0) & (Y34 <= 1)), "A34 가 [0,1] 비율이 아님"
    meta = dict(n_rows=int(len(rows)), n_roi_valid=int(valid.sum()), n_roi_total=int(len(valid)),
                n_a14_observed=int(np.isfinite(Y14).all(1).sum()), fold_sizes={int(k): int((fold == k).sum()) for k in np.unique(fold)})
    return rows, fold, F, Y34, names, Y14, meta


def load_features():
    """Horikawa 시각 1000·의미 73 + 표준 형식 특징 (V-JEPA, caption). 저수준 시각은 Perlmutter 에 없음."""
    F = {}
    for name, fn in [("hk_vision1000", "vision_features.csv"), ("hk_semantic73", "semantic_features.csv")]:
        d = pd.read_csv(META_DIR / fn); d.index = d.pop("stimulus_num").str.replace("stimulus_", "").astype(int)
        F[name] = d.astype(np.float64)
    for p in sorted(FEAT_DIR.glob("*.npy")):
        ids = pd.read_csv(p.with_name(p.stem + "_video_id.tsv"), sep="\t").video_id.values
        F[p.stem] = pd.DataFrame(np.load(p).astype(np.float64), index=ids)
    return F


bb.load_subject = load_subject
cl.load_features = load_features


def emotion_cv_shared(make, fold, vids, Y34, Y14, names, conds, pid):
    """cl.emotion_cv 와 같은 계산. make(trm, tem) -> (Xtr, [Xte...]) 로 학습이 같은 조건들을 한 번만 fit 한다.
    내용만과 뇌 → 내용 → 정서는 학습 입력(학습 영상의 실제 특징)과 라벨이 같아 같은 모델이고, 평가 입력만 다르다."""
    obs14 = np.isfinite(Y14).all(1); out = []
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        for space, Y, mask, dims in [("A34", Y34, np.ones(len(fold), bool), names), ("A14", Y14, obs14, bb.DIMS14)]:
            trm, tem = tr & mask, te & mask
            Xtr, Xtes = make(trm, tem)
            P, _ = cl.emotion_fit(space, Xtr, Y[trm], np.vstack(Xtes), fold[trm])
            mu = Y[trm].mean(0); idx = np.flatnonzero(tem); m = len(idx)
            for c, cond in enumerate(conds):
                Pc = P[c * m:(c + 1) * m]
                for k, d in enumerate(dims):
                    out.append(pd.DataFrame(dict(participant_id=pid, video_id=vids[idx], outer_fold=int(f), input_condition=cond,
                                                 target_space=space, dimension=d, y_true=Y[idx, k], y_pred=Pc[:, k], train_mean=mu[k])))
    return out


UNIT_FEATURES = ["hk_semantic73", "caption_human_mpnet", "vjepa2_vitg_final"]


def run_unit(sub, unit):
    """피험자 하나의 일부 조건. unit = brain | <특징>:content | <특징>:plus | <특징>:all. 결과는 04_brain_features/units/."""
    import time
    t0 = time.time(); od = OUT / "04_brain_features"; ud = od / "units"; ud.mkdir(parents=True, exist_ok=True)
    (od / "predictions").mkdir(exist_ok=True)
    rows, fold, FB, Y34, names, Y14, meta = load_subject(sub)
    vids = rows.video_id.values; B = FB["brain_roi469"]; pid = f"sub-{sub}"
    bb.OPT_LOG.clear(); preds = []
    if unit == "brain":
        preds = cl.emotion_cv(lambda tr, te: cl.std_fit(B[tr], B[te]), fold, vids, Y34, Y14, names, "brain_roi469", pid)
    else:
        name, part = unit.split(":")
        Z = load_features()[name].loc[vids].values
        if part in ("content", "all"):
            Zhat = np.zeros_like(Z)
            for f in np.unique(fold):
                tr, te = fold != f, fold == f
                Btr, Bte = cl.std_fit(B[tr], B[te])
                Zhat[te], _ = bb.fit_predict_a14(Btr, Z[tr], Bte, fold[tr])
            rs = np.array([bb.pearson(Z[:, j], Zhat[:, j]) if Z[:, j].std() > 0 else np.nan for j in range(Z.shape[1])])
            acc = []
            for f in np.unique(fold):
                te = fold == f; a = Zhat[te] - Z[fold != f].mean(0); b_ = Z[te] - Z[fold != f].mean(0)
                a /= np.linalg.norm(a, axis=1, keepdims=True) + 1e-12; b_ /= np.linalg.norm(b_, axis=1, keepdims=True) + 1e-12
                S = a @ b_.T; d = np.diag(S); acc.append(np.mean([(d[i] > np.delete(S[i], i)).mean() for i in range(len(S))]))
            pd.DataFrame([dict(participant_id=pid, feature=name, n_dims=Z.shape[1], r_mean=float(np.nanmean(rs)),
                               r_median=float(np.nanmedian(rs)), frac_r_gt_0p1=float(np.nanmean(rs > 0.1)),
                               pair_identification=float(np.mean(acc)))]).to_csv(ud / f"brain_to_feature_{pid}_{name}.tsv", sep="\t", index=False, float_format="%.5f")
            np.save(od / f"predictions/{pid}_{name}_brain_predicted.npy", Zhat.astype(np.float32))
            print(f"  {name}: 뇌→내용 r 평균 {np.nanmean(rs):.3f}, 짝 구별 {np.mean(acc):.3f} ({time.time() - t0:.0f}초)", flush=True)
            def make(tr, te):
                Xtr, Xc = cl.std_fit(Z[tr], Z[te]); _, Xv = cl.std_fit(Z[tr], Zhat[te]); return Xtr, [Xc, Xv]
            preds += emotion_cv_shared(make, fold, vids, Y34, Y14, names, [name, f"brain→{name}→emotion"], pid)
        if part in ("plus", "all"):
            X = np.hstack([B, Z])
            preds += cl.emotion_cv(lambda tr, te: cl.std_fit(X[tr], X[te]), fold, vids, Y34, Y14, names, f"brain+{name}", pid)
    pred = pd.concat(preds, ignore_index=True); pred["split_id"] = "horikawa_rungroup6_v1"
    tag = unit.replace(":", "_")
    pred.to_csv(ud / f"{pid}_{tag}.tsv.gz", sep="\t", index=False, float_format="%.6g")
    import json
    (ud / f"{pid}_{tag}_run_info.json").write_text(json.dumps(dict(unit=unit, seconds=round(time.time() - t0),
                                                                   softbce_convergence=bb.convergence_summary(), **meta), ensure_ascii=False, indent=1))
    dim, _ = bb.evaluate(pred, sub)
    print(dim.groupby(["target_space", "input_condition"], sort=False).r_oof.mean().round(4).to_string(), flush=True)
    print(f"{pid} {unit} 완료 ({time.time() - t0:.0f}초)", flush=True)


def collect_units():
    """units/ 의 원예측을 피험자별로 합쳐 ladder 지표 파일을 만든다 (cl.run_subject 와 같은 파일 이름)."""
    od = OUT / "04_brain_features"; ud = od / "units"
    for sub in ["01", "02", "03", "04", "05"]:
        fs = sorted(ud.glob(f"sub-{sub}_*.tsv.gz"))
        if not fs:
            continue
        pred = pd.concat([pd.read_csv(f, sep="\t") for f in fs], ignore_index=True)
        dim, prof = bb.evaluate(pred, sub)
        dim.to_csv(od / f"ladder_dimension_metrics_sub-{sub}.tsv", sep="\t", index=False, float_format="%.5f")
        prof.to_csv(od / f"ladder_profile_metrics_sub-{sub}.tsv", sep="\t", index=False, float_format="%.5f")
        print(f"sub-{sub}: 단위 {len(fs)}개, 조건 {sorted(pred.input_condition.unique())}")


def reproduction_check():
    """Perlmutter 의 뇌만 결과가 랩서버 02_brain 뇌 기준선과 같은지 (같은 자료·코드면 거의 같아야 한다)."""
    lab = pd.read_csv(LAB_REPORT / "02_brain/dimension_metrics.tsv", sep="\t")
    lab = lab[lab.input_condition == "brain_roi469"].set_index(["participant_id", "target_space", "dimension"])
    files = sorted((OUT / "04_brain_features").glob("ladder_dimension_metrics_sub-*.tsv"))
    ours = pd.concat([pd.read_csv(f, sep="\t") for f in files])
    ours = ours[ours.input_condition == "brain_roi469"].set_index(["participant_id", "target_space", "dimension"])
    j = ours[["r_oof", "n_eval"]].join(lab[["r_oof", "n_eval"]], rsuffix="_lab", how="inner")
    d = (j.r_oof - j.r_oof_lab).abs()
    print(f"재현 대조: {len(j)}개 (피험자 × 차원), |Δr| 최대 {d.max():.5f}, 평균 {d.mean():.6f}, n_eval 일치 {(j.n_eval == j.n_eval_lab).all()}")
    j.assign(abs_diff=d).to_csv(OUT / "04_brain_features/reproduction_vs_lab.tsv", sep="\t", float_format="%.5f")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["roi", "stimulus", "sub", "unit", "summarize"])
    ap.add_argument("--sub"); ap.add_argument("--unit")
    a = ap.parse_args()
    if a.step == "roi":
        for s in (a.sub.split(",") if a.sub else ["01", "02", "03", "04", "05"]):
            make_roi(s)
    elif a.step == "stimulus":
        cl.run_stimulus()
    elif a.step == "sub":
        cl.run_subject(a.sub)
    elif a.step == "unit":
        run_unit(a.sub, a.unit)
    else:
        collect_units(); cl.summarize(); reproduction_check()
