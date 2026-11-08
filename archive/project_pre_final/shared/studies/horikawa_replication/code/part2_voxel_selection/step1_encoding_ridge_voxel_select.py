"""part2 step1. Voxel selection by encoding regression R^2.

Per-subject, voxel-wise ridge regression from Cowen 34-cat soft ratings to BOLD voxel.
5-fold CV. Per voxel compute cv-Pearson r^2 (sign preserved). Threshold to select emotion-related voxels.

This makes our clustering input match Horikawa et al. 2020 Figure 6: paper used encoding-significant voxels only,
not whole-brain.

Input.
  results/voxel_patterns/sub-XX.npy  shape (N_stim=2185, N_voxel_masked)        (from part1 step1)
  shared/data/cowen_horikawa_labels.csv -> 34 columns score_0 .. score_33

Output.
  results/voxel_selection/sub-XX_r2_map.npy        full per-voxel signed r^2  shape (N_voxel,)
  results/voxel_selection/sub-XX_selected_idx.npy  voxel indices with r^2 >= threshold (1-D int)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

REPO = Path("/pscratch/sd/s/sjmoon/EmoBrain")
STUDY = REPO / "project" / "shared" / "studies" / "horikawa_replication"
VOXEL_DIR = STUDY / "results" / "voxel_patterns"
OUT_DIR = STUDY / "results" / "voxel_selection"
LABELS_CSV = REPO / "project" / "shared" / "data" / "cowen_horikawa_labels.csv"


def load_cat34() -> np.ndarray:
    df = pd.read_csv(LABELS_CSV)
    df = df.sort_values("stim_idx").reset_index(drop=True)
    return df[[f"score_{i}" for i in range(34)]].to_numpy(dtype=np.float32)


def cv_r2_per_voxel(X: np.ndarray, Y: np.ndarray, n_splits: int = 5, alpha: float = 1.0) -> np.ndarray:
    """5-fold CV signed r^2 per voxel.

    X shape (N, n_features), Y shape (N, V). Returns (V,) sign-preserving r^2.
    Multi-output Ridge means one fit covers all V voxels per fold.
    """
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=0)
    y_pred = np.zeros_like(Y, dtype=np.float32)
    for fold, (tr, te) in enumerate(kf.split(X)):
        ridge = Ridge(alpha=alpha)
        ridge.fit(X[tr], Y[tr])
        y_pred[te] = ridge.predict(X[te]).astype(np.float32)
        print(f"  fold {fold+1}/{n_splits} fit (alpha={alpha})", flush=True)
    yc = Y - Y.mean(axis=0, keepdims=True)
    pc = y_pred - y_pred.mean(axis=0, keepdims=True)
    num = (yc * pc).sum(axis=0)
    den = np.sqrt((yc ** 2).sum(axis=0) * (pc ** 2).sum(axis=0)) + 1e-12
    r = num / den
    return (np.sign(r) * (r ** 2)).astype(np.float32)


def process_subject(subj: int, X: np.ndarray, alpha: float, r2_thresh: float) -> None:
    in_path = VOXEL_DIR / f"sub-{subj:02d}.npy"
    if not in_path.exists():
        print(f"[encoding] sub-{subj:02d}: no voxel patterns at {in_path} (run part1 first); skip", flush=True)
        return
    Y = np.load(in_path).astype(np.float32)
    print(f"[encoding] sub-{subj:02d}: Y shape={Y.shape}", flush=True)
    r2 = cv_r2_per_voxel(X, Y, n_splits=5, alpha=alpha)
    sel = np.where(r2 >= r2_thresh)[0].astype(np.int64)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    np.save(OUT_DIR / f"sub-{subj:02d}_r2_map.npy", r2)
    np.save(OUT_DIR / f"sub-{subj:02d}_selected_idx.npy", sel)
    print(f"[encoding] sub-{subj:02d}: r^2 mean={r2.mean():.4f} "
          f"median={float(np.median(r2)):.4f} max={r2.max():.4f} "
          f"-> {len(sel)} of {len(r2)} voxels pass r^2 >= {r2_thresh}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--subjects", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    p.add_argument("--alpha", type=float, default=1.0, help="ridge alpha")
    p.add_argument("--r2-threshold", type=float, default=0.05,
                   help="signed r^2 threshold (default 0.05, paper-style)")
    args = p.parse_args()
    X = load_cat34()
    print(f"[encoding] X (Cat34 soft) shape={X.shape}", flush=True)
    for s in args.subjects:
        process_subject(s, X, alpha=args.alpha, r2_thresh=args.r2_threshold)
    print("[encoding] all subjects done.")


if __name__ == "__main__":
    main()
