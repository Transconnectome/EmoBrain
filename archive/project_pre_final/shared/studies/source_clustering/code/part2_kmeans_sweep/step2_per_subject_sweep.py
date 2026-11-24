"""Stage A. per-subject clustering sweep.

For each (brain_source, subject in 1..5, algo, K), runs cluster + stores labels.
Output. results/clustering/per_subject/<source>__sub-XX/<algo>_K<K>/labels.csv

Default. 3 brain sources x 5 subj x 4 algo x 49 K = 2940 settings. CPU bound, ~15-30 min.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from part2_kmeans_sweep.step1_pooled_sweep import (
    DEFAULT_ALGOS,
    DEFAULT_KS,
    OUT_ROOT,
    ALGO_DISPATCH,
    preprocess,
)
from part1_embedding_load.load_embeddings import BRAIN_SOURCES, load_brain_single_subject

PS_ROOT = OUT_ROOT / "per_subject"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--brain-sources", nargs="+", default=list(BRAIN_SOURCES.keys()))
    p.add_argument("--subjects", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    p.add_argument("--algos", nargs="+", default=DEFAULT_ALGOS)
    p.add_argument("--ks", nargs="+", type=int, default=DEFAULT_KS)
    args = p.parse_args()

    PS_ROOT.mkdir(parents=True, exist_ok=True)
    for src_short in args.brain_sources:
        source_alias = f"brain.{src_short}"
        for subj in args.subjects:
            x = load_brain_single_subject(src_short, subj)
            x_pre = preprocess(x)
            tag = f"{source_alias}__sub-{subj:02d}"
            print(f"[ps-sweep] {tag} input {x.shape} -> {x_pre.shape}", flush=True)
            for algo in args.algos:
                ks = [-1] if algo == "hdbscan" else args.ks
                for k in ks:
                    labels = ALGO_DISPATCH[algo](x_pre, k)
                    out_dir = PS_ROOT / tag / (f"{algo}_K{k}" if algo != "hdbscan" else "hdbscan_auto")
                    out_dir.mkdir(parents=True, exist_ok=True)
                    pd.DataFrame({"stim_idx": np.arange(len(labels)), "cluster_id": labels}).to_csv(
                        out_dir / "labels.csv", index=False)
                short = "auto" if algo == "hdbscan" else f"K{k}"
                print(f"  {algo}_{short}: done all K", flush=True)
    print(f"[ps-sweep] done. results under {PS_ROOT}")


if __name__ == "__main__":
    main()
