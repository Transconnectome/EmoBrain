"""Video cluster vs brain cluster alignment.

For each (video_source, brain_source, algo, K), compute
  NMI(video_labels, brain_labels), ARI, confusion matrix.

Same algo + same K only (apples to apples). HDBSCAN ignored (K not fixed).

Output. results/clustering/video_vs_brain.csv
        + per-comparison confusion matrices under results/clustering/_confusion/
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, confusion_matrix, normalized_mutual_info_score

from part2_kmeans_sweep.step1_pooled_sweep import OUT_ROOT


def load_labels(source: str, setting: str) -> np.ndarray | None:
    p = OUT_ROOT / source / setting / "labels.csv"
    if not p.exists():
        return None
    return pd.read_csv(p)["cluster_id"].to_numpy()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--video-sources", nargs="+", default=["video.vjepa2", "video.clip"])
    p.add_argument("--brain-sources", nargs="+", default=["brain.roi_mean", "brain.brain_jepa", "brain.swift"])
    p.add_argument("--out-csv", default=str(OUT_ROOT / "video_vs_brain.csv"))
    args = p.parse_args()

    confusion_dir = OUT_ROOT / "_confusion"
    confusion_dir.mkdir(parents=True, exist_ok=True)

    settings = set()
    for src in args.video_sources + args.brain_sources:
        d = OUT_ROOT / src
        if d.exists():
            settings.update(p.name for p in d.iterdir() if p.is_dir() and p.name != "_confusion")
    settings = sorted(s for s in settings if not s.startswith("hdbscan"))

    rows = []
    for setting in settings:
        for v_src in args.video_sources:
            v_lab = load_labels(v_src, setting)
            if v_lab is None:
                continue
            for b_src in args.brain_sources:
                b_lab = load_labels(b_src, setting)
                if b_lab is None:
                    continue
                nmi = normalized_mutual_info_score(v_lab, b_lab)
                ari = adjusted_rand_score(v_lab, b_lab)
                cm = confusion_matrix(v_lab, b_lab)
                np.save(confusion_dir / f"{v_src}__vs__{b_src}__{setting}.npy", cm)
                rows.append({
                    "setting": setting, "video": v_src, "brain": b_src,
                    "nmi": float(nmi), "ari": float(ari),
                    "n_video_clusters": int(len(np.unique(v_lab))),
                    "n_brain_clusters": int(len(np.unique(b_lab))),
                })
                print(f"[compare] {setting}  {v_src} vs {b_src}  NMI={nmi:.3f}  ARI={ari:.3f}", flush=True)
    df = pd.DataFrame(rows)
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out_csv, index=False)
    print(f"[compare] wrote {len(df)} rows to {args.out_csv}")
    print(f"[compare] confusion matrices under {confusion_dir}")


if __name__ == "__main__":
    main()
