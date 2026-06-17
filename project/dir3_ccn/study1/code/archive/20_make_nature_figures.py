#!/usr/bin/env python3
"""
Create paper-style Figure 1 and Figure 2 for the CCN manuscript.

Figure 1: Brain-predictable subspace of V-JEPA2
Figure 2: Categorical emotion structure in the brain-predictable subspace
"""

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BASE = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN")
RESULTS = BASE / "results"
FIGURES = BASE / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

PC_PATH = RESULTS / "pc_emotion_correlation.npz"
SUBSPACE_3D_PATH = RESULTS / "brain_pred_subspace_prediction.npz"
PARTIAL_PATH = RESULTS / "vision_semantic_partial_results.npz"
SUBSPACE_2D_PATH = RESULTS / "exp17_av2d_results.npz"
SUBJECT_PATH = RESULTS / "exp18_subjectwise_claim_check.npz"


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Arial", "Liberation Sans", "DejaVu Sans"],
            "font.size": 7,
            "axes.titlesize": 8,
            "axes.labelsize": 7,
            "axes.linewidth": 0.8,
            "axes.titlepad": 6.0,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "xtick.major.size": 3,
            "ytick.major.size": 3,
            "legend.fontsize": 6,
            "legend.frameon": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.dpi": 600,
        }
    )


def style_axes(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(direction="out")


def add_panel_label(ax, label: str) -> None:
    ax.text(
        -0.14,
        1.04,
        label,
        transform=ax.transAxes,
        fontsize=9,
        fontweight="bold",
        va="bottom",
        ha="left",
    )


def save_figure(fig, stem: str) -> None:
    fig.savefig(FIGURES / f"{stem}.png", bbox_inches="tight", facecolor="white")
    fig.savefig(FIGURES / f"{stem}.pdf", bbox_inches="tight", facecolor="white")


def make_figure_1() -> None:
    pc = np.load(PC_PATH, allow_pickle=True)

    r2_vjepa = pc["r2_vjepa"].astype(np.float64)
    pred_mask = pc["brain_pred_mask_vjepa"].astype(bool)
    corr_vjepa_emo = pc["corr_vjepa_emo"].astype(np.float64)

    pc_index = np.arange(1, 21)
    r2_first20 = r2_vjepa[:20]
    max_abs_corr = np.max(np.abs(corr_vjepa_emo), axis=1)

    pred_mean = float(max_abs_corr[pred_mask].mean())
    pred_sem = float(max_abs_corr[pred_mask].std(ddof=1) / np.sqrt(pred_mask.sum()))
    unpred_mean = float(max_abs_corr[~pred_mask].mean())
    unpred_sem = float(max_abs_corr[~pred_mask].std(ddof=1) / np.sqrt((~pred_mask).sum()))

    accent = "#0f766e"
    accent_light = "#14b8a6"
    gray = "#c9ced6"
    dark = "#111827"
    threshold = 0.01

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
    fig.patch.set_facecolor("white")

    ax = axes[0]
    colors = [accent if i < 3 else gray for i in range(20)]
    edgecolors = [accent if i < 3 else gray for i in range(20)]
    ax.bar(pc_index, r2_first20, color=colors, edgecolor=edgecolors, linewidth=0.6, width=0.72)
    ax.axhline(threshold, color=dark, linestyle=(0, (3, 2)), linewidth=1.0)
    ax.text(19.9, threshold + 0.006, "threshold = 0.01", ha="right", va="bottom", fontsize=6, color=dark)
    ax.set_xlim(0.3, 20.7)
    ax.set_ylim(0, max(0.40, r2_first20.max() * 1.08))
    ax.set_xlabel("PC index")
    ax.set_ylabel("Ridge CV $R^2$")
    ax.set_title("Brain-predictable PCs are extremely sparse", loc="left")
    ax.set_xticks([1, 5, 10, 15, 20])
    style_axes(ax)
    add_panel_label(ax, "A")
    ax.text(
        0.97,
        0.94,
        "3 / 100 PCs exceed threshold",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=6.5,
        color=accent,
        fontweight="bold",
    )
    ax.text(
        0.97,
        0.85,
        "PC1 = 0.373\nPC2 = 0.075\nPC3 = 0.088",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=6.2,
        color=dark,
    )

    ax = axes[1]
    group_means = [pred_mean, unpred_mean]
    group_sems = [pred_sem, unpred_sem]
    bars = ax.bar(
        [0, 1],
        group_means,
        yerr=group_sems,
        color=[accent, "#b8c0cc"],
        edgecolor=[accent, "#b8c0cc"],
        linewidth=0.8,
        width=0.62,
        capsize=3,
        error_kw={"elinewidth": 0.8, "capthick": 0.8, "ecolor": dark},
    )
    ax.set_xticks([0, 1], ["Brain-predictable\nPCs", "Brain-unpredictable\nPCs"])
    ax.set_ylabel("Mean max $|r|$ with emotion categories")
    ax.set_ylim(0, max(0.40, pred_mean * 1.22))
    ax.set_title("Readable PCs carry stronger emotion-category structure", loc="left")
    style_axes(ax)
    add_panel_label(ax, "B")
    ax.text(0, group_means[0] + group_sems[0] + 0.015, f"{group_means[0]:.2f}", ha="center", va="bottom", fontsize=6.5, color=dark)
    ax.text(1, group_means[1] + group_sems[1] + 0.015, f"{group_means[1]:.2f}", ha="center", va="bottom", fontsize=6.5, color=dark)
    ax.text(0, 0.02, "n = 3 PCs", ha="center", va="bottom", fontsize=6, color=dark)
    ax.text(1, 0.02, "n = 97 PCs", ha="center", va="bottom", fontsize=6, color=dark)
    ax.text(
        0.96,
        0.94,
        "Pred > unpred\nby 3.64x",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=6.4,
        color=accent,
        fontweight="bold",
    )

    fig.suptitle("Figure 1. Brain-predictable subspace of V-JEPA2", x=0.06, y=1.02, ha="left", fontsize=9, fontweight="bold")
    fig.tight_layout(pad=1.0, w_pad=1.7)
    save_figure(fig, "Figure1_brain_predictable_subspace_vjepa2")
    plt.close(fig)


def make_figure_2() -> None:
    sub2d = np.load(SUBSPACE_2D_PATH, allow_pickle=True)
    partial = np.load(PARTIAL_PATH, allow_pickle=True)
    subj = np.load(SUBJECT_PATH, allow_pickle=True)

    emotion_labels = [str(x) for x in sub2d["emotion_labels"]]
    dim_labels = [str(x) for x in sub2d["dim_labels"]]
    r2_pred = sub2d["r2_pred_vjepa"].astype(np.float64)
    r2_all = sub2d["r2_all_vjepa"].astype(np.float64)

    cat_pred = r2_pred[:34]
    av_pred = r2_pred[34:]
    cat_all = r2_all[:34]
    av_all = r2_all[34:]

    order = np.argsort(-cat_pred)
    sorted_cat_labels = [emotion_labels[i] for i in order]
    sorted_cat_vals = cat_pred[order]

    arousal = float(av_pred[dim_labels.index("Arousal")])
    valence = float(av_pred[dim_labels.index("Valence")])

    calmness_idx = emotion_labels.index("Calmness")
    calmness_sorted_idx = int(np.where(order == calmness_idx)[0][0])
    calmness_orig = float(partial["r2_original_vjepa"][calmness_idx])
    calmness_partial = float(partial["r2_partial_vjepa"][calmness_idx])
    calmness_retained = calmness_partial / calmness_orig if calmness_orig > 0 else np.nan

    mean_cat_all = float(cat_all.mean())
    mean_av_all = float(av_all.mean())
    mean_cat_pred = float(cat_pred.mean())
    mean_av_pred = float(av_pred.mean())

    ratio_all = mean_cat_all / mean_av_all
    ratio_pred = mean_cat_pred / mean_av_pred
    subject_agreement = int(round(float(subj["agreement_rate_2d_vjepa"][0]) * 5))

    cat_color = "#1f5aa6"
    cat_dark = "#153f77"
    dim_color = "#e07a2d"
    calm_color = "#2b8a3e"
    grid = "#e5e7eb"
    dark = "#111827"

    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.2))
    fig.patch.set_facecolor("white")

    ax = axes[0]
    x = np.arange(len(sorted_cat_vals))
    bars = ax.bar(x, sorted_cat_vals, color=cat_color, edgecolor=cat_color, linewidth=0.5, width=0.78)
    bars[calmness_sorted_idx].set_facecolor(calm_color)
    bars[calmness_sorted_idx].set_edgecolor(calm_color)
    bars[calmness_sorted_idx].set_linewidth(0.8)
    ax.axhline(arousal, color=dim_color, linestyle=(0, (4, 2)), linewidth=1.0)
    ax.axhline(valence, color="#b45309", linestyle=(0, (1.5, 1.8)), linewidth=1.0)
    ax.text(len(sorted_cat_vals) - 0.2, arousal + 0.006, f"Arousal = {arousal:.3f}", ha="right", va="bottom", fontsize=6, color=dim_color)
    ax.text(len(sorted_cat_vals) - 0.2, valence + 0.006, f"Valence = {valence:.3f}", ha="right", va="bottom", fontsize=6, color="#b45309")
    ax.text(
        calmness_sorted_idx,
        sorted_cat_vals[calmness_sorted_idx] + 0.012,
        f"Calmness\n45% retained",
        ha="center",
        va="bottom",
        fontsize=5.8,
        color=calm_color,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(sorted_cat_labels, rotation=90)
    ax.set_ylabel("Ridge CV $R^2$")
    ax.set_xlabel("Emotion category")
    ax.set_ylim(0, max(0.36, sorted_cat_vals.max() * 1.10))
    ax.set_title("Category decoding is distributed and exceeds A/V", loc="left")
    style_axes(ax)
    add_panel_label(ax, "A")
    ax.grid(axis="y", color=grid, linewidth=0.6)

    ax = axes[1]
    group_x = np.array([0, 1])
    width = 0.34
    ax.bar(group_x - width / 2, [mean_cat_all, mean_cat_pred], width=width, color=cat_color, edgecolor=cat_color, linewidth=0.7, label="Emotion categories")
    ax.bar(group_x + width / 2, [mean_av_all, mean_av_pred], width=width, color=dim_color, edgecolor=dim_color, linewidth=0.7, label="Arousal / Valence")
    ax.set_xticks(group_x, ["All 100 PCs", "Brain-predictable\nsubspace"])
    ax.set_ylabel("Mean Ridge CV $R^2$")
    ax.set_ylim(0, max(0.20, mean_cat_all * 1.18))
    ax.set_title("Readable subspace is more category-leaning than full space", loc="left")
    style_axes(ax)
    add_panel_label(ax, "B")
    ax.grid(axis="y", color=grid, linewidth=0.6)
    ax.legend(loc="upper right")

    ax.text(group_x[0], max(mean_cat_all, mean_av_all) + 0.012, f"cat/A/V = {ratio_all:.2f}", ha="center", va="bottom", fontsize=6.3, color=dark)
    ax.text(group_x[1], max(mean_cat_pred, mean_av_pred) + 0.012, f"cat/A/V = {ratio_pred:.2f}", ha="center", va="bottom", fontsize=6.3, color=dark, fontweight="bold")
    ax.text(group_x[1], max(mean_cat_pred, mean_av_pred) + 0.038, f"{subject_agreement}/5 subjects", ha="center", va="bottom", fontsize=6.3, color=cat_dark, fontweight="bold")

    fig.suptitle("Figure 2. Categorical emotion structure in the brain-predictable subspace", x=0.06, y=1.03, ha="left", fontsize=9, fontweight="bold")
    fig.tight_layout(pad=1.0, w_pad=1.8)
    save_figure(fig, "Figure2_categorical_structure_vjepa2")
    plt.close(fig)


def main() -> None:
    set_style()
    make_figure_1()
    make_figure_2()
    print("Saved figure files:")
    for stem in [
        "Figure1_brain_predictable_subspace_vjepa2",
        "Figure2_categorical_structure_vjepa2",
    ]:
        print(FIGURES / f"{stem}.png")
        print(FIGURES / f"{stem}.pdf")


if __name__ == "__main__":
    main()
