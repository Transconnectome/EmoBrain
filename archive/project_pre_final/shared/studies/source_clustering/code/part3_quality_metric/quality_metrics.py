"""Cluster quality + emotion alignment.

For each (source, algo, K) under results/clustering/<source>/<algo_K>/labels.csv:
  - silhouette_score on the preprocessed embedding (skip if N>5000 to keep fast)
  - davies_bouldin_score
  - calinski_harabasz_score
  - NMI vs Cowen cat34_top1   (emotion-meaning indicator)
  - ARI vs Cowen cat34_top1
  - mean cluster-internal V/A spread (small = cluster is emotion-coherent)

Output. results/clustering/quality_summary.csv with one row per setting.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    adjusted_rand_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    normalized_mutual_info_score,
    silhouette_score,
)

from part2_kmeans_sweep.step1_pooled_sweep import OUT_ROOT, preprocess
from part1_embedding_load.load_embeddings import ALL_SOURCES, load, load_cowen_labels


def cluster_va_spread(labels: np.ndarray, va: np.ndarray) -> float:
    """Mean within-cluster std of V/A across clusters. Lower = more emotion-coherent."""
    spreads = []
    for k in np.unique(labels):
        if k == -1 or (labels == k).sum() < 2:
            continue
        spreads.append(va[labels == k].std(axis=0).mean())
    return float(np.mean(spreads)) if spreads else float("nan")


def quality_one(x_pre: np.ndarray, labels: np.ndarray, cowen_top1: np.ndarray, va: np.ndarray) -> dict:
    valid = labels != -1
    n_unique = len(set(labels[valid])) if valid.any() else 0
    out = {"n_clusters": int(n_unique), "n_noise": int((~valid).sum())}
    if n_unique < 2 or valid.sum() < 10:
        return {**out, "silhouette": np.nan, "davies_bouldin": np.nan,
                "calinski_harabasz": np.nan, "nmi_vs_cat34": np.nan,
                "ari_vs_cat34": np.nan, "va_spread": np.nan}
    x_v, lab_v = x_pre[valid], labels[valid]
    sub = np.random.default_rng(0).choice(len(x_v), size=min(2000, len(x_v)), replace=False)
    out["silhouette"] = float(silhouette_score(x_v[sub], lab_v[sub]))
    out["davies_bouldin"] = float(davies_bouldin_score(x_v, lab_v))
    out["calinski_harabasz"] = float(calinski_harabasz_score(x_v, lab_v))
    out["nmi_vs_cat34"] = float(normalized_mutual_info_score(cowen_top1[valid], lab_v))
    out["ari_vs_cat34"] = float(adjusted_rand_score(cowen_top1[valid], lab_v))
    out["va_spread"] = cluster_va_spread(labels, va)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out-csv", default=str(OUT_ROOT / "quality_summary.csv"))
    args = p.parse_args()

    cowen = load_cowen_labels()
    cat_top1 = cowen["cat34_top1"]
    va = cowen["va"]

    rows = []
    for src_dir in sorted(OUT_ROOT.glob("*")):
        if not src_dir.is_dir():
            continue
        source = src_dir.name
        if source not in ALL_SOURCES:
            continue  # skip _confusion, figures, per_subject, logs etc.
        x_pre = preprocess(load(source))
        for setting_dir in sorted(src_dir.glob("*")):
            labels_path = setting_dir / "labels.csv"
            if not labels_path.exists():
                continue
            labels = pd.read_csv(labels_path)["cluster_id"].to_numpy()
            q = quality_one(x_pre, labels, cat_top1, va)
            rows.append({"source": source, "setting": setting_dir.name, **q})
            print(f"[qual] {source}/{setting_dir.name}: n={q['n_clusters']} "
                  f"sil={q.get('silhouette', float('nan')):.3f} "
                  f"NMI={q.get('nmi_vs_cat34', float('nan')):.3f} "
                  f"ARI={q.get('ari_vs_cat34', float('nan')):.3f} "
                  f"va_spread={q.get('va_spread', float('nan')):.3f}", flush=True)
    df = pd.DataFrame(rows)
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out_csv, index=False)
    print(f"[qual] wrote {len(df)} rows to {args.out_csv}")


if __name__ == "__main__":
    main()
