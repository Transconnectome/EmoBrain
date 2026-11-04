#!/usr/bin/env python3
"""S1: 원 논문 ROI가 우리 T1w에서 해부학적으로 제자리에 있는지와, Talairach Daemon 두 판 중 어느 쪽과 맞는지 본다 (2026-11-04).

1) 정렬: 참가자마다 FreeSurfer aseg(우리 v3, v2의 T1w_aseg_raw)와 원 논문 ROI를 비교한다.
   각 축 ±2 voxel로 원 ROI를 옮겨 가며 Dice를 내고, 안 옮겼을 때가 가장 좋은지 본다. 피질은 HCP 360개 합집합과 aseg 피질로 본다.
   큰 어긋남은 z축만 −40~+40 mm(2 mm 간격)로 따로 찾는다.
   이동 규칙: 원 ROI의 ijk(격자 밖 voxel 포함)에 이동량을 더하고 격자 안에 드는 voxel만 센다. 경계에서 감기지 않는다. Dice 분모 = 이동 뒤 격자 안 ROI voxel + aseg voxel.
2) 판 비교: HK 5명에서 PickAtlas의 두 판(MNI_atlas_templates, TD-ICBM_MNI_atlas_templates)을 fMRIPrep의 MNI → T1w 변환으로 옮겨(s1_original_roi_align.sh가 ANTs로 만듦)
   원 논문 ROI와 Dice를 비교한다. 원 논문은 SPM 변환을 썼으므로 값 자체가 아니라 두 판의 차이만 본다.
   전제와 한계: PickAtlas의 SPM MNI 공간을 MNI152NLin2009cAsym과 같다고 놓았다. 그 차이를 재지 않았으므로 판을 알아보는 단서일 뿐이고 저자가 쓴 판의 증명이 아니다.
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


def shifted_dice(points, ref, shift):
    """points(n×3 ijk, 격자 밖 포함)를 shift만큼 옮겨 격자 안에 드는 voxel로 Dice를 낸다. 감기지 않는다."""
    q = points + np.asarray(shift)
    q = q[((q >= 0) & (q < np.array(ref.shape))).all(1)]
    return 2 * float(ref[tuple(q.T)].sum()) / max(1, len(q) + int(ref.sum()))


def best_shift(points, ref):
    best = (-1.0, (0, 0, 0))
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            for dz in range(-2, 3):
                d = shifted_dice(points, ref, (dx, dy, dz))
                if d > best[0] or (d == best[0] and (dx, dy, dz) == (0, 0, 0)):
                    best = (d, (dx, dy, dz))
    return best


def best_z(points, ref):
    """z축만 −40~+40 mm(2 mm 간격)로 찾는다. 돌려주는 값은 (Dice, mm)."""
    return max(((shifted_dice(points, ref, (0, 0, k)), 2 * k) for k in range(-20, 21)), key=lambda x: x[0])


def alignment():
    rows = []
    for cohort, (root, ver, subs) in COHORT.items():
        for s in subs.split():
            ijk, M, names, m = load(cohort, s)
            aseg = on_grid(nib.load(PM / root / f"sub-{s}/{ver}/atlas/T1w_aseg_raw.nii.gz"), m)
            for roi, labs in ASEG.items():
                f = M[:, names.index(roi)]
                v = volume(ijk, f, m.shape)
                ref = np.isin(aseg, labs)
                b, z = best_shift(ijk[f].astype(int), ref), best_z(ijk[f].astype(int), ref)
                rows.append(dict(cohort=cohort, participant=f"sub-{s}", roi=roi, n_orig_total=int(f.sum()), n_orig=int(v.sum()), n_aseg=int(ref.sum()), dice_no_shift=round(dice(v, ref), 3), dice_best=round(b[0], 3), best_shift=str(b[1]), dice_best_z=round(z[0], 3), best_z_mm=z[1]))
            cx = np.array([n.startswith("hcp180") for n in names])
            f = M[:, cx].any(1)
            v = volume(ijk, f, m.shape)
            ref = np.isin(aseg, [3, 42])
            b, z = best_shift(ijk[f].astype(int), ref), best_z(ijk[f].astype(int), ref)
            rows.append(dict(cohort=cohort, participant=f"sub-{s}", roi="cortex(HCP 360 합집합)", n_orig_total=int(f.sum()), n_orig=int(v.sum()), n_aseg=int(ref.sum()), dice_no_shift=round(dice(v, ref), 3), dice_best=round(b[0], 3), best_shift=str(b[1]), dice_best_z=round(z[0], 3), best_z_mm=z[1]))
            print(cohort, s, flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(MAN / "original_roi_alignment.tsv", sep="\t", index=False)
    print(t.groupby("roi")[["dice_no_shift", "dice_best"]].mean().round(3).to_string())
    print("no-shift best:", int((t.best_shift == "(0, 0, 0)").sum()), "of", len(t))
    print(t[(t.cohort == "hk") & (t.participant == "sub-03")].to_string(index=False))
    print("largest |best_z_mm| excluding HK sub-03 (subcortex):")
    o = t[~((t.cohort == "hk") & (t.participant == "sub-03")) & ~t.roi.str.startswith("cortex")]
    print(o.reindex(o.best_z_mm.abs().sort_values(ascending=False).index).head(8).to_string(index=False))


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
