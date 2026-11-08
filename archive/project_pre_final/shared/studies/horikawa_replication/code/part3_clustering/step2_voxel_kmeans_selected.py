"""part3 step2. Voxel-level k-means K=15/27/50 per subject, USING ONLY SELECTED VOXELS.

Same procedure as step1_voxel_kmeans_correlation but restricts voxel pool to part2 step1 의 selected_idx.
This is the paper-faithful version (Horikawa et al. 2020 Fig 6 used encoding-significant voxels).

step1 (whole-brain) vs step2 (selected voxel) 두 결과를 모두 갖고, part4 에서 양쪽 metric 비교.

Input.
  results/voxel_patterns/sub-XX.npy            (from part1 step1)  shape (2185, N_voxel_all)
  results/voxel_selection/sub-XX_selected_idx.npy   (from part2 step1)  1-D int

Output.
  results/per_subject/voxel_selected__sub-XX/kmeans_K{15,27,50}/labels.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, normalize

REPO = Path("/pscratch/sd/s/sjmoon/EmoBrain")
OUT_ROOT = REPO / "project" / "shared" / "studies" / "horikawa_replication" / "results"

VOXEL_DIR = OUT_ROOT / "voxel_patterns"
SEL_DIR = OUT_ROOT / "voxel_selection"
PS_ROOT = OUT_ROOT / "per_subject"


def preprocess_for_corr(x: np.ndarray, n_pca: int = 256) -> np.ndarray:
    x = StandardScaler().fit_transform(x)
    if x.shape[1] > n_pca:
        x = PCA(n_components=n_pca, random_state=0).fit_transform(x)
    x = normalize(x, norm="l2", axis=1)
    return x


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--subjects", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    p.add_argument("--ks", nargs="+", type=int, default=[15, 27, 50])
    args = p.parse_args()
    PS_ROOT.mkdir(parents=True, exist_ok=True)
    for subj in args.subjects:
        vox_path = VOXEL_DIR / f"sub-{subj:02d}.npy"
        sel_path = SEL_DIR / f"sub-{subj:02d}_selected_idx.npy"
        if not vox_path.exists():
            print(f"[selected-cluster] sub-{subj:02d} missing voxel_patterns {vox_path}, skip", flush=True)
            continue
        if not sel_path.exists():
            print(f"[selected-cluster] sub-{subj:02d} missing selected_idx {sel_path} (run part2 step1 first), skip", flush=True)
            continue
        x_all = np.load(vox_path).astype(np.float32)
        sel = np.load(sel_path).astype(np.int64)
        x = x_all[:, sel]
        x_pre = preprocess_for_corr(x)
        tag = f"voxel_selected__sub-{subj:02d}"
        print(f"[selected-cluster] {tag}: voxel_all={x_all.shape} -> selected={x.shape} -> pre={x_pre.shape}", flush=True)
        for k in args.ks:
            lab = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(x_pre)
            out_dir = PS_ROOT / tag / f"kmeans_K{k}"
            out_dir.mkdir(parents=True, exist_ok=True)
            pd.DataFrame({"stim_idx": np.arange(len(lab)), "cluster_id": lab}).to_csv(
                out_dir / "labels.csv", index=False)
            print(f"  kmeans_K{k}: n_clusters={len(set(lab))} -> {out_dir.name}", flush=True)
    print(f"[selected-cluster] done. labels under {PS_ROOT}/voxel_selected__*/")


if __name__ == "__main__":
    main()
