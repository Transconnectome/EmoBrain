#!/usr/bin/env python3
"""Build a canonical Horikawa fMRI window manifest for NetFeeliX.

The manifest is the starting point for new extraction. It ignores legacy cache
contents and records the actual local fMRI windows for canonical Horikawa/Cowen
stimuli 1..2185.
"""

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path("/pscratch/sd/s/sjmoon")
DEFAULT_IMG_ROOT = ROOT / "Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img"
DEFAULT_OUTPUT = ROOT / "NetFeeliX/setup/data/horikawa_window_manifest.csv"
DEFAULT_SUMMARY = ROOT / "NetFeeliX/reports/status/horikawa_window_manifest_summary.json"
SUBJECT_RE = re.compile(r"^(sub-\d+)_stimulus_(\d+)$")


def frame_count(path):
    return sum(1 for _ in path.glob("frame_*.pt"))


def build_rows(img_root, canonical_stimuli):
    rows = []
    extras = []
    for path in sorted(img_root.glob("sub-*_stimulus_*")):
        if not path.is_dir():
            continue
        match = SUBJECT_RE.match(path.name)
        if match is None:
            continue
        subject, stim_raw = match.groups()
        stimulus_id = int(stim_raw)
        n_frames = frame_count(path)
        row = {
            "sample_id": path.name,
            "subject": subject,
            "stimulus_id": stimulus_id,
            "stimulus": f"stimulus_{stimulus_id}",
            "n_frames": n_frames,
            "path": str(path),
        }
        if stimulus_id <= canonical_stimuli:
            rows.append(row)
        else:
            extras.append(row)
    return rows, extras


def summarize(rows, extras, canonical_stimuli):
    frame_counts = Counter(row["n_frames"] for row in rows)
    per_subject = Counter(row["subject"] for row in rows)
    subject_stimuli = defaultdict(set)
    for row in rows:
        subject_stimuli[row["subject"]].add(row["stimulus_id"])

    observed_stimuli = {row["stimulus_id"] for row in rows}
    complete_stimuli = [
        stim
        for stim in observed_stimuli
        if sum(1 for subject in subject_stimuli if stim in subject_stimuli[subject]) == 5
    ]

    return {
        "canonical_stimuli": canonical_stimuli,
        "canonical_subject_stimulus_rows": len(rows),
        "observed_unique_stimuli": len(observed_stimuli),
        "complete_five_subject_stimuli": len(complete_stimuli),
        "local_extra_subject_stimulus_rows": len(extras),
        "local_extra_stimulus_ids": sorted({row["stimulus_id"] for row in extras}),
        "frame_count_distribution": {str(k): int(v) for k, v in sorted(frame_counts.items())},
        "per_subject_rows": {k: int(v) for k, v in sorted(per_subject.items())},
        "min_frame_count": min(frame_counts) if frame_counts else None,
        "max_frame_count": max(frame_counts) if frame_counts else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--img-root", default=str(DEFAULT_IMG_ROOT))
    parser.add_argument("--canonical-stimuli", type=int, default=2185)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--summary-output", default=str(DEFAULT_SUMMARY))
    args = parser.parse_args()

    img_root = Path(args.img_root)
    rows, extras = build_rows(img_root, args.canonical_stimuli)
    summary = summarize(rows, extras, args.canonical_stimuli)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["sample_id", "subject", "stimulus_id", "stimulus", "n_frames", "path"],
        )
        writer.writeheader()
        writer.writerows(rows)

    summary_output = Path(args.summary_output)
    summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Wrote manifest: {output}")
    print(f"Wrote summary : {summary_output}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
