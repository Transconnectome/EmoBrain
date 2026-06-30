"""Stage C step 1. Extract per-subject per-stim voxel mean pattern.

For each subject 1..5, each stim 1..2185:
  - load all frame_T.pt files (per-TR voxel volume, shape (74,91,81,1))
  - mean across TR
  - apply brain mask (global_stats.pt: valid_voxels)
  - flatten -> 1D vector

Output. results/clustering/voxel_patterns/sub-XX.npy  shape (N_stim=2185, N_voxel_masked)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch

REPO = Path("/pscratch/sd/s/sjmoon/EmoBrain")
N_STIM = 2185

RAW_ROOT = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img")
OUT_DIR = REPO / "project" / "shared" / "studies" / "horikawa_replication" / "results" / "voxel_patterns"
LABELS_CSV = REPO / "project" / "shared" / "data" / "cowen_horikawa_labels.csv"


def derive_brain_mask(subject: int, stim_ids: list[int], n_probe: int = 5) -> np.ndarray:
    """Derive brain mask from union of nonzero voxels across n_probe stim's frames.

    `global_stats.pt['valid_voxels']` is an int count, not a mask. We use the
    union of nonzero voxels across the first n_probe stim x all their frames.
    """
    acc = None
    used = 0
    for sid in stim_ids[:n_probe]:
        sd = RAW_ROOT / f"sub-{subject:02d}_stimulus_{sid}"
        mean3d = load_stim_mean(sd)
        if mean3d is None:
            continue
        nz = (mean3d != 0)
        acc = nz if acc is None else (acc | nz)
        used += 1
    if acc is None:
        raise RuntimeError(f"sub-{subject:02d}: no probe stim found to derive mask")
    print(f"[mask] sub-{subject:02d}: union of {used} stim -> {int(acc.sum())} voxels", flush=True)
    return acc


def load_stim_mean(stim_dir: Path) -> np.ndarray:
    """Return (74, 91, 81) mean across all TR frames as np.float32."""
    frames = sorted(stim_dir.glob("frame_*.pt"))
    if not frames:
        return None
    arrs = []
    for f in frames:
        t = torch.load(f, weights_only=False, map_location="cpu")
        if isinstance(t, torch.Tensor):
            arr = t.detach().cpu().numpy().astype(np.float32).squeeze()
            arrs.append(arr)
    if not arrs:
        return None
    stacked = np.stack(arrs, axis=0)  # (T, 74, 91, 81)
    return stacked.mean(axis=0)


def get_stim_ids() -> list[int]:
    import pandas as pd
    df = pd.read_csv(LABELS_CSV)
    df = df.sort_values("stim_idx").reset_index(drop=True)
    return df["stim_num_int"].astype(int).tolist()


def extract_subject(subject: int, stim_ids: list[int]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"sub-{subject:02d}.npy"
    if out_path.exists():
        print(f"[voxel] sub-{subject:02d} already exists, skip", flush=True)
        return
    mask = derive_brain_mask(subject, stim_ids, n_probe=5)
    n_masked = int(mask.sum())
    print(f"[voxel] sub-{subject:02d} brain mask = {n_masked} voxels", flush=True)
    out_mat = np.zeros((N_STIM, n_masked), dtype=np.float32)
    missing = 0
    for i, sid in enumerate(stim_ids):
        sd = RAW_ROOT / f"sub-{subject:02d}_stimulus_{sid}"
        mean3d = load_stim_mean(sd)
        if mean3d is None:
            missing += 1
            continue
        out_mat[i] = mean3d[mask]
        if (i + 1) % 250 == 0:
            print(f"  sub-{subject:02d} stim {i+1}/{N_STIM} done", flush=True)
    np.save(out_path, out_mat)
    np.save(OUT_DIR / f"sub-{subject:02d}_mask.npy", mask)
    print(f"[voxel] sub-{subject:02d} saved shape={out_mat.shape} missing={missing} -> {out_path}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--subjects", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    args = p.parse_args()
    stim_ids = get_stim_ids()
    print(f"[voxel] {len(stim_ids)} stim ids, range {min(stim_ids)}..{max(stim_ids)}", flush=True)
    for s in args.subjects:
        extract_subject(s, stim_ids)
    print("[voxel] all subjects done")


if __name__ == "__main__":
    main()
