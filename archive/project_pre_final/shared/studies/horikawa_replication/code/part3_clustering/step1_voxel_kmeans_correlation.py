"""Stage C step 2. Per-subject voxel-level clustering (Horikawa paper style).

Input. results/clustering/voxel_patterns/sub-XX.npy  shape (N_stim, N_voxel)
Procedure (paper-faithful).
  - per subject: standardize voxel
  - PCA -> 256 dim (voxel count too large for direct k-means at correlation distance)
  - convert to unit-norm vectors so that L2 distance == sqrt(2*(1-cos sim)) == correlation distance proxy
  - k-means K = 15, 27, 50

Output. results/clustering/per_subject/voxel__sub-XX/<algo>_K<K>/labels.csv
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
PS_ROOT = OUT_ROOT / "per_subject"


def preprocess_for_corr(x: np.ndarray, n_pca: int = 256) -> np.ndarray:
    x = StandardScaler().fit_transform(x)
    if x.shape[1] > n_pca:
        x = PCA(n_components=n_pca, random_state=0).fit_transform(x)
    x = normalize(x, norm="l2", axis=1)   # cosine == correlation up to mean centering
    return x


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--subjects", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    p.add_argument("--ks", nargs="+", type=int, default=[15, 27, 50])
    args = p.parse_args()
    PS_ROOT.mkdir(parents=True, exist_ok=True)
    for subj in args.subjects:
        in_path = VOXEL_DIR / f"sub-{subj:02d}.npy"
        if not in_path.exists():
            print(f"[voxel-cluster] sub-{subj:02d} missing voxel npy, skip")
            continue
        x = np.load(in_path)
        x_pre = preprocess_for_corr(x)
        tag = f"voxel__sub-{subj:02d}"
        print(f"[voxel-cluster] {tag}: {x.shape} -> {x_pre.shape}", flush=True)
        for k in args.ks:
            lab = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(x_pre)
            out_dir = PS_ROOT / tag / f"kmeans_K{k}"
            out_dir.mkdir(parents=True, exist_ok=True)
            pd.DataFrame({"stim_idx": np.arange(len(lab)), "cluster_id": lab}).to_csv(
                out_dir / "labels.csv", index=False)
            print(f"  kmeans_K{k}: n_clusters={len(set(lab))} -> {out_dir.name}", flush=True)
    print(f"[voxel-cluster] done. labels under {PS_ROOT}/voxel__*/")


if __name__ == "__main__":
    main()
