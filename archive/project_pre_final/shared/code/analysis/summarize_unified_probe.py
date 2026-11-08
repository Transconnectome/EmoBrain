"""
Unified probe 결과 요약.

Input:
  results/phase1/probe_{task}.csv (per-task CSV, per-seed row)

Output:
  Console: aggregate 표 + best cell + per-mode 비교
  results/phase1/probe_{task}_table.txt (markdown 표)
  results/phase1/probe_{task}_fig.png (bar chart)

Usage:
  python code/analysis/summarize_unified_probe.py --task V_binary
  python code/analysis/summarize_unified_probe.py --task V_binary,A_binary
  python code/analysis/summarize_unified_probe.py --task all
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/shared/results/phase1")

TASK_LIST = ["V_binary", "A_binary", "V_reg", "A_reg", "Cat34_top1", "Dim14_multi"]
TASK_METRIC_NAME = {
    "V_binary": "AUROC", "A_binary": "AUROC",
    "V_reg": "Pearson r", "A_reg": "Pearson r",
    "Cat34_top1": "Balanced Acc", "Dim14_multi": "Mean Pearson r",
}
TASK_BASELINE = {  # chance level
    "V_binary": 0.5, "A_binary": 0.5,
    "V_reg": 0.0, "A_reg": 0.0,
    "Cat34_top1": 1/34, "Dim14_multi": 0.0,
}


def load_task(task):
    p = ROOT / f"probe_{task}.csv"
    if not p.exists():
        p = ROOT / f"probe_{task}_linear.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p)
    return df


def summarize_task(task):
    df = load_task(task)
    if df is None:
        print(f"[skip] {task}: no CSV in {ROOT}")
        return None
    metric = TASK_METRIC_NAME[task]
    baseline = TASK_BASELINE[task]
    print(f"\n{'='*90}")
    print(f"TASK: {task}  (main metric: {metric}, chance = {baseline:.3f})")
    print(f"{'='*90}")

    # Aggregate per (feature, init, head, mode), mean over seed + subject (for per_subject mode)
    agg = (df.groupby(["feature", "init", "head", "mode"])["test_main"]
             .agg(["mean", "std", "count"])
             .reset_index())
    agg["main_str"] = agg.apply(lambda r: f"{r['mean']:.3f} ± {r['std']:.3f}", axis=1)
    pivot = agg.pivot_table(index=["feature", "init", "head"],
                            columns="mode", values="main_str", aggfunc="first")
    print(pivot.to_string())

    # Best cell
    best = agg.loc[agg["mean"].idxmax()]
    print(f"\nBest cell ({metric}): {best['feature']} / {best['init']} / {best['head']} / {best['mode']} = {best['mean']:.3f} ± {best['std']:.3f}")

    return agg, df


def make_figure(task, agg, out_path):
    metric = TASK_METRIC_NAME[task]
    baseline = TASK_BASELINE[task]

    # Sort by feature + init for consistent x-axis
    features = sorted(agg["feature"].unique())
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, mode in zip(axes, ["pooled", "per_subject"]):
        sub = agg[agg["mode"] == mode]
        if len(sub) == 0:
            continue
        x_labels = []
        means = []
        stds = []
        colors = []
        for feat in features:
            for init in ["resting", "scratch", "n/a"]:
                for head in ["linear", "mlp"]:
                    cell = sub[(sub["feature"]==feat) & (sub["init"]==init) & (sub["head"]==head)]
                    if len(cell) == 0:
                        continue
                    short_feat = feat.replace("SwiFT_NewE96", "SwiFT").replace("Brain-JEPA", "BJ").replace("NeuroSTORM", "NS").replace("ROI_Schaefer400Tian50", "ROI")
                    short_init = "" if init == "n/a" else f"_{init[0]}"
                    short_head = "L" if head == "linear" else "M"
                    x_labels.append(f"{short_feat}{short_init}_{short_head}")
                    means.append(cell["mean"].values[0])
                    stds.append(cell["std"].values[0])
                    if "ROI" in feat: colors.append("#7f8c8d")
                    elif "SwiFT" in feat: colors.append("#3498db" if init == "resting" else "#85c1e2")
                    elif "JEPA" in feat: colors.append("#e74c3c" if init == "resting" else "#f5b7b1")
                    elif "STORM" in feat: colors.append("#27ae60" if init == "resting" else "#a9dfbf")
                    else: colors.append("#000000")

        x = np.arange(len(x_labels))
        ax.bar(x, means, yerr=stds, capsize=2, color=colors, edgecolor="black", linewidth=0.4)
        ax.axhline(baseline, color="grey", ls="--", lw=0.8, alpha=0.6, label=f"chance={baseline:.2f}")
        ax.set_xticks(x); ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=7)
        ax.set_ylabel(metric); ax.set_title(f"{mode}")
        ax.grid(axis="y", alpha=0.25, ls=":")
        # Add values on bars
        for xi, mi, si in zip(x, means, stds):
            ax.text(xi, mi + (si if not np.isnan(si) else 0) + 0.005, f"{mi:.3f}",
                    ha="center", va="bottom", fontsize=6)
    fig.suptitle(f"Task: {task}  (metric: {metric})", fontsize=13)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  figure → {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="all", help="comma-separated or 'all'")
    args = ap.parse_args()

    if args.task == "all":
        tasks = TASK_LIST
    else:
        tasks = [t.strip() for t in args.task.split(",")]

    for task in tasks:
        out = summarize_task(task)
        if out is None:
            continue
        agg, df = out
        fig_path = ROOT / f"probe_{task}_fig.png"
        make_figure(task, agg, fig_path)


if __name__ == "__main__":
    main()
