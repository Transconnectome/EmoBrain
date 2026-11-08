"""Phase 1 / A1-4. Event and run audit.

Scientific question
-------------------
Which brain response corresponds to which stimulus presentation, in which run
and session, for how long, and how many times was each stimulus presented?

What this excludes
------------------
prereg_v2 D7 and B9 reserve 72 repeated stimuli for reliability, noise ceiling
and final held-out evaluation, and A4-2 selects the response estimator by
repeated-test reliability. Every one of those depends on repeated
presentations actually existing in the data. Counting them from the event
records, rather than assuming the design document, is what decides whether
those analyses are executable at all. Presented duration also varies here, so
a fixed-length boxcar assumption would be wrong; the audit measures it.

Source
------
Per-stimulus sidecars written by the segmentation step, one per presentation:
  EmoViS/data/raw/step7_voxel/sub-XX/sub-XX_stimulus-<name>[_vN]_meta.txt
and one summary per run:
  EmoViS/data/raw/step7_voxel/sub-XX/sub-XX_ses-YY_run-ZZ_stimulus_summary.txt

Outputs
-------
manifests/events_audited.tsv   one row per presentation
manifests/runs.tsv             one row per participant, session and run
manifests/event_audit.json     integrity verdicts
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

from _assets import (  # noqa: E402
    ASSETS,
    DOC_CLAIMS,
    EVENT_META_GLOB,
    EVENT_META_ROOT,
    MANIFESTS,
    RUN_SUMMARY_GLOB,
    provenance,
    write_json,
    write_tsv,
)

SCRIPT = "prereg_v2/code/p1b_event_run_audit.py"
REPEAT_SUFFIX = re.compile(r"_v(\d+)$")


def parse_meta(path: Path) -> dict:
    d = {"meta_path": str(path)}
    for line in path.read_text().splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            d[k.strip()] = v.strip()
    return d


def to_stimulus_number(name: str):
    """'1000.0' -> 1000; 'baseline' -> None."""
    try:
        f = float(name)
    except ValueError:
        return None
    return int(f) if float(f).is_integer() else None


def main() -> None:
    prov = provenance(SCRIPT, {"event_meta_root": str(EVENT_META_ROOT)})
    audit: dict = {"provenance": prov}

    subs = sorted(p.name for p in EVENT_META_ROOT.glob("sub-*") if p.is_dir())
    print(f"  participants with event metadata: {subs}")

    rows = []
    for s in subs:
        metas = sorted((EVENT_META_ROOT / s).glob(EVENT_META_GLOB))
        print(f"  {s}: {len(metas)} presentation sidecars")
        for m in metas:
            d = parse_meta(m)
            stem = m.name.replace("_meta.txt", "")
            rep = REPEAT_SUFFIX.search(stem)
            shape = d.get("data_shape", "")
            nt = None
            if shape.startswith("(") and "," in shape:
                try:
                    nt = int(shape.strip("()").split(",")[-1])
                except ValueError:
                    nt = None
            rows.append({
                "participant_id": d.get("subject", s),
                "session": d.get("session"),
                "run": d.get("run"),
                "stimulus_name": d.get("stimulus_name"),
                "stimulus_number": to_stimulus_number(d.get("stimulus_name", "")),
                "is_baseline": d.get("stimulus_name") == "baseline",
                "presentation_suffix": int(rep.group(1)) if rep else 0,
                "stimulus_index_in_run": int(float(d.get("stimulus_index", "nan")))
                if d.get("stimulus_index") not in (None, "") else None,
                "onset_sec": float(d.get("onset_sec", "nan")),
                "duration_sec": float(d.get("duration_sec", "nan")),
                "onset_tr": int(float(d.get("onset_tr", "nan"))),
                "duration_tr": int(float(d.get("duration_tr", "nan"))),
                "data_shape": shape,
                "data_shape_n_tr": nt,
                "is_duplicate_flag": d.get("is_duplicate") == "True",
                "meta_path": str(m),
            })
    ev = pd.DataFrame(rows)

    # ---- per participant ----------------------------------------------------
    per_part = {}
    stim_sets = {}
    for s, g in ev.groupby("participant_id"):
        st = g[~g.is_baseline]
        counts = st.stimulus_number.value_counts()
        stim_sets[s] = set(st.stimulus_number.dropna().astype(int))
        per_part[s] = {
            "n_presentation_records": int(len(g)),
            "n_baseline_records": int(g.is_baseline.sum()),
            "n_stimulus_presentations": int(len(st)),
            "n_unique_stimuli": int(st.stimulus_number.nunique()),
            "n_stimuli_presented_more_than_once": int((counts > 1).sum()),
            "max_presentations_of_any_stimulus": int(counts.max()),
            "n_sessions": int(g.session.nunique()),
            "n_runs": int(g.groupby(["session", "run"]).ngroups),
            "duration_sec_min": float(st.duration_sec.min()),
            "duration_sec_max": float(st.duration_sec.max()),
            "duration_sec_mean": float(st.duration_sec.mean()),
            "n_unresolved_stimulus_names": int(st.stimulus_number.isna().sum()),
            "data_shape_n_tr_equals_duration_tr": bool(
                (st.data_shape_n_tr == st.duration_tr).all()),
        }
    audit["per_participant"] = per_part

    ref = subs[0]
    audit["participant_stimulus_set_identical"] = {
        s: bool(stim_sets[s] == stim_sets[ref]) for s in subs}
    audit["n_stimuli_in_all_participants"] = len(set.intersection(*stim_sets.values()))
    audit["n_stimuli_in_any_participant"] = len(set.union(*stim_sets.values()))

    # ---- within-run timing integrity ---------------------------------------
    overlaps, dup_onsets = [], []
    run_rows = []
    for (s, ses, run), g in ev.groupby(["participant_id", "session", "run"]):
        g = g.sort_values("onset_sec")
        on = g.onset_sec.to_numpy()
        off = on + g.duration_sec.to_numpy()
        n_ov = int((on[1:] < off[:-1] - 1e-9).sum())
        n_dup = int(len(on) - len(np.unique(on)))
        if n_ov:
            overlaps.append({"participant_id": s, "session": ses, "run": run,
                             "n_overlapping_pairs": n_ov})
        if n_dup:
            dup_onsets.append({"participant_id": s, "session": ses, "run": run,
                               "n_duplicate_onsets": n_dup})
        st = g[~g.is_baseline]
        run_rows.append({
            "participant_id": s, "session": ses, "run": run,
            "n_records": int(len(g)),
            "n_stimulus_presentations": int(len(st)),
            "n_baseline_blocks": int(g.is_baseline.sum()),
            "onset_min_sec": float(on.min()), "offset_max_sec": float(off.max()),
            "n_overlapping_pairs": n_ov, "n_duplicate_onsets": n_dup,
        })
    runs = pd.DataFrame(run_rows).sort_values(
        ["participant_id", "session", "run"]).reset_index(drop=True)

    audit["timing_integrity"] = {
        "n_runs_with_overlapping_presentations": len(overlaps),
        "runs_with_overlap": overlaps[:20],
        "n_runs_with_duplicate_onsets": len(dup_onsets),
        "runs_with_duplicate_onsets": dup_onsets[:20],
        "n_records_with_missing_onset": int(ev.onset_sec.isna().sum()),
        "n_records_with_missing_duration": int(ev.duration_sec.isna().sum()),
    }

    # ---- cross-check against the derived ROI time series --------------------
    spec = ASSETS["brain_roi_timeseries"]
    roi_checks = {}
    for pt in sorted(Path(spec["path"]).glob(spec["glob"])):
        d = torch.load(pt, map_location="cpu", weights_only=False)
        sn = np.asarray(d["stim_num"]).astype(int)
        ot = np.asarray(d["original_T"]).astype(int)
        g = ev[(ev.participant_id == pt.stem) & (~ev.is_baseline)]
        m = dict(zip(g.stimulus_number.astype("Int64"), g.duration_tr))
        aligned = np.array([m.get(int(x), -1) for x in sn])
        roi_checks[pt.stem] = {
            "n_roi_stimuli": int(sn.size),
            "n_event_stimuli": int(len(g)),
            "n_roi_stimuli_absent_from_events": int((aligned < 0).sum()),
            "n_event_stimuli_absent_from_roi": int(
                len(set(g.stimulus_number.dropna().astype(int)) - set(sn.tolist()))),
            "original_T_matches_event_duration_tr": bool(
                np.all(aligned[aligned >= 0] == ot[aligned >= 0])),
            "n_original_T_mismatches": int(
                (aligned[aligned >= 0] != ot[aligned >= 0]).sum()),
        }
    audit["roi_timeseries_cross_check"] = roi_checks

    # ---- repeats, counted by content rather than by file number -------------
    # A stimulus shown twice under two file numbers is still a repeat. Counting
    # by file number alone reports zero repeats and would wrongly conclude that
    # no reliability estimate is possible.
    cw = pd.read_csv(MANIFESTS / "stimulus_crosswalk.tsv", sep="\t", comment="#")
    to_canon = dict(zip(cw.video_number, cw.canonical_stimulus_id))
    ev["canonical_stimulus_id"] = ev.stimulus_number.map(to_canon)
    annotated = set(cw.loc[cw.usable_for_modeling, "video_number"])

    max_rep_by_file = max(v["max_presentations_of_any_stimulus"]
                          for v in per_part.values())
    n_rep_by_file = max(v["n_stimuli_presented_more_than_once"]
                        for v in per_part.values())
    g = ev[~ev.is_baseline]
    can_per_part = {}
    for s_, gg in g.groupby("participant_id"):
        c = gg.canonical_stimulus_id.value_counts()
        ca = gg[gg.stimulus_number.isin(annotated)].canonical_stimulus_id.value_counts()
        can_per_part[s_] = {
            "n_canonical_stimuli": int(gg.canonical_stimulus_id.nunique()),
            "n_canonical_repeated": int((c > 1).sum()),
            "max_presentations": int(c.max()),
            "n_canonical_repeated_within_annotated_set": int((ca > 1).sum()),
        }
    audit["canonical_repeat_structure"] = can_per_part

    n_rep_canon = max(v["n_canonical_repeated"] for v in can_per_part.values())
    n_rep_canon_ann = max(v["n_canonical_repeated_within_annotated_set"]
                          for v in can_per_part.values())
    audit["repeated_presentation_verdict"] = {
        "claimed_repeated_test_stimuli_prereg_v2_D7": DOC_CLAIMS[
            "prereg_v2_D7_repeated_test_stimuli"],
        "measured_stimuli_presented_more_than_once_by_file_number": n_rep_by_file,
        "measured_max_presentations_by_file_number": max_rep_by_file,
        "measured_canonical_stimuli_presented_more_than_once": n_rep_canon,
        "measured_canonical_repeats_inside_the_annotated_set": n_rep_canon_ann,
        "repeated_test_design_executable_at_claimed_size": bool(
            n_rep_canon >= DOC_CLAIMS["prereg_v2_D7_repeated_test_stimuli"]),
        "any_repeat_reliability_estimable": bool(n_rep_canon > 0),
        "consequence": (
            "prereg_v2 D7 and B9 reserve 72 repeated stimuli for reliability, "
            "noise ceiling and final held-out evaluation, and action_items "
            "A4-2 chooses between the existing block response and GLMsingle by "
            "repeated-test reliability. The measured number of repeated "
            "canonical stimuli is the ceiling on all of these, and it is far "
            "below 72. A reliability estimate from this many stimuli is a "
            "descriptive number, not a basis for choosing an estimator."),
    }

    write_tsv(MANIFESTS / "events_audited.tsv", ev, prov)
    write_tsv(MANIFESTS / "runs.tsv", runs, prov)
    write_json(MANIFESTS / "event_audit.json", audit)

    print("\n  ---- per participant ----")
    for s, v in per_part.items():
        print(f"    {s}: {v['n_stimulus_presentations']} presentations, "
              f"{v['n_unique_stimuli']} unique, "
              f"{v['n_stimuli_presented_more_than_once']} repeated, "
              f"{v['n_sessions']} sessions, {v['n_runs']} runs, "
              f"duration {v['duration_sec_min']}-{v['duration_sec_max']}s")
    print("  ---- repeated presentations ----")
    for k, v in audit["repeated_presentation_verdict"].items():
        if k != "consequence":
            print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
