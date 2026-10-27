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
    ap.add_argument("step", choices=["roi", "stimulus", "sub", "summarize"])
    ap.add_argument("--sub")
    a = ap.parse_args()
    if a.step == "roi":
        for s in (a.sub.split(",") if a.sub else ["01", "02", "03", "04", "05"]):
            make_roi(s)
    elif a.step == "stimulus":
        cl.run_stimulus()
    elif a.step == "sub":
        cl.run_subject(a.sub)
    else:
        cl.summarize(); reproduction_check()
