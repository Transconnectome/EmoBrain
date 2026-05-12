#!/usr/bin/env python3
"""Summarize fresh Horikawa BFM probe results into one comparison table."""

import argparse
import csv
import json
from pathlib import Path


ROOT = Path("/pscratch/sd/s/sjmoon")
NETFEELIX = ROOT / "FEELIN"
DEFAULT_RESULT_ROOT = NETFEELIX / "setup/results/horikawa_bfm_fresh"

MODEL_KEYS = [
    ("SwiFT-v2", "swift_v2"),
    ("Brain-JEPA", "brain_jepa"),
    ("NeuroSTORM", "neurostorm"),
    ("BrainLM", "brain_lm"),
]

TASK_PRIMARY = {
    "valence": "auc_roc",
    "arousal": "auc_roc",
    "emotion34": "mean_pearson_r",
}


def collect_rows(result_root):
    rows = []
    for model_name, model_arg in MODEL_KEYS:
        result_path = result_root / model_arg / f"{model_arg}_results.json"
        if not result_path.exists():
            rows.append(
                {
                    "dataset": "Horikawa/Cowen",
                    "bfm": model_name,
                    "model_arg": model_arg,
                    "task": "",
                    "decoder": "",
                    "metric": "",
                    "mean": "",
                    "std": "",
                    "n_subjects": 0,
                    "status": "missing_fresh_result_json",
                    "source": str(result_path),
                }
            )
            continue
        data = json.loads(result_path.read_text(encoding="utf-8"))
        tasks = sorted({task for subj in data.values() for task in subj.keys()})
        for task in tasks:
            decoder_names = sorted({decoder for subj in data.values() for decoder in subj.get(task, {}).keys()})
            for decoder in decoder_names:
                metric_names = sorted(
                    {
                        metric
                        for subj in data.values()
                        for metric in subj.get(task, {}).get(decoder, {}).get("summary", {}).keys()
                        if metric != "per_category"
                    }
                )
                for metric in metric_names:
                    values = []
                    for subj in sorted(data.keys()):
                        try:
                            values.append(float(data[subj][task][decoder]["summary"][metric]["mean"]))
                        except KeyError:
                            pass
                    if not values:
                        continue
                    mean = sum(values) / len(values)
                    var = sum((value - mean) ** 2 for value in values) / len(values)
                    rows.append(
                        {
                            "dataset": "Horikawa/Cowen",
                            "bfm": model_name,
                            "model_arg": model_arg,
                            "task": task,
                            "decoder": decoder,
                            "metric": metric,
                            "mean": mean,
                            "std": var ** 0.5,
                            "n_subjects": len(values),
                            "status": "ok",
                            "source": str(result_path),
                        }
                    )
    return rows


def write_csv(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["dataset", "bfm", "model_arg", "task", "decoder", "metric", "mean", "std", "n_subjects", "status", "source"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows, path):
    primary = [row for row in rows if row["status"] == "ok" and row["metric"] == TASK_PRIMARY.get(row["task"]) and row["decoder"] == "linear"]
    order = {"valence": 0, "arousal": 1, "emotion34": 2}
    primary = sorted(primary, key=lambda row: (order.get(row["task"], 99), -float(row["mean"])))
    lines = [
        "# Fresh Horikawa BFM Benchmark Summary",
        "",
        "Fresh-extracted BFM embeddings only. Old caches and old EmoDe result JSONs are not read.",
        "",
        "| Dataset | Task | BFM | Metric | Mean | Std | N |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for row in primary:
        lines.append(
            "| {dataset} | {task} | {bfm} | {metric} | {mean:.4f} | {std:.4f} | {n_subjects} |".format(
                dataset=row["dataset"],
                task=row["task"],
                bfm=row["bfm"],
                metric=row["metric"],
                mean=float(row["mean"]),
                std=float(row["std"]),
                n_subjects=row["n_subjects"],
            )
        )
    if not primary:
        lines.append("| Horikawa/Cowen | pending | pending fresh extraction | pending |  |  |  |")
    lines.extend(["", "Use this as the fresh Horikawa slice of the larger `Dataset x BFM x Task` matrix.", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-root", default=str(DEFAULT_RESULT_ROOT))
    parser.add_argument("--output-csv", default=str(NETFEELIX / "setup/results/horikawa_bfm_fresh_summary.csv"))
    parser.add_argument("--output-md", default=str(NETFEELIX / "setup/results/horikawa_bfm_fresh_summary.md"))
    args = parser.parse_args()

    rows = collect_rows(Path(args.result_root))
    write_csv(rows, Path(args.output_csv))
    write_markdown(rows, Path(args.output_md))
    print(f"Wrote {args.output_csv}")
    print(f"Wrote {args.output_md}")


if __name__ == "__main__":
    main()
