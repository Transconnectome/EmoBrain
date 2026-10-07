"""Preprocessing census q0. Atlas on the fMRI grid.

Scientific question
-------------------
Which voxels did the existing pipeline assign to each of the 450 parcels, and
how far apart are the atlas space and the fMRI space?

What this excludes
------------------
If the ROI values in the CSVs cannot be reproduced from a known label volume,
every later check of the ROI stage is uninterpretable. The label volume is
rebuilt here by nearest-neighbour lookup through the two affines, which is
what nilearn.resample_to_img(interpolation='nearest') does. Whether it matches
the pipeline exactly is decided in q2 by reproducing the CSV values.

Outputs
-------
qc/atlas/schaefer_on_fmri_grid.npy   int16 (97,115,97), 0 = no label
qc/atlas/tian_on_fmri_grid.npy       int16 (97,115,97)
qc/atlas/atlas_grid.json             affines, offsets, per-label voxel counts
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nibabel as nib  # noqa: E402
import numpy as np  # noqa: E402

from _assets import provenance, sha256_file, write_json  # noqa: E402
from _qc import GRID_SHAPE, QC_ATLAS, SCHAEFER, STEP7, TIAN  # noqa: E402

SCRIPT = "prereg_v2/code/q0_atlas_grid.py"


def nearest_on_grid(atlas_img, target_affine, target_shape):
    """Label of the atlas voxel nearest to each target voxel centre."""
    ii, jj, kk = np.meshgrid(*[np.arange(n) for n in target_shape], indexing="ij")
    vox = np.stack([ii, jj, kk, np.ones_like(ii)], -1).reshape(-1, 4).T
    world = target_affine @ vox
    avox = np.linalg.inv(atlas_img.affine) @ world
    frac = avox[:3] - np.floor(avox[:3])
    idx = np.round(avox[:3]).astype(int)
    data = np.asarray(atlas_img.dataobj)
    ok = np.all((idx >= 0) & (idx < np.array(data.shape)[:, None]), axis=0)
    out = np.zeros(idx.shape[1], dtype=np.int16)
    out[ok] = np.round(data[idx[0, ok], idx[1, ok], idx[2, ok]]).astype(np.int16)
    return out.reshape(target_shape), frac


def main() -> None:
    ref_path = STEP7 / "sub-01" / "sub-01_stimulus-2017.nii.gz"
    ref = nib.load(ref_path)
    prov = provenance(SCRIPT, {"reference_fmri": str(ref_path)})
    assert ref.shape[:3] == GRID_SHAPE

    out = {"provenance": prov,
           "fmri_affine": ref.affine.tolist(),
           "fmri_shape": list(ref.shape[:3]),
           "fmri_qform_code": int(ref.header["qform_code"]),
           "fmri_sform_code": int(ref.header["sform_code"])}
    QC_ATLAS.mkdir(parents=True, exist_ok=True)
    for name, path in [("schaefer", SCHAEFER), ("tian", TIAN)]:
        a = nib.load(path)
        lab, frac = nearest_on_grid(a, ref.affine, GRID_SHAPE)
        orig = np.round(np.asarray(a.dataobj)).astype(int)
        n_lab = int(orig.max())
        cnt_orig = np.bincount(orig.ravel(), minlength=n_lab + 1)[1:]
        cnt_grid = np.bincount(lab.ravel().astype(int), minlength=n_lab + 1)[1:]
        np.save(QC_ATLAS / f"{name}_on_fmri_grid.npy", lab)
        # distance of each target centre from the nearest atlas centre, in voxels
        off = np.abs(frac - np.round(frac))
        out[name] = {
            "path": str(path), "sha256": sha256_file(path),
            "atlas_shape": list(a.shape[:3]), "atlas_affine": a.affine.tolist(),
            "n_labels": n_lab,
            "labels_lost_on_fmri_grid": [int(i + 1) for i in np.where(cnt_grid == 0)[0]],
            "voxels_per_label_on_fmri_grid_min": int(cnt_grid.min()),
            "voxels_per_label_on_fmri_grid_median": float(np.median(cnt_grid)),
            "voxels_per_label_on_fmri_grid_max": int(cnt_grid.max()),
            "voxels_per_label_orig": cnt_orig.tolist(),
            "voxels_per_label_on_fmri_grid": cnt_grid.tolist(),
            "subvoxel_offset_between_grids_vox": np.unique(np.round(off, 4), axis=1).tolist()
            if off.size < 10 else [float(off[d].max()) for d in range(3)],
        }
        print(f"  {name}: {n_lab} labels, lost {len(out[name]['labels_lost_on_fmri_grid'])}, "
              f"voxels/label {cnt_grid.min()}..{cnt_grid.max()}, "
              f"max offset per axis {out[name]['subvoxel_offset_between_grids_vox']}")
    s = np.load(QC_ATLAS / "schaefer_on_fmri_grid.npy")
    t = np.load(QC_ATLAS / "tian_on_fmri_grid.npy")
    out["n_voxels_in_both_schaefer_and_tian"] = int(((s > 0) & (t > 0)).sum())
    out["space_note"] = (
        "The atlases are FSL MNI152 (MNI152NLin6Asym) 2 mm, 91x109x91, stored "
        "left-right flipped. The fMRI grid is 97x115x97 with origin "
        "(-96.5,-132.5,-78.5), the size of the fMRIPrep MNI152NLin2009cAsym 2 mm "
        "grid but offset by half a voxel from its usual origin (-96,-132,-78). "
        "Nearest-neighbour lookup through the affines assumes both are the same "
        "world space. If the fMRI is in MNI152NLin2009cAsym, the two templates "
        "differ by a few millimetres, and no file here states which template "
        "the fMRI was normalised to.")
    print(f"  voxels labelled by both atlases: {out['n_voxels_in_both_schaefer_and_tian']}")
    write_json(QC_ATLAS / "atlas_grid.json", out)


if __name__ == "__main__":
    main()
