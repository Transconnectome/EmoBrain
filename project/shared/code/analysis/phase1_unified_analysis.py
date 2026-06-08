"""
FEELIN Phase 1 unified analysis (Nature-style figures).

모든 probe CSV (chance, ROI, BFM main, SwiFT padding ablation, video) 결합.
Output:
  results/phase1/_unified_ranking_per_task.csv
  results/phase1/_best_conditions_per_task.csv
  results/phase1/_swift_padding_ablation_summary.csv
  results/phase1/_mode_comparison.csv
  figures/phase1/ranking_<task>.png   (4 task, Nature style + value labels)
  figures/phase1/padding_ablation.png (5 padding x 2 init x 4 task)
  figures/phase1/mode_comparison.png
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

# ============================================================
# Nature-style rcParams
# ============================================================
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
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": False,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# Muted Nature-like palette
NATURE_COLORS = {
    "chance":  "#9E9E9E",   # grey
    "roi":     "#6BAED6",   # soft blue
    "bfm":     "#3182BD",   # mid blue
    "video_p": "#E6550D",   # warm orange (pretrained)
    "video_s": "#FDAE6B",   # pale orange (scratch)
    "caption": "#A1D99B",   # green for caption
    "best":    "#252525",   # near-black for highlights
}

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
RESULTS = FEELIN / "project/shared/results/phase1"
FIGS = FEELIN / "figures/phase1"
FIGS.mkdir(parents=True, exist_ok=True)

TASKS = ["V_binary", "A_binary", "V_reg", "A_reg"]
TASK_METRIC = {"V_binary": "AUROC", "A_binary": "AUROC",
               "V_reg": "Pearson r", "A_reg": "Pearson r"}

SOURCE_FILES = {
    "chance":         ["chance_baseline.csv"],
    "ROI":            ["bfm_probe_ROI_Schaefer400Tian50.csv"],
    "SwiFT_NewE96":   ["bfm_probe_SwiFT_NewE96.csv"],
    "Brain-JEPA":     ["bfm_probe_Brain-JEPA.csv"],
    "NeuroSTORM":     ["bfm_probe_NeuroSTORM.csv"],
    "swift_pad_abl":  [f"swift_padding_ablation_{t}.csv" for t in TASKS],
    "swift_pad_cyc":  [f"swift_padding_cyclic_only_{t}.csv" for t in TASKS],
    # SwiFT 5 variants (zero padding extraction) per-task CSV
    "swift_variants": [f"bfm_probe_SwiFT_{v}_zero_{t}.csv"
                       for v in ["NewE36", "NewE192", "UAH_5M", "UAH_51M", "UAH_202M"]
                       for t in TASKS],
    "video":          ["video_probe_V-JEPA2.csv", "video_probe_CLIP.csv",
                       "video_probe_DINOv2.csv", "video_probe_VideoMAE.csv",
                       "video_probe_Qwen-VL_caption.csv"],
}


def load_all() -> pd.DataFrame:
    dfs = []
    for group, files in SOURCE_FILES.items():
        for f in files:
            p = RESULTS / f
            if not p.exists():
                print(f"  [WARN] missing {p}")
                continue
            d = pd.read_csv(p, keep_default_na=False, na_values=[""])
            d["source_group"] = group
            d["source_file"] = f
            dfs.append(d)
    df = pd.concat(dfs, ignore_index=True)
    df = df[df["task"].isin(TASKS)].copy()
    return df


def unified_ranking(df: pd.DataFrame) -> pd.DataFrame:
    grp = ["task", "feature", "init", "padding", "head", "mode"]
    g = df.groupby(grp, dropna=False).agg(
        test_main_mean=("test_main", "mean"),
        test_main_std=("test_main", "std"),
        count=("test_main", "size"),
    ).reset_index()
    g["is_swift_pad_abl"] = (g["feature"] == "SwiFT_NewE96") & (g["padding"].isin(["replicate", "zero", "spatial_only", "cyclic_replicate"]))
    return g


def best_per_task(rank: pd.DataFrame, top_k: int = 8) -> pd.DataFrame:
    rows = []
    for task in TASKS:
        sub = rank[rank["task"] == task].sort_values("test_main_mean", ascending=False).head(top_k).copy()
        sub.insert(0, "rank", range(1, len(sub) + 1))
        rows.append(sub)
    return pd.concat(rows, ignore_index=True)


def padding_ablation_table(rank: pd.DataFrame) -> pd.DataFrame:
    df = rank[rank["feature"] == "SwiFT_NewE96"].copy()
    g = df.groupby(["task", "padding", "init"], dropna=False).agg(
        mean=("test_main_mean", "mean"),
        std=("test_main_mean", "std"),
        count=("test_main_mean", "size"),
    ).reset_index()
    return g


def mode_comparison(rank: pd.DataFrame) -> pd.DataFrame:
    df = rank[rank["mode"].isin(["pooled", "per_subject"])].copy()
    g = df.groupby(["task", "feature", "init", "padding", "head", "mode"], dropna=False).agg(
        mean=("test_main_mean", "mean"),
    ).reset_index()
    pv = g.pivot_table(index=["task", "feature", "init", "padding", "head"],
                       columns="mode", values="mean").reset_index()
    if "pooled" in pv.columns and "per_subject" in pv.columns:
        pv["delta_pooled_minus_persubj"] = pv["pooled"] - pv["per_subject"]
    return pv


# ============================================================
# Figures
# ============================================================

def _color_for(feature: str) -> str:
    if feature == "chance":
        return NATURE_COLORS["chance"]
    if feature.startswith("ROI"):
        return NATURE_COLORS["roi"]
    if feature in {"SwiFT_NewE96", "Brain-JEPA", "NeuroSTORM"}:
        return NATURE_COLORS["bfm"]
    if feature == "Qwen-VL_caption":
        return NATURE_COLORS["caption"]
    if "_scratch" in feature:
        return NATURE_COLORS["video_s"]
    return NATURE_COLORS["video_p"]


def _annotate_bars(ax, bars, means, stds, fontsize=6.5):
    """Print 'mean (sigma)' above each bar."""
    for bar, m, s in zip(bars, means, stds):
        h = bar.get_height()
        s_disp = 0.0 if pd.isna(s) else s
        label = f"{m:.3f}\n(±{s_disp:.3f})"
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.005,
                label, ha="center", va="bottom", fontsize=fontsize,
                color="#252525", linespacing=0.95)


def fig_ranking_per_task(rank: pd.DataFrame):
    for task in TASKS:
        sub = rank[(rank["task"] == task) & (~rank["is_swift_pad_abl"])].copy()
        best = sub.sort_values("test_main_mean", ascending=False).groupby(
            ["feature", "init"], as_index=False).first()
        best = best.sort_values("test_main_mean", ascending=False)
        best["label"] = best.apply(
            lambda r: f"{r['feature']}/{r['init']}"
            if r["init"] != "n/a" else r["feature"], axis=1,
        )
        colors = best["feature"].apply(_color_for).tolist()
        n = len(best)

        fig, ax = plt.subplots(figsize=(max(7.2, n * 0.55), 4.5))
        x = np.arange(n)
        means = best["test_main_mean"].values
        stds = best["test_main_std"].fillna(0).values
        bars = ax.bar(x, means, yerr=stds, color=colors,
                      edgecolor="#252525", linewidth=0.4,
                      capsize=2.5, error_kw={"linewidth": 0.6, "ecolor": "#252525"},
                      width=0.7)
        _annotate_bars(ax, bars, means, stds, fontsize=6.5)
        ax.set_xticks(x)
        ax.set_xticklabels(best["label"].tolist(), rotation=45, ha="right", fontsize=7)
        ax.set_ylabel(TASK_METRIC[task], fontsize=8)
        ax.set_title(f"{task} (best per feature)", fontsize=9, loc="left", fontweight="bold")
        ax.set_ylim(0, max(means.max() + (stds.max() if len(stds) else 0) + 0.10, 1.05))

        ch = sub[sub["feature"] == "chance"]["test_main_mean"].max() if (sub["feature"] == "chance").any() else None
        if ch is not None and not pd.isna(ch):
            ax.axhline(ch, color="#9E9E9E", ls=(0, (3, 2)), lw=0.7)
            ax.text(n - 0.5, ch, f"  chance = {ch:.3f}", color="#9E9E9E",
                    fontsize=6.5, va="center", ha="right")

        # Category legend
        legend_handles = [
            plt.Rectangle((0, 0), 1, 1, color=NATURE_COLORS["chance"], label="chance"),
            plt.Rectangle((0, 0), 1, 1, color=NATURE_COLORS["roi"],    label="ROI baseline"),
            plt.Rectangle((0, 0), 1, 1, color=NATURE_COLORS["bfm"],    label="brain foundation model"),
            plt.Rectangle((0, 0), 1, 1, color=NATURE_COLORS["video_p"],label="video pretrained"),
            plt.Rectangle((0, 0), 1, 1, color=NATURE_COLORS["video_s"],label="video scratch"),
            plt.Rectangle((0, 0), 1, 1, color=NATURE_COLORS["caption"],label="caption text"),
        ]
        ax.legend(handles=legend_handles, loc="upper right", frameon=False, fontsize=6.5, ncol=2)
        plt.tight_layout()
        out = FIGS / f"ranking_{task}.png"
        plt.savefig(out, dpi=300)
        plt.close()
        print(f"  saved {out}")


def fig_padding_ablation(rank: pd.DataFrame):
    df = rank[rank["feature"] == "SwiFT_NewE96"].copy()
    g = df.groupby(["task", "padding", "init"], dropna=False).agg(
        mean=("test_main_mean", "mean"),
        std=("test_main_mean", "std"),
    ).reset_index()
    pads_canonical = ["mean", "replicate", "zero", "spatial_only", "cyclic_replicate"]
    pads = [p for p in pads_canonical if p in g["padding"].unique()]
    inits = ["resting", "scratch"]
    init_color = {"resting": "#3182BD", "scratch": "#9ECAE1"}

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), sharex=True)
    width = 0.36
    for ax, task in zip(axes.flat, TASKS):
        sub = g[g["task"] == task]
        x = np.arange(len(pads))
        for i, init in enumerate(inits):
            ssub = sub[sub["init"] == init].set_index("padding").reindex(pads)
            means = ssub["mean"].values
            stds = ssub["std"].fillna(0).values
            offset = (i - 0.5) * width
            bars = ax.bar(x + offset, means, yerr=stds, width=width,
                          color=init_color[init], edgecolor="#252525",
                          linewidth=0.4, capsize=2.5,
                          error_kw={"linewidth": 0.6, "ecolor": "#252525"},
                          label=init)
            for bar, m, s in zip(bars, means, stds):
                if pd.isna(m):
                    continue
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.003,
                        f"{m:.3f}\n(±{s:.3f})",
                        ha="center", va="bottom", fontsize=6,
                        color="#252525", linespacing=0.95)
        ax.set_xticks(x)
        ax.set_xticklabels(pads, fontsize=7, rotation=15, ha="right")
        ax.set_ylabel(TASK_METRIC[task], fontsize=8)
        ax.set_title(task, fontsize=9, loc="left", fontweight="bold")
        ax.legend(frameon=False, fontsize=7, loc="upper right")
        # extend y for labels
        yhi = sub["mean"].max() + sub["std"].fillna(0).max() + 0.06
        ax.set_ylim(0, max(yhi, 0.1))
    fig.suptitle("SwiFT NewE96 padding ablation (averaged over head, mode, subject, fold)",
                 fontsize=10, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    out = FIGS / "padding_ablation.png"
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"  saved {out}")


def fig_mode_comparison(mode_df: pd.DataFrame):
    df = mode_df.dropna(subset=["pooled", "per_subject"]).copy()
    fig, axes = plt.subplots(1, 4, figsize=(13.5, 3.6))
    for ax, task in zip(axes, TASKS):
        sub = df[df["task"] == task]
        feats = sorted(sub["feature"].unique())
        # color BFMs distinctly
        feat_color = {
            "SwiFT_NewE96": "#3182BD",
            "Brain-JEPA": "#08519C",
            "NeuroSTORM": "#6BAED6",
            "ROI_Schaefer400Tian50": "#FD8D3C",
        }
        for f in feats:
            ssub = sub[sub["feature"] == f]
            ax.scatter(ssub["per_subject"], ssub["pooled"],
                       label=f.replace("_Schaefer400Tian50", " (ROI 450)"),
                       color=feat_color.get(f, "#9E9E9E"),
                       s=22, alpha=0.85, edgecolor="#252525", linewidth=0.3)
        lo = min(sub["per_subject"].min(), sub["pooled"].min())
        hi = max(sub["per_subject"].max(), sub["pooled"].max())
        pad = (hi - lo) * 0.08
        ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], color="#252525",
                ls=(0, (3, 2)), lw=0.6)
        ax.set_xlabel("per-subject mean", fontsize=7.5)
        ax.set_ylabel("pooled mean", fontsize=7.5)
        ax.set_title(f"{task} ({TASK_METRIC[task]})", fontsize=8.5, loc="left", fontweight="bold")
        ax.legend(frameon=False, fontsize=6, loc="upper left")
        ax.set_xlim(lo - pad, hi + pad)
        ax.set_ylim(lo - pad, hi + pad)
    fig.suptitle("Pooled vs per-subject mode (above the diagonal: pooled wins)",
                 fontsize=10, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    out = FIGS / "mode_comparison.png"
    plt.savefig(out, dpi=300)
    plt.close()
    print(f"  saved {out}")


def main():
    print("=== Loading all CSVs ===")
    df = load_all()
    print(f"  total rows after task filter: {len(df)}")

    print("\n=== Unified ranking ===")
    rank = unified_ranking(df)
    rank.to_csv(RESULTS / "_unified_ranking_per_task.csv", index=False)
    print(f"  saved (cells: {len(rank)})")

    print("\n=== Best per task ===")
    best = best_per_task(rank, top_k=8)
    best.to_csv(RESULTS / "_best_conditions_per_task.csv", index=False)

    print("\n=== SwiFT padding ablation summary ===")
    pad = padding_ablation_table(rank)
    pad.to_csv(RESULTS / "_swift_padding_ablation_summary.csv", index=False)

    print("\n=== Mode comparison ===")
    mode_df = mode_comparison(rank)
    mode_df.to_csv(RESULTS / "_mode_comparison.csv", index=False)

    print("\n=== Figures ===")
    fig_ranking_per_task(rank)
    fig_padding_ablation(rank)
    fig_mode_comparison(mode_df)

    print(f"\n[done]")


if __name__ == "__main__":
    main()
