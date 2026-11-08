"""Sweep clustering algos x K x source. exploratory, standalone.

For each (source, algo, K) it stores per-stim cluster id as
  results/clustering/<source>/<algo>_K<K>/labels.csv  with columns (stim_idx, cluster_id)

Default sources. video.{vjepa2,clip} + brain.{roi_mean,brain_jepa,swift}
Default algos.   kmeans, agglomerative_ward, gmm, hdbscan
Default K.       2 3 5 6 10 15 20 34 50    (hdbscan ignores K)

CPU only. Total ~140 settings * a few seconds.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from part1_embedding_load.load_embeddings import REPO, load

DEFAULT_SOURCES = [
    "video.vjepa2", "video.clip",
    "brain.roi_mean", "brain.brain_jepa", "brain.swift",
]
DEFAULT_ALGOS = ["kmeans", "agglomerative_ward", "gmm", "hdbscan"]
DEFAULT_KS = list(range(2, 51))   # 2..50 all (Horikawa best ~24 included)

OUT_ROOT = REPO / "project" / "shared" / "studies" / "source_clustering" / "results"


def preprocess(x: np.ndarray, max_dim: int = 128) -> np.ndarray:
    """Standardize. If D very large, PCA down to max_dim for clustering stability + speed."""
    x = StandardScaler().fit_transform(x)
    if x.shape[1] > max_dim:
        x = PCA(n_components=max_dim, random_state=0).fit_transform(x)
    return x


def fit_kmeans(x: np.ndarray, k: int) -> np.ndarray:
    return KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(x)


def fit_agglomerative_ward(x: np.ndarray, k: int) -> np.ndarray:
    return AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(x)


def fit_gmm(x: np.ndarray, k: int) -> np.ndarray:
    return GaussianMixture(n_components=k, covariance_type="diag", random_state=0).fit_predict(x)


def fit_hdbscan(x: np.ndarray, _k_ignored: int) -> np.ndarray:
    try:
        from sklearn.cluster import HDBSCAN
    except ImportError:
        import hdbscan
        return hdbscan.HDBSCAN(min_cluster_size=20).fit_predict(x)
    return HDBSCAN(min_cluster_size=20).fit_predict(x)


ALGO_DISPATCH = {
    "kmeans": fit_kmeans,
    "agglomerative_ward": fit_agglomerative_ward,
    "gmm": fit_gmm,
    "hdbscan": fit_hdbscan,
}


def run_one(source: str, algo: str, k: int, x_pre: np.ndarray) -> tuple[np.ndarray, Path]:
    labels = ALGO_DISPATCH[algo](x_pre, k)
    out_dir = OUT_ROOT / source / (f"{algo}_K{k}" if algo != "hdbscan" else "hdbscan_auto")
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"stim_idx": np.arange(len(labels)), "cluster_id": labels}).to_csv(
        out_dir / "labels.csv", index=False
    )
    return labels, out_dir


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sources", nargs="+", default=DEFAULT_SOURCES)
    p.add_argument("--algos", nargs="+", default=DEFAULT_ALGOS)
    p.add_argument("--ks", nargs="+", type=int, default=DEFAULT_KS)
    args = p.parse_args()

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for src in args.sources:
        x = load(src)
        x_pre = preprocess(x)
        print(f"[sweep] {src}: input {x.shape} -> preprocessed {x_pre.shape}", flush=True)
        for algo in args.algos:
            ks = [-1] if algo == "hdbscan" else args.ks
            for k in ks:
                labels, out_dir = run_one(src, algo, k, x_pre)
                n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
                noise = int((labels == -1).sum())
                tag = "auto" if algo == "hdbscan" else f"K{k}"
                print(f"  {algo}_{tag}: n_clusters={n_clusters} noise={noise} -> {out_dir.name}", flush=True)
    print(f"[sweep] done. results under {OUT_ROOT}")


if __name__ == "__main__":
    main()
