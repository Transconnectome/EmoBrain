"""Build ROI time-series pt files per subject.

Source (read-only).
    /pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/time_series/
      sub-XX/stimulus_N/{fMRI.Schaefer17n400p.csv.gz, fMRI.Tian_Subcortex_S3_3T.csv.gz}

Output.
    project/shared/data/roi_timeseries/sub-XX.pt

Per-pt content (dict of tensors).
    roi_timeseries  (2185, T_max, 450) float32   right zero-padded
    roi_mean        (2185, 450)        float32   time-mean over valid T only
    mask            (2185, T_max)      bool      True = valid, False = padding
    original_T      (2185,)            int32     original time-series length per stim
    stim_num        (2185,)            int32     1-based canonical stimulus number
    T_max           int (47)
    n_roi           int (450)
    missing_stim    tensor of int32              stim_num values missing on disk

Sanity checks.
    1. Regenerated roi_mean matches existing reference
       (roi_schaefer400tian50_mean/sub-XX.pt embeddings) within float32 tolerance.
       Ensures our controlled pipeline reproduces the mean form baseline / E1 / E2 use.
    2. Padding-invariance. Replace values at padding positions with random noise,
       recompute mean using mask. Result identical to original mean.
       Ensures padded zeros do not leak into downstream computation.

Run.
    bash project/scripts/build_roi_timeseries.sh
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
import torch


SRC_ROOT = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/time_series")
OUT_ROOT = REPO_ROOT / "project" / "shared" / "data" / "roi_timeseries"
REF_ROOT = REPO_ROOT / "project" / "shared" / "output" / "embeddings" / "roi_schaefer400tian50_mean"

CANONICAL_N = 2185
T_MAX = 47            # covers longest observed stim (T=47 in Horikawa)
N_ROI = 450           # Schaefer-400 cortical + Tian-S3-50 subcortical


def load_stim(subj_dir: Path, stim_num: int) -> np.ndarray | None:
    """Return (T, 450) time-series for one stimulus, or None if missing."""
    stim_dir = subj_dir / f"stimulus_{stim_num}"
    cort = stim_dir / "fMRI.Schaefer17n400p.csv.gz"
    subc = stim_dir / "fMRI.Tian_Subcortex_S3_3T.csv.gz"
    if not cort.exists() or not subc.exists():
        return None
    cort_ts = pd.read_csv(cort).iloc[:, 1:].values.astype(np.float32)  # (400, T)
    subc_ts = pd.read_csv(subc).iloc[:, 1:].values.astype(np.float32)  # (50, T)
    assert cort_ts.shape[0] == 400 and subc_ts.shape[0] == 50
    combined = np.concatenate([cort_ts, subc_ts], axis=0)  # (450, T)
    return combined.T  # (T, 450)


def build_subject(subj: str) -> dict:
    subj_dir = SRC_ROOT / subj
    assert subj_dir.exists(), f"subject dir missing: {subj_dir}"

    ts = np.zeros((CANONICAL_N, T_MAX, N_ROI), dtype=np.float32)
    mask = np.zeros((CANONICAL_N, T_MAX), dtype=bool)
    original_T = np.zeros(CANONICAL_N, dtype=np.int32)
    stim_num = np.arange(1, CANONICAL_N + 1, dtype=np.int32)
    missing: list[int] = []

    for i, s in enumerate(stim_num):
        data = load_stim(subj_dir, int(s))
        if data is None:
            missing.append(int(s))
            continue
        T = data.shape[0]
        assert T <= T_MAX, f"stim {s}: T={T} exceeds T_MAX={T_MAX}"
        ts[i, :T, :] = data
        mask[i, :T] = True
        original_T[i] = T

    # Time-mean over VALID T only. ts is zero at padding so sum is unchanged.
    T_safe = np.maximum(original_T, 1)  # avoid /0 for missing (mean stays 0)
    roi_mean = ts.sum(axis=1) / T_safe[:, None]  # (2185, 450)

    return {
        "roi_timeseries": torch.from_numpy(ts),
        "roi_mean": torch.from_numpy(roi_mean),
        "mask": torch.from_numpy(mask),
        "original_T": torch.from_numpy(original_T),
        "stim_num": torch.from_numpy(stim_num),
        "T_max": T_MAX,
        "n_roi": N_ROI,
        "missing_stim": torch.tensor(missing, dtype=torch.int32),
    }


def sanity_vs_reference(subj: str, data: dict) -> None:
    ref_path = REF_ROOT / f"{subj}.pt"
    if not ref_path.exists():
        print(f"  [sanity]  no reference at {ref_path}, skip")
        return
    ref = torch.load(ref_path, map_location="cpu", weights_only=True)
    ref_emb: torch.Tensor = ref["embeddings"]
    ref_stim: torch.Tensor = ref["stim_num"]
    # Align by stim_num (in case ref only has a subset)
    ref_lookup = {int(s): i for i, s in enumerate(ref_stim.tolist())}
    matched = 0
    max_abs = 0.0
    mean_abs = 0.0
    n = 0
    for i, s in enumerate(data["stim_num"].tolist()):
        if s in ref_lookup:
            our = data["roi_mean"][i]
            ref_v = ref_emb[ref_lookup[s]]
            diff = (our - ref_v).abs()
            max_abs = max(max_abs, float(diff.max()))
            mean_abs += float(diff.mean())
            n += 1
            matched += 1
    mean_abs = mean_abs / max(n, 1)
    print(f"  [sanity]  regenerated mean vs reference ({matched} stim matched)")
    print(f"            max abs diff  = {max_abs:.2e}")
    print(f"            mean abs diff = {mean_abs:.2e}")
    assert max_abs < 1e-4, "regenerated mean does not match reference within tol"


def padding_invariance_test(data: dict) -> None:
    """Replace padding positions with large random noise. Recomputed mean must
    match the original (padding masked out).
    """
    ts = data["roi_timeseries"].clone()
    mask = data["mask"]
    T = data["original_T"]

    # Fill padding zone with large-magnitude random noise, per stim.
    for i in range(ts.shape[0]):
        t = int(T[i])
        if t < T_MAX:
            ts[i, t:, :] = torch.randn_like(ts[i, t:, :]) * 1e3

    # Apply mask: valid positions kept, padding zeroed.
    masked = ts * mask.unsqueeze(-1).to(ts.dtype)
    T_safe = T.clamp(min=1).to(torch.float32)
    recomputed = masked.sum(dim=1) / T_safe.unsqueeze(-1)

    diff = (data["roi_mean"] - recomputed).abs()
    print(f"  [invar]   padding-invariance: max abs diff = {float(diff.max()):.2e}")
    assert float(diff.max()) < 1e-4, "padding-invariance failed: mask does not block padding"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", default="sub-01,sub-02,sub-03,sub-04,sub-05")
    args = ap.parse_args()
    subjects = [s.strip() for s in args.subjects.split(",")]

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"[out] {OUT_ROOT}")

    for subj in subjects:
        print(f"\n=== {subj} ===")
        data = build_subject(subj)

        print(f"  roi_timeseries {tuple(data['roi_timeseries'].shape)}  dtype={data['roi_timeseries'].dtype}")
        print(f"  roi_mean       {tuple(data['roi_mean'].shape)}")
        print(f"  mask           {tuple(data['mask'].shape)}  valid_ratio={float(data['mask'].float().mean()):.3f}")
        print(f"  original_T     range [{int(data['original_T'].min())}, {int(data['original_T'].max())}]")
        print(f"  missing        {len(data['missing_stim'])} stim")

        sanity_vs_reference(subj, data)
        padding_invariance_test(data)

        out = OUT_ROOT / f"{subj}.pt"
        torch.save(data, out)
        size_mb = out.stat().st_size / (1024 * 1024)
        print(f"  [save]    {out}  ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
