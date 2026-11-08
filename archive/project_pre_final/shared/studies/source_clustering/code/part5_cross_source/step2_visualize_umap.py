"""UMAP visualization per source.

5 coloring 모두 그림.
  cowen_top1     Cowen cat34 의 argmax (discrete 34 색)
  cowen_top2     argmax 제외 후 second max (discrete 34 색)
  cowen_entropy  Cowen 34 soft distribution 의 entropy (continuous, "mixed vs dominant")
  valence        Horikawa valence_score (continuous)
  arousal        Horikawa arousal_score (continuous)

cluster setting (kmeans / agglomerative / gmm × K) 도 함께 그림.
  default. kmeans 의 핵심 K 만 (K=2,6,10,20,24,34,50). 전체 K 다 그리면 figure 양이 너무 많음.

Output. results/clustering/figures/<source>/<coloring_or_setting>.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from part2_kmeans_sweep.step1_pooled_sweep import OUT_ROOT, preprocess
from part1_embedding_load.load_embeddings import load, load_cowen_labels

FIG_ROOT = OUT_ROOT / "figures"


def umap_embed(x: np.ndarray, n_neighbors: int = 15) -> np.ndarray:
    try:
        import umap
        return umap.UMAP(n_neighbors=n_neighbors, min_dist=0.1, n_components=2, random_state=0).fit_transform(x)
    except ImportError:
        from sklearn.manifold import TSNE
        return TSNE(n_components=2, perplexity=30, random_state=0).fit_transform(x)


def scatter_discrete(coords, labels, title, out_path, cmap="tab20"):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(coords[:, 0], coords[:, 1], c=labels, cmap=cmap, s=5, alpha=0.75)
    ax.set_title(title, fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def scatter_continuous(coords, values, title, out_path, cmap="viridis"):
    fig, ax = plt.subplots(figsize=(6.4, 6))
    sc = ax.scatter(coords[:, 0], coords[:, 1], c=values, cmap=cmap, s=5, alpha=0.8)
    ax.set_title(title, fontsize=10)
    ax.set_xticks([]); ax.set_yticks([])
    plt.colorbar(sc, ax=ax, fraction=0.04, pad=0.02)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sources", nargs="+", default=[
        "video.vjepa2", "video.clip",
        "brain.roi_mean", "brain.brain_jepa", "brain.swift",
    ])
    p.add_argument("--ks-for-cluster-fig", nargs="+", type=int,
                   default=[2, 6, 10, 20, 24, 34, 50])
    p.add_argument("--algos-for-cluster-fig", nargs="+",
                   default=["kmeans"])
    args = p.parse_args()

    cowen = load_cowen_labels()
    for src in args.sources:
        x = load(src)
        x_pre = preprocess(x)
        coords = umap_embed(x_pre)
        sd = FIG_ROOT / src
        sd.mkdir(parents=True, exist_ok=True)
        scatter_discrete(coords, cowen["cat34_top1"], f"{src} | Cowen cat34 top1",
                         sd / "color_cowen_top1.png", cmap="tab20")
        scatter_discrete(coords, cowen["cat34_top2"], f"{src} | Cowen cat34 top2",
                         sd / "color_cowen_top2.png", cmap="tab20")
        scatter_continuous(coords, cowen["cat34_entropy"], f"{src} | Cowen entropy (high = mixed)",
                           sd / "color_cowen_entropy.png", cmap="magma")
        scatter_continuous(coords, cowen["valence"], f"{src} | valence_score",
                           sd / "color_valence.png", cmap="coolwarm")
        scatter_continuous(coords, cowen["arousal"], f"{src} | arousal_score",
                           sd / "color_arousal.png", cmap="plasma")
        print(f"[viz] {src}: 5 coloring done", flush=True)
        for algo in args.algos_for_cluster_fig:
            for k in args.ks_for_cluster_fig:
                setting = f"{algo}_K{k}"
                lab_path = OUT_ROOT / src / setting / "labels.csv"
                if not lab_path.exists():
                    continue
                lab = pd.read_csv(lab_path)["cluster_id"].to_numpy()
                scatter_discrete(coords, lab, f"{src} | {setting}",
                                 sd / f"cluster_{setting}.png", cmap="tab20")
            print(f"[viz] {src} {algo}: cluster figs at K={args.ks_for_cluster_fig}", flush=True)
    print(f"[viz] done. per-source figures under {FIG_ROOT}/<source>/")


if __name__ == "__main__":
    main()
