#!/usr/bin/env python3
"""S1: 원 논문 ROI가 우리 T1w에서 해부학적으로 제자리에 있는지와, Talairach Daemon 두 판 중 어느 쪽과 맞는지 본다 (2026-11-04).

1) 정렬: 참가자마다 FreeSurfer aseg(우리 v3, v2의 T1w_aseg_raw)와 원 논문 ROI를 비교한다.
   각 축 ±2 voxel로 원 ROI를 옮겨 가며 Dice를 내고, 안 옮겼을 때가 가장 좋은지 본다. 피질은 HCP 360개 합집합이 aseg 피질에 드는 비율로 본다.
2) 판 비교: HK 5명에서 PickAtlas의 두 판(MNI_atlas_templates, TD-ICBM_MNI_atlas_templates)을 fMRIPrep의 MNI → T1w 변환으로 옮겨(s1_original_roi_align.sh가 ANTs로 만듦)
   원 논문 ROI와 Dice를 비교한다. 원 논문은 SPM 변환을 썼으므로 값 자체가 아니라 두 판의 차이만 본다.
입력: project/output/final_2026-11/s1_original_rois/*_rois.npz
출력: manifests/original_roi_alignment.tsv, manifests/td_version_check.tsv
"""
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd

PM = Path("/pscratch/sd/s/sjmoon")
REPO = PM / "EmoBrain"
OUT = REPO / "project/output/final_2026-11/s1_original_rois"
MAN = REPO / "project/analysis/final_2026-11/manifests"
COHORT = {"hk": ("Horikawa", "v3", "01 02 03 04 05"), "mc": ("MindCaptioning", "v2", "01 02 03 04 05 06")}
ASEG = {"hyppocampus": [17, 53], "thalamus": [10, 49], "amygdala": [18, 54], "caudate": [11, 50], "putamen": [12, 51], "pallidum": [13, 52], "brainstem": [16], "cerebellum": [7, 8, 46, 47]}
TD = {"hypothalamus": ("TD_brodmann", [105]), "putamen": ("TD_brodmann", [110]), "nuc_accum": ("TD_brodmann", [34]), "brainstem": ("TD_hemisphere", [3, 4]), "cerebellum": ("TD_hemisphere", [1, 2]), "caudate": ("TD_label", [36])}


def dice(a, b):
    return float(2 * (a & b).sum() / max(1, a.sum() + b.sum()))


def load(cohort, s):
    root, ver, _ = COHORT[cohort]
    z = np.load(OUT / f"{cohort}_sub-{s}_rois.npz")
    m = nib.load(PM / root / f"sub-{s}/{ver}_qc/sub-{s}_mask_qc.nii.gz")
    return z["ijk"], z["member"], [str(x) for x in z["roi"]], m


def volume(ijk, flag, shape):
    v = np.zeros(shape, bool)
    i = ijk[flag]
    keep = ((i >= 0) & (i < np.array(shape))).all(1)
    v[tuple(i[keep].T)] = True
    return v


def on_grid(img, m):
    """다른 격자의 라벨 영상을 mask 격자로 최근접 이웃으로 옮긴다."""
    ii = np.indices(m.shape).reshape(3, -1).T
    w = nib.affines.apply_affine(m.affine, ii)
    j = np.round(nib.affines.apply_affine(np.linalg.inv(img.affine), w)).astype(int)
    ok = ((j >= 0) & (j < np.array(img.shape[:3]))).all(1)
    a = np.asarray(img.dataobj)
    o = np.zeros(len(ii), a.dtype)
    o[ok] = a[tuple(j[ok].T)]
    return o.reshape(m.shape)


def best_shift(v, ref):
    best = (-1.0, (0, 0, 0))
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            for dz in range(-2, 3):
                d = dice(np.roll(v, (dx, dy, dz), (0, 1, 2)), ref)
                if d > best[0]:
                    best = (d, (dx, dy, dz))
    return best


def alignment():
    rows = []
    for cohort, (root, ver, subs) in COHORT.items():
        for s in subs.split():
            ijk, M, names, m = load(cohort, s)
            aseg = on_grid(nib.load(PM / root / f"sub-{s}/{ver}/atlas/T1w_aseg_raw.nii.gz"), m)
            for roi, labs in ASEG.items():
                v = volume(ijk, M[:, names.index(roi)], m.shape)
                ref = np.isin(aseg, labs)
                b = best_shift(v, ref)
                rows.append(dict(cohort=cohort, participant=f"sub-{s}", roi=roi, n_orig=int(v.sum()), n_aseg=int(ref.sum()), dice_no_shift=round(dice(v, ref), 3), dice_best=round(b[0], 3), best_shift=str(b[1])))
            cx = np.array([n.startswith("hcp180") for n in names])
            v = volume(ijk, M[:, cx].any(1), m.shape)
            ref = np.isin(aseg, [3, 42])
            b = best_shift(v, ref)
            rows.append(dict(cohort=cohort, participant=f"sub-{s}", roi="cortex(HCP 360 합집합)", n_orig=int(v.sum()), n_aseg=int(ref.sum()), dice_no_shift=round(dice(v, ref), 3), dice_best=round(b[0], 3), best_shift=str(b[1])))
            print(cohort, s, flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(MAN / "original_roi_alignment.tsv", sep="\t", index=False)
    print(t.groupby("roi")[["dice_no_shift", "dice_best"]].mean().round(3).to_string())
    print("no-shift best:", int((t.best_shift == "(0, 0, 0)").sum()), "of", len(t))
    print(t[t.best_shift != "(0, 0, 0)"].to_string(index=False))


def td_versions(tmp):
    rows = []
    for s in COHORT["hk"][2].split():
        ijk, M, names, m = load("hk", s)
        for roi, (file, labs) in TD.items():
            v = volume(ijk, M[:, names.index(roi)], m.shape)
            rec = dict(participant=f"sub-{s}", roi=roi, n_orig=int(v.sum()))
            for tag in ["MNI_atlas_templates", "TD-ICBM_MNI_atlas_templates"]:
                w = np.isin(np.asarray(nib.load(tmp / f"sub-{s}_{tag}_{file}.nii.gz").dataobj), labs)
                rec[f"dice_{tag}"] = round(dice(v, w), 3)
            rows.append(rec)
    t = pd.DataFrame(rows)
    t.to_csv(MAN / "td_version_check.tsv", sep="\t", index=False)
    print(t.groupby("roi")[["n_orig", "dice_MNI_atlas_templates", "dice_TD-ICBM_MNI_atlas_templates"]].mean().round(3).to_string())
    d = t["dice_MNI_atlas_templates"] - t["dice_TD-ICBM_MNI_atlas_templates"]
    print("MNI_atlas_templates higher in", int((d > 0).sum()), "of", len(t))


if __name__ == "__main__":
    if sys.argv[1] == "alignment":
        alignment()
    else:
        td_versions(Path(sys.argv[2]))
