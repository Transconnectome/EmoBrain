"""Phase 3 / A3-1, A3-2, A3-4. Participant-common stimulus-wise splits and
leakage tests.

Scientific question
-------------------
Can a held-out set be constructed such that no stimulus reaches both training
and evaluation through any participant, any duplicate file, or any nested
split, so that a held-out score measures generalization to new stimuli rather
than memorization?

What this excludes
------------------
Splitting on the stimulus file number would put videos 1 and 2186, or 259 and
866, or 1349 and 1363, on opposite sides. Those are the same clip. A model
would then be scored on a stimulus it was trained on, and the held-out number
would be uninterpretable. Grouping by canonical stimulus is what removes that
explanation, and it is only available because A1-3 computed content hashes.

Split unit
----------
prereg_v2 B8 requires that one stimulus sit in the same outer fold for every
participant, and A3-4 fixes the participant as the inferential unit and the
stimulus as the generalization unit. All five participants here saw the same
2196 presentations, so a single fold vector over canonical stimuli is shared by
every participant by construction, and that is asserted rather than assumed.

Open parameter
--------------
Neither prereg_v2 nor implementation_v2 states the number of outer or inner
folds. The values below are defaults written here so the split is executable;
they are recorded in the config block and must be confirmed before any outcome
is produced.

Outputs
-------
splits/outer_folds.tsv    canonical stimulus to outer fold
splits/inner_folds.tsv    canonical stimulus to inner fold, within each outer train
splits/folds.json         fold membership, config and seed
splits/split_config.json  the frozen split parameters and their status
tests/leakage_report.json result of every leakage assertion
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

from _assets import (  # noqa: E402
    ASSETS,
    MANIFESTS,
    SPLITS,
    TESTS,
    provenance,
    read_tsv,
    write_json,
    write_tsv,
)

SCRIPT = "prereg_v2/code/p3_splits_leakage.py"

SPLIT_CONFIG = {
    "unit": "canonical_stimulus_id",
    "n_outer_folds": 5,
    "n_inner_folds": 5,
    "seed": 20260923,
    "shuffle": True,
    "stratified": False,
    "stratification_note": (
        "A3-1 permits stratification only on a predefined summary and forbids "
        "balancing the target itself. No summary has been predefined, so the "
        "split is unstratified and the realised target balance is reported "
        "rather than enforced."),
    "status": "PROVISIONAL: fold counts are not fixed by prereg_v2 or "
              "implementation_v2 and require confirmation before freeze",
}


def assign_folds(units: np.ndarray, k: int, seed: int) -> np.ndarray:
    """Deterministic contiguous assignment after one seeded permutation."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(units))
    fold = np.empty(len(units), dtype=int)
    fold[order] = np.arange(len(units)) % k
    return fold


def main() -> None:
    prov = provenance(SCRIPT, {"split_config": SPLIT_CONFIG})

    cw = read_tsv(MANIFESTS / "stimulus_crosswalk.tsv")
    lab = pd.read_csv(ASSETS["labels_emobrain"]["path"])

    # ---- eligible set -------------------------------------------------------
    # A stimulus is eligible when it has an annotation row, a brain response in
    # the ROI time series, and a caption. Videos 2186-2196 fail the first two.
    elig = cw[cw.usable_for_modeling].copy()
    units = np.sort(elig.canonical_stimulus_id.unique())
    print(f"  eligible video numbers: {len(elig)}")
    print(f"  canonical stimuli to split: {len(units)}")

    outer = assign_folds(units, SPLIT_CONFIG["n_outer_folds"], SPLIT_CONFIG["seed"])
    outer_map = dict(zip(units.tolist(), outer.tolist()))

    of = pd.DataFrame({"canonical_stimulus_id": units, "outer_fold": outer})
    of["n_video_numbers"] = of.canonical_stimulus_id.map(
        elig.groupby("canonical_stimulus_id").size())
    of["video_numbers"] = of.canonical_stimulus_id.map(
        elig.groupby("canonical_stimulus_id").video_number
            .apply(lambda s: ",".join(map(str, sorted(s)))))

    # ---- inner folds, inside each outer training set ------------------------
    inner_rows = []
    for k in range(SPLIT_CONFIG["n_outer_folds"]):
        tr = units[outer != k]
        inner = assign_folds(tr, SPLIT_CONFIG["n_inner_folds"],
                             SPLIT_CONFIG["seed"] + 1000 + k)
        for u, f in zip(tr, inner):
            inner_rows.append({"outer_fold": k, "canonical_stimulus_id": int(u),
                               "inner_fold": int(f)})
    inf = pd.DataFrame(inner_rows)

    # ---- leakage assertions -------------------------------------------------
    tests: dict = {}

    def record(name: str, passed: bool, detail) -> None:
        tests[name] = {"passed": bool(passed), "detail": detail}
        print(f"    [{'PASS' if passed else 'FAIL'}] {name}")

    # 1. every eligible stimulus appears in exactly one outer fold
    record("every_canonical_stimulus_in_exactly_one_outer_fold",
           of.canonical_stimulus_id.is_unique and len(of) == len(units),
           {"n_units": int(len(units)), "n_rows": int(len(of))})

    # 2. outer folds are pairwise disjoint
    sets = {k: set(of.loc[of.outer_fold == k, "canonical_stimulus_id"])
            for k in range(SPLIT_CONFIG["n_outer_folds"])}
    inter = {f"{a}|{b}": len(sets[a] & sets[b])
             for a in sets for b in sets if a < b}
    record("outer_folds_pairwise_intersection_is_zero",
           all(v == 0 for v in inter.values()), inter)

    # 3. no duplicate file number is split across outer folds. This is the
    #    assertion that the content hash exists for.
    vid_fold = {}
    for _, r in elig.iterrows():
        vid_fold[int(r.video_number)] = outer_map[int(r.canonical_stimulus_id)]
    bad = []
    for cid, g in elig.groupby("canonical_stimulus_id"):
        f = {vid_fold[int(v)] for v in g.video_number}
        if len(f) > 1:
            bad.append({"canonical_stimulus_id": int(cid),
                        "video_numbers": sorted(int(v) for v in g.video_number),
                        "folds": sorted(f)})
    record("duplicate_and_near_duplicate_files_share_one_outer_fold",
           not bad, {"n_violations": len(bad), "violations": bad[:10],
                     "n_canonical_ids_with_multiple_files": int(
                         (elig.groupby("canonical_stimulus_id").size() > 1).sum())})

    # 4. the fold vector is identical for every participant
    spec = ASSETS["brain_roi_timeseries"]
    per_part = {}
    for pt in sorted(Path(spec["path"]).glob(spec["glob"])):
        d = torch.load(pt, map_location="cpu", weights_only=False)
        sn = np.asarray(d["stim_num"]).astype(int)
        folds = np.array([vid_fold.get(int(x), -1) for x in sn])
        per_part[pt.stem] = {
            "n_stimuli": int(sn.size),
            "n_without_fold": int((folds < 0).sum()),
            "fold_vector_sha256": hashlib.sha256(
                np.stack([sn, folds]).tobytes()).hexdigest(),
            "fold_sizes": {str(k): int((folds == k).sum())
                           for k in range(SPLIT_CONFIG["n_outer_folds"])},
        }
    ref = next(iter(per_part))
    record("outer_fold_assignment_identical_across_participants",
           all(v["fold_vector_sha256"] == per_part[ref]["fold_vector_sha256"]
               for v in per_part.values()),
           {k: v["fold_vector_sha256"][:16] for k, v in per_part.items()})
    record("every_participant_stimulus_has_a_fold",
           all(v["n_without_fold"] == 0 for v in per_part.values()),
           {k: v["n_without_fold"] for k, v in per_part.items()})

    # 5. inner folds never touch the outer test set
    viol = []
    for k in range(SPLIT_CONFIG["n_outer_folds"]):
        inner_units = set(inf.loc[inf.outer_fold == k, "canonical_stimulus_id"])
        overlap = inner_units & sets[k]
        if overlap:
            viol.append({"outer_fold": k, "n_overlap": len(overlap)})
    record("inner_folds_disjoint_from_outer_test", not viol,
           {"violations": viol})

    # 6. inner folds partition the outer training set exactly once
    bad_inner = []
    for k in range(SPLIT_CONFIG["n_outer_folds"]):
        sub = inf[inf.outer_fold == k]
        expect = set(units[outer != k].tolist())
        if set(sub.canonical_stimulus_id) != expect or sub.canonical_stimulus_id.duplicated().any():
            bad_inner.append(k)
    record("inner_folds_partition_outer_training_set", not bad_inner,
           {"bad_outer_folds": bad_inner})

    # 7. no annotated stimulus is missing from the split, and nothing outside
    #    the eligible set entered it
    lab_ids = set(lab.stim_num_int.astype(int))
    split_vids = set(int(v) for v in elig.video_number)
    record("split_covers_exactly_the_annotated_and_brain_matched_set",
           split_vids == (lab_ids & set(cw.loc[cw.in_brain_roi_timeseries, "video_number"])),
           {"n_in_split": len(split_vids), "n_annotated": len(lab_ids),
            "annotated_not_in_split": sorted(lab_ids - split_vids)[:10]})

    # ---- realised balance, reported not enforced ----------------------------
    cols34 = [c for c in lab.columns if c.startswith("score_")]
    lab2 = lab.merge(elig[["video_number", "canonical_stimulus_id"]],
                     left_on="stim_num_int", right_on="video_number", how="inner")
    lab2["outer_fold"] = lab2.canonical_stimulus_id.map(outer_map)
    bal = lab2.groupby("outer_fold")[cols34].mean()
    balance = {
        "n_annotated_rows_per_outer_fold":
            lab2.groupby("outer_fold").size().to_dict(),
        "max_across_fold_range_of_any_category_mean":
            float((bal.max() - bal.min()).max()),
        "mean_across_fold_range": float((bal.max() - bal.min()).mean()),
        "per_fold_mean_row_sum":
            lab2.groupby("outer_fold")[cols34].sum(axis=1).groupby(
                lab2.outer_fold).mean().to_dict()
            if False else
            lab2.assign(_rs=lab2[cols34].sum(axis=1)).groupby("outer_fold")._rs.mean().to_dict(),
    }

    folds_json = {
        "provenance": prov,
        "config": SPLIT_CONFIG,
        "n_canonical_stimuli": int(len(units)),
        "outer": {str(k): sorted(int(x) for x in sets[k]) for k in sets},
        "inner": {str(k): {str(j): sorted(
            int(x) for x in inf.loc[(inf.outer_fold == k) & (inf.inner_fold == j),
                                    "canonical_stimulus_id"])
            for j in range(SPLIT_CONFIG["n_inner_folds"])}
            for k in range(SPLIT_CONFIG["n_outer_folds"])},
        "canonical_to_video_numbers": {
            str(int(c)): sorted(int(v) for v in g.video_number)
            for c, g in elig.groupby("canonical_stimulus_id")},
    }
    folds_json["folds_sha256"] = hashlib.sha256(
        json.dumps({"outer": folds_json["outer"], "inner": folds_json["inner"]},
                   sort_keys=True).encode()).hexdigest()

    write_tsv(SPLITS / "outer_folds.tsv", of, prov)
    write_tsv(SPLITS / "inner_folds.tsv", inf, prov)
    write_json(SPLITS / "folds.json", folds_json)
    write_json(SPLITS / "split_config.json",
               {"provenance": prov, "config": SPLIT_CONFIG,
                "realised_balance": balance,
                "per_participant_fold_summary": per_part})
    write_json(TESTS / "leakage_report.json",
               {"provenance": prov,
                "all_passed": all(t["passed"] for t in tests.values()),
                "n_tests": len(tests), "tests": tests})

    print(f"\n  outer fold sizes: "
          f"{ {k: len(v) for k, v in sets.items()} }")
    print(f"  folds_sha256: {folds_json['folds_sha256']}")
    print(f"  all leakage tests passed: {all(t['passed'] for t in tests.values())}")
    print(f"  largest across-fold difference in any category mean: "
          f"{balance['max_across_fold_range_of_any_category_mean']:.5f}")


if __name__ == "__main__":
    main()
