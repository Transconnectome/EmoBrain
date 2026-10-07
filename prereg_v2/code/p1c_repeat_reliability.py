"""Phase 1. Magnitude of the repeat structure found in A1-4.

Scientific question
-------------------
The crosswalk shows that 16 canonical stimuli were presented twice. How much
agreement is there between the two presentations, on the brain side and on the
annotation side?

What this excludes
------------------
The count alone does not say whether a reliability estimate is usable. A
repeated-test design with a handful of stimuli and low agreement cannot select
a response estimator, set a noise ceiling, or serve as a final held-out set,
which is what prereg_v2 D7 and B9 and action_items A4-2 all assume it will do.
The magnitude is what decides that, so it is measured here rather than
deferred.

This is descriptive and label-blind on the brain side. It is not the A4-2
estimator comparison, which requires GLMsingle and raw timing that are not on
this system.

Outputs
-------
manifests/repeat_reliability.json
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
    provenance,
    read_tsv,
    write_json,
)

SCRIPT = "prereg_v2/code/p1c_repeat_reliability.py"


def main() -> None:
    prov = provenance(SCRIPT)
    cw = read_tsv(MANIFESTS / "stimulus_crosswalk.tsv")
    fmri = np.load(ASSETS["brain_roi_matrix"]["path"])  # (n_sub, 2196, 450)
    n_sub, n_pres, n_roi = fmri.shape

    # fmri_raw row j holds the response to video number j+1. Verified in p1.
    pairs = []
    for cid, g in cw.groupby("canonical_stimulus_id"):
        nums = sorted(int(v) for v in g.video_number)
        if len(nums) == 2:
            pairs.append((int(cid), nums[0], nums[1]))
    print(f"  canonical stimuli with exactly two presentations: {len(pairs)}")

    rows = []
    for cid, a, b in pairs:
        for s in range(n_sub):
            x = fmri[s, a - 1].astype(float)
            y = fmri[s, b - 1].astype(float)
            rows.append({
                "canonical_stimulus_id": cid,
                "video_a": a, "video_b": b,
                "participant_index": s,
                "roi_pattern_pearson_r": float(np.corrcoef(x, y)[0, 1]),
                "both_annotated": bool(a <= 2185 and b <= 2185),
            })
    rr = pd.DataFrame(rows)

    # A null for the same quantity: the same stimulus against a different one.
    rng = np.random.default_rng(20260923)
    null = []
    for cid, a, b in pairs:
        for s in range(n_sub):
            c = int(rng.integers(1, n_pres + 1))
            while c in (a, b):
                c = int(rng.integers(1, n_pres + 1))
            null.append(float(np.corrcoef(fmri[s, a - 1].astype(float),
                                          fmri[s, c - 1].astype(float))[0, 1]))
    null = np.array(null)

    # Annotation side: the two rows of the 34-D table for the same clip.
    lab = pd.read_csv(ASSETS["labels_emobrain"]["path"]).set_index("stim_num_int")
    cols34 = [c for c in lab.columns if c.startswith("score_")]
    dim14 = [c for c in lab.columns if c.endswith("_score")]
    ann = []
    for cid, a, b in pairs:
        if a > 2185 or b > 2185:
            continue
        p = lab.loc[a, cols34].to_numpy(float)
        q = lab.loc[b, cols34].to_numpy(float)
        u = lab.loc[a, dim14].to_numpy(float)
        v = lab.loc[b, dim14].to_numpy(float)
        ann.append({"canonical_stimulus_id": cid, "video_a": a, "video_b": b,
                    "profile34_pearson_r": float(np.corrcoef(p, q)[0, 1]),
                    "profile34_max_abs_diff": float(np.abs(p - q).max()),
                    "dim14_pearson_r": float(np.corrcoef(u, v)[0, 1]),
                    "dim14_max_abs_diff": float(np.abs(u - v).max())})

    out = {
        "provenance": prov,
        "n_canonical_stimuli_with_two_presentations": len(pairs),
        "n_such_stimuli_with_two_annotated_rows": len(ann),
        "brain_roi_pattern_repeat_reliability": {
            "n_observations": int(len(rr)),
            "mean_r": float(rr.roi_pattern_pearson_r.mean()),
            "median_r": float(rr.roi_pattern_pearson_r.median()),
            "min_r": float(rr.roi_pattern_pearson_r.min()),
            "max_r": float(rr.roi_pattern_pearson_r.max()),
            "per_participant_mean_r": rr.groupby(
                "participant_index").roi_pattern_pearson_r.mean().round(4).to_dict(),
        },
        "mismatched_stimulus_null": {
            "n_observations": int(null.size),
            "mean_r": float(null.mean()),
            "median_r": float(np.median(null)),
            "sd_r": float(null.std(ddof=1)),
        },
        "repeat_minus_null": float(rr.roi_pattern_pearson_r.mean() - null.mean()),
        "annotation_repeat_agreement": ann,
        "annotation_repeat_summary": {
            "profile34_mean_r": float(np.mean([a["profile34_pearson_r"] for a in ann]))
            if ann else None,
            "profile34_min_r": float(np.min([a["profile34_pearson_r"] for a in ann]))
            if ann else None,
            "dim14_mean_r": float(np.mean([a["dim14_pearson_r"] for a in ann]))
            if ann else None,
        },
        "reading": (
            "The repeat set is 16 canonical stimuli, of which 5 have two "
            "annotated rows. prereg_v2 D7 assumes 72. Whatever the agreement "
            "turns out to be, a set this small cannot select a response "
            "estimator, cannot fix a noise ceiling with usable precision, and "
            "cannot serve as the final held-out evaluation set that B9 "
            "reserves it for."),
    }
    write_json(MANIFESTS / "repeat_reliability.json", out)

    b = out["brain_roi_pattern_repeat_reliability"]
    n = out["mismatched_stimulus_null"]
    print(f"  brain repeat r: mean {b['mean_r']:.4f}, median {b['median_r']:.4f}, "
          f"range {b['min_r']:.4f} to {b['max_r']:.4f}")
    print(f"  mismatched-stimulus null r: mean {n['mean_r']:.4f}, sd {n['sd_r']:.4f}")
    print(f"  repeat minus null: {out['repeat_minus_null']:.4f}")
    if ann:
        s = out["annotation_repeat_summary"]
        print(f"  annotation 34-D repeat r: mean {s['profile34_mean_r']:.4f}, "
              f"min {s['profile34_min_r']:.4f}")
        print(f"  annotation 14-D repeat r: mean {s['dim14_mean_r']:.4f}")


if __name__ == "__main__":
    main()
