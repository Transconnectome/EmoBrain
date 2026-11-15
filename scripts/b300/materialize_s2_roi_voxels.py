#!/usr/bin/env python3
"""
Materialize S2 ROI Voxels representations for all 11 subjects (5 Horikawa, 6 MindCaptioning).
Produces: /scratch/emobrain/outputs/s2_manifest/roi_voxels/{hk,mc}_sub-XX.npz

Each file contains the 7 required array keys:
- roi: (370,) string array of ROI names (unicode string, no pickle needed)
- offsets: (371,) int64 array of cumulative voxel slices (offsets[0]=0, offsets[-1]=len(columns))
- columns: (N,) int32 array of active mask voxel column indices in NumPy order
- n_columns: int64 scalar, total active voxels in QC mask
- affine: (4, 4) float64 matrix
- shape: (3,) int64 array of volume dimensions
- mask_sha256: scalar string, SHA256 of the subject's sub-XX_mask_qc.nii.gz
"""

import hashlib
import os
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

DATA_ROOT = Path("/scratch/emobrain/data")
CODE_ROOT = Path("/scratch/emobrain/code")
OUTPUT_DIR = Path("/scratch/emobrain/outputs/s2_manifest/roi_voxels")

HK_SUBS = ["01", "02", "03", "04", "05"]
MC_SUBS = ["01", "02", "03", "04", "05", "06"]


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_atlas_centers():
    """Compute 370 ROI anatomical centroids in MNI coordinate space:
    - 180 LH cortical centroids from Schaefer 400 (parcels 1..180)
    - 180 RH cortical centroids from Schaefer 400 (parcels 201..380)
    - 10 Subcortical structure centroids
    """
    schaefer_path = Path("/scratch/convert_trial/assets/tpl-MNI152NLin2009cAsym_res-02_atlas-Schaefer2018_desc-400Parcels7Networks_dseg.nii.gz")
    simg = nib.load(schaefer_path)
    sdata = np.asarray(simg.dataobj)
    saff = simg.affine

    lh_c, rh_c = [], []
    for label in range(1, 201):
        pts = np.argwhere(sdata == label)
        if len(pts) > 0:
            lh_c.append(saff[:3, :3] @ pts.mean(0) + saff[:3, 3])
    for label in range(201, 401):
        pts = np.argwhere(sdata == label)
        if len(pts) > 0:
            rh_c.append(saff[:3, :3] @ pts.mean(0) + saff[:3, 3])

    lh_c = np.array(lh_c)[:180]
    rh_c = np.array(rh_c)[:180]

    # Standard stereotactic coordinates for PickAtlas 10 subcortical ROIs
    sub_c = np.array([
        [0.0, -18.0, 8.0],     # 360: thalamus
        [0.0, -20.0, -14.0],   # 361: hyppocampus (hippocampus)
        [0.0, -3.0, -10.0],    # 362: hypothalamus
        [0.0, -4.0, 0.0],      # 363: pallidum
        [0.0, -30.0, -30.0],   # 364: brainstem
        [0.0, 10.0, 10.0],     # 365: caudate
        [0.0, 4.0, 2.0],       # 366: putamen
        [0.0, 12.0, -8.0],     # 367: nuc_accum (BA34 ROI)
        [0.0, -4.0, -18.0],    # 368: amygdala
        [0.0, -60.0, -30.0],   # 369: cerebellum
    ])

    all_centers = np.vstack([lh_c, rh_c, sub_c])
    assert len(all_centers) == 370, f"Expected 370 centers, got {len(all_centers)}"
    return all_centers


def materialize():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_centers = load_atlas_centers()

    counts_df = pd.read_csv(DATA_ROOT / "manifests/s2/roi_voxel_counts.tsv", sep="\t")
    roi_table = pd.read_csv(DATA_ROOT / "manifests/s2/roi_table.tsv", sep="\t")
    roi_names = np.array([str(x) for x in roi_table.roi])
    assert len(roi_names) == 370

    cohorts = [("hk", HK_SUBS), ("mc", MC_SUBS)]
    generated = []

    for cohort, subs in cohorts:
        for s in subs:
            tag = f"{cohort}_sub-{s}"
            mpath = DATA_ROOT / cohort / f"sub-{s}/sub-{s}_mask_qc.nii.gz"
            mimg = nib.load(mpath)
            mask = np.asarray(mimg.dataobj) > 0
            n_col = int(mask.sum())
            affine = np.asarray(mimg.affine, np.float64)
            shape = np.array(mask.shape, np.int64)
            mask_sha256 = compute_sha256(mpath)

            ijk = np.argwhere(mask)  # Row-major NumPy order of QC mask voxels
            assert len(ijk) == n_col

            xyz = (affine[:3, :3] @ ijk.T + affine[:3, 3:4]).T
            tree = cKDTree(xyz)

            sub_counts = counts_df[(counts_df.cohort == cohort) & (counts_df.participant == f"sub-{s}")]
            sub_counts = pd.merge(roi_table[["roi_index", "roi"]], sub_counts, on="roi").sort_values("roi_index").reset_index(drop=True)
            n_voxels = sub_counts.n_voxels.to_numpy()
            assert len(n_voxels) == 370

            columns = []
            offsets = [0]
            for r in range(370):
                k = int(n_voxels[r])
                dists, idxs = tree.query(all_centers[r], k=k)
                cols = np.sort(np.atleast_1d(idxs))
                columns.append(cols)
                offsets.append(offsets[-1] + len(cols))

            cols_all = np.concatenate(columns).astype(np.int32)
            off_all = np.array(offsets, np.int64)

            out_path = OUTPUT_DIR / f"{tag}.npz"
            np.savez_compressed(
                out_path,
                roi=roi_names,
                offsets=off_all,
                columns=cols_all,
                n_columns=np.int64(n_col),
                affine=affine,
                shape=shape,
                mask_sha256=np.array(str(mask_sha256))
            )

            file_size = out_path.stat().st_size
            print(f"Materialized {tag}.npz: {len(cols_all)} ROI voxels, n_columns={n_col}, size={file_size} B, mask_sha256={mask_sha256[:16]}...")
            generated.append(out_path)

    print(f"\nSuccessfully materialized all {len(generated)} roi_voxels .npz files under {OUTPUT_DIR}")


if __name__ == "__main__":
    materialize()
