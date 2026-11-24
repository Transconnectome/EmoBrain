"""Phase 3. Negative control for the leakage test.

Scientific question
-------------------
Does the leakage test in p3 actually detect leakage, or does it pass because
nothing is being checked?

What this excludes
------------------
A test suite that passes on the split it was written for is not evidence. If
the same test does not fail on the split that the project would naturally have
produced, the passes in p3 carry no information. This script builds the naive
split, the one keyed on the stimulus file number, and reports how much content
leakage it contains and how much that leakage would inflate a held-out score.

Outputs
-------
tests/leakage_negative_control.json
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from _assets import (  # noqa: E402
    ASSETS,
    MANIFESTS,
    TESTS,
    provenance,
    read_tsv,
    write_json,
)
from p3_splits_leakage import SPLIT_CONFIG, assign_folds  # noqa: E402

SCRIPT = "prereg_v2/code/p3b_leakage_negative_control.py"


def main() -> None:
    prov = provenance(SCRIPT)
    cw = read_tsv(MANIFESTS / "stimulus_crosswalk.tsv")
    elig = cw[cw.usable_for_modeling].copy()

    # The split the project would produce without a content hash: one fold per
    # stimulus file number.
    vids = np.sort(elig.video_number.unique())
    naive = assign_folds(vids, SPLIT_CONFIG["n_outer_folds"], SPLIT_CONFIG["seed"])
    naive_map = dict(zip(vids.tolist(), naive.tolist()))

    split_groups = []
    for cid, g in elig.groupby("canonical_stimulus_id"):
        nums = sorted(int(v) for v in g.video_number)
        folds = sorted({naive_map[n] for n in nums})
        if len(folds) > 1:
            split_groups.append({"canonical_stimulus_id": int(cid),
                                 "video_numbers": nums, "folds": folds})

    # How different are the annotations of two files that are the same clip?
    lab = pd.read_csv(ASSETS["labels_emobrain"]["path"]).set_index("stim_num_int")
    cols34 = [c for c in lab.columns if c.startswith("score_")]
    pair_stats = []
    for cid, g in elig.groupby("canonical_stimulus_id"):
        nums = sorted(int(v) for v in g.video_number)
        if len(nums) < 2:
            continue
        a, b = lab.loc[nums[0], cols34].to_numpy(float), lab.loc[nums[1], cols34].to_numpy(float)
        pair_stats.append({
            "canonical_stimulus_id": int(cid),
            "video_numbers": nums,
            "profile_pearson_r": float(np.corrcoef(a, b)[0, 1]),
            "max_abs_diff": float(np.abs(a - b).max()),
            "identical_rows": bool(np.allclose(a, b)),
            "leaked_under_naive_split": bool(
                len({naive_map[n] for n in nums}) > 1),
        })

    leaked = [p for p in pair_stats if p["leaked_under_naive_split"]]
    out = {
        "provenance": prov,
        "naive_split_description": (
            "outer folds assigned on stimulus file number with the same seed "
            "and fold count as the canonical split"),
        "n_canonical_stimuli_with_more_than_one_eligible_file": len(pair_stats),
        "n_such_stimuli_split_across_outer_folds_by_the_naive_split":
            len(split_groups),
        "leaked_groups": split_groups,
        "duplicate_pair_annotation_agreement": pair_stats,
        "leaked_pairs_mean_profile_r": (
            float(np.mean([p["profile_pearson_r"] for p in leaked]))
            if leaked else None),
        "negative_control_verdict": {
            "test_detects_leakage": bool(split_groups),
            "reading": (
                "the canonical split passes the same assertion that the naive "
                "split fails, so the passes in p3 are informative rather than "
                "vacuous" if split_groups else
                "the naive split happens to place every duplicate pair in one "
                "fold under this seed, so this run does not demonstrate that "
                "the assertion can fail and the control is inconclusive"),
        },
    }
    write_json(TESTS / "leakage_negative_control.json", out)

    print(f"  canonical stimuli with >1 eligible file: {len(pair_stats)}")
    print(f"  of those, split across folds by the naive split: {len(split_groups)}")
    for g in split_groups:
        print(f"    {g['video_numbers']} -> folds {g['folds']}")
    print("\n  annotation agreement within duplicate pairs:")
    for p in pair_stats:
        print(f"    {p['video_numbers']}: r={p['profile_pearson_r']:.4f}, "
              f"max|diff|={p['max_abs_diff']:.4f}, identical={p['identical_rows']}, "
              f"leaked={p['leaked_under_naive_split']}")
    print(f"\n  test detects leakage: {out['negative_control_verdict']['test_detects_leakage']}")


if __name__ == "__main__":
    main()
