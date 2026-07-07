"""Measure brain cross-subject ISC (noise ceiling estimator).

Uses fMRI ROI mean (5 subj × stim × 450) to compute how consistent brain
responses are across subjects. Reports on the TEST split (same axis as the B1
baseline) and also on all stimuli for a fuller picture.

Context. B1 ridge profile pearson was 0.29. This ISC tells us whether that is
"model-limited" (high ISC, shared signal exists) or "signal-limited" (low ISC,
brain response is idiosyncratic, R0 risk).

Output.
    project/shared/results/noise_ceiling/brain_isc.json
    project/shared/results/noise_ceiling/per_roi_isc.npy

Run.
    bash project/scripts/measure_brain_isc.sh
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd

from project.data.fmri_adapter import FmriAdapter, SUBJECTS
from project.evaluation.noise_ceiling import spatial_isc, per_roi_isc


DATA_DIR = REPO_ROOT / "project" / "shared" / "data"
SPLIT_CSV = DATA_DIR / "horikawa_split.csv"
OUT_DIR = REPO_ROOT / "project" / "shared" / "results" / "noise_ceiling"


def stim_tensor(adapter: FmriAdapter, stim_nums: list[int]) -> np.ndarray:
    """Return (n_subj, n_stim, 450) roi_mean tensor for the given stimuli."""
    arr = np.zeros((len(SUBJECTS), len(stim_nums), adapter.n_roi), dtype=np.float64)
    for si, subj in enumerate(SUBJECTS):
        for ti, sn in enumerate(stim_nums):
            arr[si, ti] = adapter.get(subj, sn, mode="mean").numpy()
    return arr


def report(name: str, stim_nums: list[int], adapter: FmriAdapter) -> dict:
    X = stim_tensor(adapter, stim_nums)
    sp = spatial_isc(X)
    roi = per_roi_isc(X)
    print(f"\n=== {name}  (n_stim={len(stim_nums)}, {sp['n_pairs']} subject pairs) ===")
    print(f"  spatial ISC   mean={sp['mean']:+.4f} median={sp['median']:+.4f} std={sp['std']:.4f}")
    print(f"  per-ROI ISC   mean={roi['mean']:+.4f} median={roi['median']:+.4f}")
    print(f"  top ROI ISC   {[round(v,3) for v in roi['top_roi_val'][:5]]} (idx {roi['top_roi_idx'][:5]})")
    return {
        "spatial": {k: v for k, v in sp.items() if k != "per_stim"},
        "per_roi_mean": roi["mean"],
        "per_roi_median": roi["median"],
        "top_roi_idx": roi["top_roi_idx"],
        "top_roi_val": roi["top_roi_val"],
        "_per_roi_full": roi["per_roi"],
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    adapter = FmriAdapter()
    split = pd.read_csv(SPLIT_CSV)

    test_stims = sorted(split.loc[split["split"] == "test", "stimulus_num"].unique().tolist())
    all_stims = sorted(split["stimulus_num"].unique().tolist())

    out = {}
    r_test = report("TEST split", test_stims, adapter)
    r_all = report("ALL stimuli", all_stims, adapter)

    # Save per-ROI map (test) for later brain visualization.
    np.save(OUT_DIR / "per_roi_isc.npy", r_test.pop("_per_roi_full"))
    r_all.pop("_per_roi_full")

    out["test"] = r_test
    out["all"] = r_all
    out["note"] = ("ISC = stimulus-driven cross-subject brain consistency. NOT an "
                   "emotion-decoding ceiling. High ISC => shared signal exists "
                   "(model-limited); low ISC => idiosyncratic (R0 risk).")
    (OUT_DIR / "brain_isc.json").write_text(json.dumps(out, indent=2))

    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print(f"  B1 ridge profile pearson (test) = 0.294 (reference)")
    print(f"  spatial ISC (test)              = {r_test['spatial']['mean']:+.4f}")
    print(f"  per-ROI ISC (test)              = {r_test['per_roi_mean']:+.4f}")
    print(f"\n[save] {OUT_DIR / 'brain_isc.json'}")


if __name__ == "__main__":
    main()
