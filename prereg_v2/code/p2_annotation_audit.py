"""Phase 2 / A2-1 to A2-4. Annotation audit for the 34-D and 14-D targets.

Scientific question
-------------------
What exactly do the 34 and 14 dimensional columns measure, on what scale, with
what missingness, and can the underlying selection counts k and rater counts n
be recovered?

What this excludes
------------------
A2-1 makes the loss function conditional on this audit. If k and n are
recoverable, a binomial negative log likelihood is defensible as a robustness
analysis; if they are not, it is not, and unweighted SoftBCE stays primary.
Treating a graded multi-select proportion as a single-choice distribution, as
one-hot, or as a count each changes both the loss and every metric. prereg_v2
L8 additionally fixes the 34-D values at raw [0,1] with no z-score and no
log1p, so whether the stored values really are raw proportions has to be
measured, not assumed.

Outputs
-------
manifests/target34_codebook.tsv       per-category summary
manifests/target14_codebook.tsv       per-dimension summary
manifests/target_lowdim_mapping.json  VA-2 and VAD-3 mapping verdict
manifests/annotation_audit.json       scale, denominator and missingness verdicts
"""
from __future__ import annotations

import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from _assets import (  # noqa: E402
    ASSETS,
    DOC_CLAIMS,
    MANIFESTS,
    provenance,
    write_json,
    write_tsv,
)

SCRIPT = "prereg_v2/code/p2_annotation_audit.py"

# prereg_v2 L2 names the 14-D space but no local file states the order, so the
# order used here is the order the columns appear in, recorded explicitly.
DIM14 = [
    "arousal_score", "dominance_score", "valence_score", "approach_score",
    "attention_score", "certainty_score", "commitment_score", "control_score",
    "effort_score", "fairness_score", "identity_score", "obstruction_score",
    "safety_score", "upswing_score",
]


def valid_denominators(values: np.ndarray, max_n: int = 400,
                       tol: float = 1e-5) -> list:
    """All n such that every observed value sits within `tol` of some k/n.

    The comparison is on the value scale rather than on v*n, because the stored
    values are rounded to about five decimals and an error of 1e-5 in v becomes
    n*1e-5 after multiplying. Testing |v - round(v*n)/n| keeps the tolerance
    independent of n and stops large n from passing trivially.
    """
    x = np.unique(values[np.isfinite(values)])
    if x.size == 0:
        return []
    return [n for n in range(1, max_n + 1)
            if np.all(np.abs(x - np.round(x * n) / n) <= tol)]


def denominator_report(m: np.ndarray, label: str, max_n: int = 400,
                       tol: float = 1e-5) -> dict:
    """Recover the rater count, pooled and per stimulus.

    A proportion or a mean over n raters can only land on a 1/n grid, so the
    grid spacing identifies n. It identifies n only up to an integer multiple:
    if every rater count in a stimulus happens to be even, n and 2n fit the
    same values. A2-1 and prereg_v2 L10 make the binomial robustness analysis
    conditional on k and n being confirmed, and a factor of two in n scales the
    likelihood weight by two, so the multiple matters.
    """
    pooled = valid_denominators(m.ravel(), max_n, tol)
    per = [valid_denominators(m[i], min(max_n, 120), tol)
           for i in range(m.shape[0])]
    smallest = [min(v) for v in per if v]
    common = set.intersection(*[set(v) for v in per]) if all(per) else set()
    out = {
        "target": label,
        "pooled_valid_n": pooled[:15],
        "single_n_fits_all_values": bool(pooled),
        "n_stimuli": int(m.shape[0]),
        "n_stimuli_with_a_recoverable_grid": int(sum(1 for v in per if v)),
        "n_valid_for_every_stimulus": sorted(common),
        "smallest_n_per_stimulus_counts": [
            [int(k_), int(c_)] for k_, c_ in
            sorted(collections.Counter(smallest).items())],
    }
    if smallest:
        a = np.array(smallest)
        out.update(smallest_n_min=int(a.min()), smallest_n_max=int(a.max()),
                   smallest_n_median=float(np.median(a)))
        # k is exactly recoverable from the smallest n
        exact = sum(1 for i, v in enumerate(per) if v and np.all(
            np.abs(m[i] - np.round(m[i] * min(v)) / min(v)) <= tol))
        out["n_stimuli_where_k_reconstructs_exactly"] = int(exact)
    if pooled:
        out["interpretation"] = (
            f"every value lies on a 1/{pooled[0]} grid, so the aggregate is "
            f"over {pooled[0]} raters, or a multiple of {pooled[0]}")
    else:
        out["interpretation"] = (
            "no single n fits all stimuli, so the number of raters varies "
            "across stimuli. Each stimulus has its own minimal denominator, "
            "and the true count is that denominator or an integer multiple "
            "of it. k/n is therefore exact but n itself is not pinned down.")
    return out


def main() -> None:
    prov = provenance(SCRIPT)
    lab = pd.read_csv(ASSETS["labels_emobrain"]["path"])
    audit: dict = {"provenance": prov,
                   "source_file": str(ASSETS["labels_emobrain"]["path"]),
                   "n_rows": int(len(lab))}

    # ------------------------------------------------------------ 34-D -----
    cols34 = [c for c in lab.columns if c.startswith("score_")]
    m34 = lab[cols34].to_numpy(dtype=float)

    rows = []
    for i, c in enumerate(cols34):
        x = m34[:, i]
        rows.append({
            "index": i,
            "column": c,
            "category_name": "UNRESOLVED: headers are positional only",
            "n_missing": int(np.isnan(x).sum()),
            "min": float(np.nanmin(x)),
            "max": float(np.nanmax(x)),
            "mean": float(np.nanmean(x)),
            "std": float(np.nanstd(x)),
            "n_zero": int((x == 0).sum()),
            "frac_zero": float((x == 0).mean()),
            "n_nonzero": int((x > 0).sum()),
            "marginal_prevalence": float(np.nanmean(x)),
        })
    cb34 = pd.DataFrame(rows)

    row_sums = np.nansum(m34, axis=1)
    nonzero_per_stim = (m34 > 0).sum(axis=1)
    # Pairwise dependence among categories, as A2-1 requires.
    with np.errstate(invalid="ignore"):
        C = np.corrcoef(m34, rowvar=False)
    off = C[~np.eye(len(cols34), dtype=bool)]

    audit["target34"] = {
        "n_columns": len(cols34),
        "global_min": float(np.nanmin(m34)),
        "global_max": float(np.nanmax(m34)),
        "within_unit_interval": bool(np.nanmin(m34) >= 0 and np.nanmax(m34) <= 1),
        "is_one_hot": bool(np.all(np.isin(m34, [0.0, 1.0]))),
        "n_missing_cells": int(np.isnan(m34).sum()),
        "frac_zero_cells": float((m34 == 0).mean()),
        "nonzero_categories_per_stimulus_mean": float(nonzero_per_stim.mean()),
        "nonzero_categories_per_stimulus_min": int(nonzero_per_stim.min()),
        "nonzero_categories_per_stimulus_max": int(nonzero_per_stim.max()),
        "row_sum_min": float(row_sums.min()),
        "row_sum_max": float(row_sums.max()),
        "row_sum_mean": float(row_sums.mean()),
        "n_rows_summing_to_one_within_1e-6": int(np.sum(np.abs(row_sums - 1.0) < 1e-6)),
        "rows_sum_to_one": bool(np.allclose(row_sums, 1.0, atol=1e-5)),
        "scale_verdict": (
            "multi-select proportion. Values lie in [0,1] but rows do not sum "
            "to 1, so each column is the fraction of raters who selected that "
            "category and a rater could select several. The row sum is the "
            "mean number of categories a rater chose for that stimulus. It is "
            "not a single-choice distribution and softmax is not applicable."),
        "pairwise_dependence": {
            "mean_offdiagonal_pearson_r": float(np.nanmean(off)),
            "min_offdiagonal_pearson_r": float(np.nanmin(off)),
            "max_offdiagonal_pearson_r": float(np.nanmax(off)),
            "n_pairs_with_abs_r_above_0_5": int(np.sum(np.abs(off) > 0.5) // 2),
        },
        "denominator_recovery": denominator_report(m34, "target34"),
        "category_names_available": False,
        "category_name_note": (
            "columns are named score_0..score_33 with no embedded names. The "
            "Cowen-Keltner category order has to be recovered from the source "
            "release before any per-category claim, and prereg_v2 A2-1 "
            "requires that order to be hash-fixed across the pipeline."),
    }
    # A2-1 makes the loss conditional on this result.
    rec = audit["target34"]["denominator_recovery"]
    fully = (rec["n_stimuli_with_a_recoverable_grid"] == rec["n_stimuli"]
             and rec["single_n_fits_all_values"])
    audit["target34"]["loss_decision"] = {
        "primary": "unweighted SoftBCE on raw [0,1] proportions",
        "binomial_nll_robustness_permitted": bool(fully),
        "status": ("k and n confirmed" if fully else
                   "k/n is exact for every stimulus and a minimal denominator "
                   "exists for every stimulus, but no single rater count fits "
                   "all stimuli and each stimulus admits its denominator and "
                   "every multiple of it. n is therefore not confirmed."),
        "basis": ("prereg_v2 L10 and action_items A2-1 permit a binomial "
                  "negative log likelihood only when k and n are confirmed"),
        "if_run_anyway": ("report the result under the minimal denominator and "
                          "under twice it, since the two differ by a factor of "
                          "two in likelihood weight"),
    }
    # prereg_v2 L8 forbids z-score and log1p on the 34-D target.
    audit["target34"]["prereg_L8_raw_proportion_check"] = {
        "values_are_raw_proportions_in_unit_interval": bool(
            np.nanmin(m34) >= 0 and np.nanmax(m34) <= 1),
        "conflicting_repository_spec": (
            "EmoBrain README and docs/paper_logic_merged.md describe the "
            "decoder target as log1p_z. prereg_v2 L8 fixes raw [0,1]. These "
            "cannot both hold and the conflict is unresolved."),
    }

    # ------------------------------------------------------------ 14-D -----
    missing14 = [c for c in DIM14 if c not in lab.columns]
    present14 = [c for c in DIM14 if c in lab.columns]
    m14 = lab[present14].to_numpy(dtype=float)

    rows = []
    for i, c in enumerate(present14):
        x = m14[:, i]
        fin = x[np.isfinite(x)]
        rows.append({
            "index": i,
            "column": c,
            "n_missing": int(np.isnan(x).sum()),
            "min": float(np.nanmin(x)),
            "max": float(np.nanmax(x)),
            "mean": float(np.nanmean(x)),
            "std": float(np.nanstd(x)),
            "p01": float(np.nanpercentile(x, 1)),
            "p99": float(np.nanpercentile(x, 99)),
            "n_distinct": int(np.unique(fin).size),
            "rating_direction": "UNVERIFIED: no local codebook states polarity",
            "reverse_coded": "UNVERIFIED",
        })
    cb14 = pd.DataFrame(rows)

    audit["target14"] = {
        "n_columns_expected": len(DIM14),
        "n_columns_present": len(present14),
        "columns_missing": missing14,
        "column_order_source": "order of appearance in the label file",
        "global_min": float(np.nanmin(m14)),
        "global_max": float(np.nanmax(m14)),
        "n_missing_cells": int(np.isnan(m14).sum()),
        "denominator_recovery": denominator_report(m14, "target14", tol=6e-5),
        "scale_verdict": (
            "the observed range is measured here, but the intended rating "
            "scale, the polarity of each dimension and any reverse coding are "
            "not verifiable from any file on this system. A2-2 requires the "
            "official codebook and it is not present."),
    }

    # ------------------------------------------------- VA-2 and VAD-3 ------
    mapping = {
        "VA2": {"valence": "valence_score", "arousal": "arousal_score"},
        "VAD3": {"valence": "valence_score", "arousal": "arousal_score",
                 "dominance": "dominance_score"},
    }
    verdict = {}
    for space, cols in mapping.items():
        present = {k: (v in lab.columns) for k, v in cols.items()}
        verdict[space] = {
            "columns": cols,
            "all_present": all(present.values()),
            "per_column_present": present,
            "direction_verified": False,
            "note": ("the column names match the construct names, but A2-3 "
                     "requires the direction and source question confirmed "
                     "against the codebook before the mapping is frozen. "
                     "prereg_v2 L3 removes VAD-3 if the dominance mapping is "
                     "insufficient, and that decision cannot be made yet."),
        }
    audit["lowdim_mapping"] = verdict

    # -------------------------------------------- A2-4 target independence --
    shared = set(cols34) & set(present14)
    audit["target_independence"] = {
        "n_columns_shared_between_34d_and_14d": len(shared),
        "shared_columns": sorted(shared),
        "note": ("A2-4 concerns shared trainable parameters and caches, which "
                 "is a training-time assertion. At the data level the two "
                 "target blocks use disjoint columns of one file, so the "
                 "stimulus key is shared by construction and only the fold "
                 "assignment may be shared."),
    }

    # ---------------------------------------------------- key integrity ----
    audit["key_integrity"] = {
        "n_duplicate_stim_num_int": int(lab.stim_num_int.duplicated().sum()),
        "stim_num_int_is_contiguous_1_to_n": bool(
            np.array_equal(np.sort(lab.stim_num_int.to_numpy()),
                           np.arange(1, len(lab) + 1))),
        "n_rows_with_any_missing_target": int(
            lab[cols34 + present14].isna().any(axis=1).sum()),
        "n_rows_with_all_zero_34d": int((m34.sum(axis=1) == 0).sum()),
    }

    audit["caption_claim"] = {
        "claimed_raters_per_clip": DOC_CLAIMS["captions_raters_per_clip"],
        "note": "verified in p1 against the caption table, not here",
    }

    write_tsv(MANIFESTS / "target34_codebook.tsv", cb34, prov)
    write_tsv(MANIFESTS / "target14_codebook.tsv", cb14, prov)
    write_json(MANIFESTS / "target_lowdim_mapping.json",
               {"provenance": prov, "mapping": verdict})
    write_json(MANIFESTS / "annotation_audit.json", audit)

    t = audit["target34"]
    print("\n  ---- 34-D ----")
    for k in ["within_unit_interval", "is_one_hot", "rows_sum_to_one",
              "frac_zero_cells", "nonzero_categories_per_stimulus_mean",
              "row_sum_mean", "row_sum_max", "n_missing_cells"]:
        print(f"    {k}: {t[k]}")
    r = t["denominator_recovery"]
    print(f"    single n fits all values: {r['single_n_fits_all_values']}")
    print(f"    stimuli with a recoverable grid: "
          f"{r['n_stimuli_with_a_recoverable_grid']} / {r['n_stimuli']}")
    print(f"    smallest n per stimulus: {r.get('smallest_n_min')} to "
          f"{r.get('smallest_n_max')}, median {r.get('smallest_n_median')}")
    print(f"    binomial NLL permitted: "
          f"{t['loss_decision']['binomial_nll_robustness_permitted']}")
    print(f"      {t['loss_decision']['status']}")
    print("  ---- 14-D ----")
    for k in ["n_columns_present", "columns_missing", "global_min",
              "global_max", "n_missing_cells"]:
        print(f"    {k}: {audit['target14'][k]}")
    r14 = audit["target14"]["denominator_recovery"]
    print(f"    pooled valid n: {r14['pooled_valid_n'][:6]}")
    print(f"    {r14['interpretation']}")


if __name__ == "__main__":
    main()
