"""
FEELIN Phase 2 unified analysis.

Inputs (all per-(fold,seed) CSVs with `task, feature, test_main`):
  - Joint A/B/C/D     results/phase2/{A,B,C,D}/{task}.csv
  - Contrastive C aux results/phase2/C/probe_{joint,brain_only}_{task}.csv
  - Brain-only I~IV   results/phase2/brain_only/{method}/{task}.csv
  - Phase 1 reference results/phase1/_best_conditions_per_task.csv

Outputs:
  results/phase2/_phase2_benchmark_per_task.csv
  results/phase2/_phase2_vs_phase1_best.csv
  results/phase2/_phase2_joint_vs_brainonly.csv
  figures/phase2/ranking_<task>.png
  figures/phase2/joint_vs_brainonly.png
  figures/phase2/method_heatmap.png
"""
from pathlib import Path
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 8,
    "axes.titlesize": 9,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,
})

PALETTE = {
    "joint":      "#3182BD",
    "brain_only": "#E6550D",
    "phase1_bfm": "#9E9E9E",
    "phase1_top": "#252525",
    "highlight":  "#D62728",
}

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
RES1   = FEELIN / "results/phase1"
RES2   = FEELIN / "results/phase2"
FIGS   = FEELIN / "figures/phase2"
FIGS.mkdir(parents=True, exist_ok=True)

TASKS = ["V_binary", "A_binary", "V_reg", "A_reg"]
TASK_METRIC = {"V_binary": "AUROC", "A_binary": "AUROC",
               "V_reg": "Pearson r", "A_reg": "Pearson r"}

JOINT_FILES = {
    "A_token_transformer": [RES2 / f"A/{t}.csv" for t in TASKS],
    "B_cross_attention":   [RES2 / f"B/{t}.csv" for t in TASKS],
    "C_contrastive_joint": [RES2 / f"C/probe_joint_{t}.csv" for t in TASKS],
    "C_contrastive_brain": [RES2 / f"C/probe_brain_only_{t}.csv" for t in TASKS],
    "D_late_fusion":       [RES2 / f"D/{t}.csv" for t in TASKS],
}
BRAIN_ONLY_METHODS = ["I_supervised", "II_distillation", "III_multitask", "IV_subject_aware"]
BRAIN_ONLY_FILES = {
    f"BrainOnly_{m}": [RES2 / f"brain_only/{m}/{t}.csv" for t in TASKS]
    for m in BRAIN_ONLY_METHODS
}

# ============================================================
# Load + aggregate
# ============================================================

def _load_group(name: str, files: list[Path]) -> pd.DataFrame:
    rows = []
    for p in files:
        if not p.exists():
            print(f"  [WARN] missing {p}")
            continue
        d = pd.read_csv(p, keep_default_na=False, na_values=[""])
        d["method"] = name
        rows.append(d)
    if not rows:
        return pd.DataFrame()
    df = pd.concat(rows, ignore_index=True)
    df = df[df["task"].isin(TASKS)].copy()
    return df


def load_all() -> pd.DataFrame:
    dfs = []
    for name, files in JOINT_FILES.items():
        d = _load_group(name, files); d["kind"] = "joint"; dfs.append(d)
    for name, files in BRAIN_ONLY_FILES.items():
        d = _load_group(name, files); d["kind"] = "brain_only"; dfs.append(d)
    out = pd.concat([d for d in dfs if len(d) > 0], ignore_index=True)
    return out


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["task", "method", "kind"]).agg(
        test_main_mean=("test_main", "mean"),
        test_main_std=("test_main", "std"),
        n_cells=("test_main", "size"),
    ).reset_index()
    return g


def load_phase1_reference() -> pd.DataFrame:
    p = RES1 / "_best_conditions_per_task.csv"
    if not p.exists():
        print(f"  [WARN] missing phase1 reference {p}")
        return pd.DataFrame()
    return pd.read_csv(p)


def vs_phase1(agg: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    if ref.empty:
        return pd.DataFrame()
    bfm_features = {"SwiFT_NewE96", "Brain-JEPA", "NeuroSTORM"}
    rows = []
    for task in TASKS:
        sub_ref = ref[ref["task"] == task]
        top_overall = sub_ref.sort_values("test_main_mean", ascending=False).iloc[0]
        bfm_only = sub_ref[sub_ref["feature"].isin(bfm_features)]
        top_bfm = bfm_only.sort_values("test_main_mean", ascending=False).iloc[0] if len(bfm_only) else None
        sub_p2 = agg[agg["task"] == task].sort_values("test_main_mean", ascending=False)
        for _, r in sub_p2.iterrows():
            row = {
                "task": task, "metric": TASK_METRIC[task],
                "method": r["method"], "kind": r["kind"],
                "phase2_mean": r["test_main_mean"], "phase2_std": r["test_main_std"],
                "phase1_top_overall": top_overall["test_main_mean"],
                "phase1_top_overall_feature": top_overall["feature"],
                "delta_vs_phase1_overall": r["test_main_mean"] - top_overall["test_main_mean"],
                "phase1_top_bfm": top_bfm["test_main_mean"] if top_bfm is not None else np.nan,
                "phase1_top_bfm_feature": top_bfm["feature"] if top_bfm is not None else "",
                "delta_vs_phase1_bfm": (r["test_main_mean"] - top_bfm["test_main_mean"]) if top_bfm is not None else np.nan,
            }
            rows.append(row)
    return pd.DataFrame(rows)


def joint_vs_brainonly(agg: pd.DataFrame) -> pd.DataFrame:
    g = agg.groupby(["task", "kind"]).agg(
        method_count=("method", "size"),
        max_mean=("test_main_mean", "max"),
        mean_mean=("test_main_mean", "mean"),
        std_of_means=("test_main_mean", "std"),
    ).reset_index()
    pv = g.pivot_table(index="task", columns="kind", values=["max_mean", "mean_mean"])
    pv.columns = [f"{c[1]}_{c[0]}" for c in pv.columns]
    pv = pv.reset_index()
    if "joint_max_mean" in pv and "brain_only_max_mean" in pv:
        pv["delta_max_joint_minus_brainonly"] = pv["joint_max_mean"] - pv["brain_only_max_mean"]
    return pv


# ============================================================
# Figures
# ============================================================

def _annotate_bars(ax, bars, means, stds, fontsize=6.5):
    for bar, m, s in zip(bars, means, stds):
        h = bar.get_height()
        s_disp = 0.0 if pd.isna(s) else s
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.005,
                f"{m:.3f}\n(±{s_disp:.3f})", ha="center", va="bottom",
                fontsize=fontsize, color="#252525", linespacing=0.95)


def fig_ranking_per_task(agg: pd.DataFrame, ref: pd.DataFrame):
    bfm_features = {"SwiFT_NewE96", "Brain-JEPA", "NeuroSTORM"}
    for task in TASKS:
        sub = agg[agg["task"] == task].sort_values("test_main_mean", ascending=False).copy()
        if sub.empty:
            continue
        n = len(sub)
        colors = [PALETTE["joint"] if k == "joint" else PALETTE["brain_only"] for k in sub["kind"]]
        means = sub["test_main_mean"].values
        stds = sub["test_main_std"].fillna(0).values
        labels = sub["method"].tolist()

        fig, ax = plt.subplots(figsize=(max(7, n * 0.8), 4.6))
        x = np.arange(n)
        bars = ax.bar(x, means, yerr=stds, color=colors, edgecolor="#252525",
                      linewidth=0.4, capsize=2.5, width=0.7,
                      error_kw={"linewidth": 0.6, "ecolor": "#252525"})
        _annotate_bars(ax, bars, means, stds)
        # Phase 1 reference lines
        if not ref.empty:
            sub_ref = ref[ref["task"] == task]
            if len(sub_ref) > 0:
                top = sub_ref.sort_values("test_main_mean", ascending=False).iloc[0]
                ax.axhline(top["test_main_mean"], color=PALETTE["phase1_top"],
                           linestyle="--", linewidth=0.8,
                           label=f"Phase 1 top: {top['feature']} ({top['test_main_mean']:.3f})")
                bfm_sub = sub_ref[sub_ref["feature"].isin(bfm_features)]
                if len(bfm_sub) > 0:
                    bt = bfm_sub.sort_values("test_main_mean", ascending=False).iloc[0]
                    ax.axhline(bt["test_main_mean"], color=PALETTE["phase1_bfm"],
                               linestyle=":", linewidth=0.8,
                               label=f"Phase 1 top BFM: {bt['feature']} ({bt['test_main_mean']:.3f})")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.set_ylabel(TASK_METRIC[task])
        ax.set_title(f"Phase 2 ranking — {task}")
        ax.legend(loc="lower left", frameon=False)
        ymax = max(means.max(), ref["test_main_mean"].max() if not ref.empty else 0) * 1.18
        ax.set_ylim(0, ymax if ymax > 0 else 1.0)
        fig.tight_layout()
        out = FIGS / f"ranking_{task}.png"
        fig.savefig(out); plt.close(fig)
        print(f"  wrote {out}")


def fig_joint_vs_brainonly(agg: pd.DataFrame):
    rows = []
    for task in TASKS:
        sub = agg[agg["task"] == task]
        for kind in ["joint", "brain_only"]:
            s = sub[sub["kind"] == kind]
            if len(s):
                top = s.sort_values("test_main_mean", ascending=False).iloc[0]
                rows.append({"task": task, "kind": kind,
                             "method": top["method"],
                             "mean": top["test_main_mean"],
                             "std": top["test_main_std"] or 0.0})
    if not rows:
        return
    d = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(7.5, 4))
    x = np.arange(len(TASKS))
    w = 0.36
    joint = d[d["kind"] == "joint"].set_index("task").reindex(TASKS)
    brain = d[d["kind"] == "brain_only"].set_index("task").reindex(TASKS)
    b1 = ax.bar(x - w/2, joint["mean"].values, w, yerr=joint["std"].values,
                color=PALETTE["joint"], edgecolor="#252525", linewidth=0.4,
                capsize=2.5, label="best joint")
    b2 = ax.bar(x + w/2, brain["mean"].values, w, yerr=brain["std"].values,
                color=PALETTE["brain_only"], edgecolor="#252525", linewidth=0.4,
                capsize=2.5, label="best brain-only")
    for bar, m, meth in zip(b1, joint["mean"].values, joint["method"].values):
        if pd.isna(m): continue
        ax.text(bar.get_x() + bar.get_width()/2, m + 0.01,
                f"{meth.replace('_',' ')}\n{m:.3f}", ha="center", va="bottom",
                fontsize=6.5, color="#252525")
    for bar, m, meth in zip(b2, brain["mean"].values, brain["method"].values):
        if pd.isna(m): continue
        ax.text(bar.get_x() + bar.get_width()/2, m + 0.01,
                f"{meth.replace('BrainOnly_','').replace('_',' ')}\n{m:.3f}",
                ha="center", va="bottom", fontsize=6.5, color="#252525")
    ax.set_xticks(x); ax.set_xticklabels(TASKS)
    ax.set_ylabel("Test main metric")
    ax.set_title("Phase 2: best joint vs best brain-only per task")
    ax.legend(frameon=False, loc="lower right")
    ax.set_ylim(0, 1.15)
    fig.tight_layout()
    out = FIGS / "joint_vs_brainonly.png"
    fig.savefig(out); plt.close(fig)
    print(f"  wrote {out}")


def fig_method_heatmap(agg: pd.DataFrame):
    pv = agg.pivot_table(index="method", columns="task",
                         values="test_main_mean").reindex(columns=TASKS)
    if pv.empty:
        return
    # Order rows: joint group first, brain-only after
    joint_methods = sorted([m for m in pv.index if not m.startswith("BrainOnly_")])
    brain_methods = sorted([m for m in pv.index if m.startswith("BrainOnly_")])
    pv = pv.reindex(joint_methods + brain_methods)

    fig, ax = plt.subplots(figsize=(6.2, max(3.5, 0.35 * len(pv))))
    im = ax.imshow(pv.values, aspect="auto", cmap="viridis", vmin=0.4, vmax=1.0)
    ax.set_xticks(range(len(TASKS))); ax.set_xticklabels(TASKS)
    ax.set_yticks(range(len(pv))); ax.set_yticklabels(pv.index)
    for i in range(len(pv)):
        for j in range(len(TASKS)):
            v = pv.values[i, j]
            if not pd.isna(v):
                color = "white" if v < 0.7 else "black"
                ax.text(j, i, f"{v:.3f}", ha="center", va="center",
                        fontsize=6.5, color=color)
    ax.axhline(len(joint_methods) - 0.5, color="white", linewidth=1.0)
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Test main metric", fontsize=7)
    ax.set_title("Phase 2 method × task heatmap")
    fig.tight_layout()
    out = FIGS / "method_heatmap.png"
    fig.savefig(out); plt.close(fig)
    print(f"  wrote {out}")


# ============================================================
# Main
# ============================================================

def main():
    print("=== Phase 2 unified analysis ===")
    df = load_all()
    print(f"loaded {len(df)} rows across {df['method'].nunique()} methods, {df['task'].nunique()} tasks")
    agg = aggregate(df)
    agg.to_csv(RES2 / "_phase2_benchmark_per_task.csv", index=False)
    print(f"  wrote {RES2 / '_phase2_benchmark_per_task.csv'}  ({len(agg)} rows)")

    ref = load_phase1_reference()
    cmp_df = vs_phase1(agg, ref)
    cmp_df.to_csv(RES2 / "_phase2_vs_phase1_best.csv", index=False)
    print(f"  wrote {RES2 / '_phase2_vs_phase1_best.csv'}  ({len(cmp_df)} rows)")

    jvb = joint_vs_brainonly(agg)
    jvb.to_csv(RES2 / "_phase2_joint_vs_brainonly.csv", index=False)
    print(f"  wrote {RES2 / '_phase2_joint_vs_brainonly.csv'}  ({len(jvb)} rows)")

    fig_ranking_per_task(agg, ref)
    fig_joint_vs_brainonly(agg)
    fig_method_heatmap(agg)

    # Summary table to stdout
    print("\n=== Best per task (Phase 2) ===")
    for t in TASKS:
        sub = agg[agg["task"] == t].sort_values("test_main_mean", ascending=False)
        if sub.empty:
            continue
        top = sub.iloc[0]
        print(f"  {t:10s} ({TASK_METRIC[t]:>10s})  best={top['method']:<32s} {top['test_main_mean']:.3f} ± {top['test_main_std'] or 0:.3f}")

    print("\n=== Joint vs brain-only (max across methods) ===")
    print(jvb.to_string(index=False))

    if not cmp_df.empty:
        print("\n=== Delta vs Phase 1 top-overall (positive = Phase 2 wins) ===")
        wide = cmp_df.pivot_table(index="method", columns="task",
                                  values="delta_vs_phase1_overall").reindex(columns=TASKS)
        print(wide.round(3).to_string())


if __name__ == "__main__":
    main()
