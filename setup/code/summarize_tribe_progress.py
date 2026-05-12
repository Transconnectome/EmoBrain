#!/usr/bin/env python3
"""Summarize TRIBE v2 Horikawa stimulus-output progress."""

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path("/pscratch/sd/s/sjmoon")
NETFEELIX = ROOT / "FEELIN"
DEFAULT_META = ROOT / "Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv"
DEFAULT_RESULTS = NETFEELIX / "setup/results/tribe_horikawa"


def parse_stimulus_id(value):
    text = str(value).strip()
    if text.startswith("stimulus_"):
        text = text.split("_", 1)[1]
    return int(text)


def load_expected(meta_path):
    df = pd.read_csv(meta_path)
    return sorted(df["stimulus_num"].map(parse_stimulus_id).astype(int).tolist())


def scan_results(result_dir):
    rows = []
    for stim_dir in sorted(result_dir.glob("stimulus_*")):
        if not stim_dir.is_dir():
            continue
        stim_id = parse_stimulus_id(stim_dir.name)
        summary_path = stim_dir / "summary.json"
        pred_path = stim_dir / "tribe_preds_fsaverage5.npy"
        error_path = stim_dir / "error.json"
        row = {
            "stimulus_id": stim_id,
            "dir": str(stim_dir),
            "has_summary": summary_path.exists(),
            "has_prediction": pred_path.exists(),
            "has_error": error_path.exists(),
        }
        row["status"] = "complete" if row["has_summary"] and row["has_prediction"] else "error" if row["has_error"] else "partial"
        if summary_path.exists():
            try:
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
                row["pred_shape"] = summary.get("pred_shape")
                row["pred_absmean"] = summary.get("pred_absmean")
            except Exception:
                row["summary_read_error"] = True
        rows.append(row)
    return {"rows": rows}


def contiguous_prefix(done_ids, expected_ids):
    last = 0
    for stim_id in expected_ids:
        if stim_id not in done_ids:
            break
        last = stim_id
    return last


def build_summary(expected, rows, canonical_n, result_dir):
    expected_set = set(expected)
    canonical_set = {stim for stim in expected if stim <= canonical_n}
    complete = {row["stimulus_id"] for row in rows if row["status"] == "complete"}
    errors = {row["stimulus_id"] for row in rows if row["status"] == "error"}
    partial = {row["stimulus_id"] for row in rows if row["status"] == "partial"}
    expected_complete = complete & expected_set
    canonical_complete = complete & canonical_set
    return {
        "result_dir": str(result_dir),
        "metadata_expected": len(expected),
        "canonical_expected": len(canonical_set),
        "complete_total": len(complete),
        "complete_expected": len(expected_complete),
        "complete_canonical": len(canonical_complete),
        "partial_total": len(partial),
        "error_total": len(errors),
        "metadata_progress_pct": round(100 * len(expected_complete) / len(expected), 2) if expected else 0.0,
        "canonical_progress_pct": round(100 * len(canonical_complete) / len(canonical_set), 2) if canonical_set else 0.0,
        "highest_complete_id": max(complete) if complete else None,
        "contiguous_complete_to": contiguous_prefix(complete, expected),
        "missing_expected_first20": [stim for stim in expected if stim not in complete][:20],
        "partial_ids_first20": sorted(partial)[:20],
        "error_ids_first20": sorted(errors)[:20],
    }


def markdown(summary):
    return "\n".join(
        [
            "# TRIBE Horikawa Progress",
            "",
            f"- Result dir: `{summary['result_dir']}`",
            f"- Metadata expected stimuli: {summary['metadata_expected']}",
            f"- Canonical benchmark stimuli: {summary['canonical_expected']}",
            f"- Complete expected stimuli: {summary['complete_expected']} ({summary['metadata_progress_pct']}%)",
            f"- Complete canonical stimuli: {summary['complete_canonical']} ({summary['canonical_progress_pct']}%)",
            f"- Highest complete stimulus id: {summary['highest_complete_id']}",
            f"- Contiguous complete from stimulus 1 to: {summary['contiguous_complete_to']}",
            f"- Partial dirs: {summary['partial_total']}",
            f"- Error dirs: {summary['error_total']}",
            "",
            "TRIBE remains a stimulus-side teacher/alignment branch, not part of the current BFM axis.",
            "",
            f"First missing expected ids: {summary['missing_expected_first20']}",
            f"First partial ids: {summary['partial_ids_first20']}",
            f"First error ids: {summary['error_ids_first20']}",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta-path", default=str(DEFAULT_META))
    parser.add_argument("--result-dir", default=str(DEFAULT_RESULTS))
    parser.add_argument("--canonical-n", type=int, default=2185)
    parser.add_argument("--output-json", default=str(NETFEELIX / "reports/status/tribe_horikawa_progress.json"))
    parser.add_argument("--output-md", default=str(NETFEELIX / "reports/status/TRIBE_HORIKAWA_PROGRESS.md"))
    args = parser.parse_args()

    expected = load_expected(Path(args.meta_path))
    result_dir = Path(args.result_dir)
    rows = scan_results(result_dir)["rows"]
    summary = build_summary(expected, rows, args.canonical_n, result_dir)

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2), encoding="utf-8")

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(markdown(summary), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"Wrote {output_json}")
    print(f"Wrote {output_md}")


if __name__ == "__main__":
    main()
