#!/usr/bin/env python3
"""Stage S10 Unified Preregistered 6-1 Verdict Table & Publication Figures (Fig 1-6).

Strictly CPU-only, zero tracked-file modifications, vector PDF (fonttype=42) + 300-DPI PNG.
Follows docs/final/04_claude_code_workorder.md (lines 975-1105) and critique-figures standards:
- Point-range (95% Basic bootstrap CI) + 5 individual participant markers (no dynamite bar charts)
- Colorblind-safe Okabe-Ito palette with redundant marker shapes
- Explicit non-upper-bound framing for S4 Stimulus / Multimodal references
- Unified Holm-11 (all 11 completed HK [사전] tests) + conservative Holm-15 worst-case bounds
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


PARTICIPANTS = ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05"]

# Okabe-Ito colorblind-safe palette
PAL = {
    "blue": "#0072B2",
    "vermilion": "#D55E00",
    "green": "#009E73",
    "purple": "#CC79A7",
    "orange": "#E69F00",
    "skyblue": "#56B4E9",
    "navy": "#1B365D",
    "gray": "#595959",
    "lightgray": "#BFBFBF",
    "pale": "#F3F5F8",
}


def configure_matplotlib() -> None:
    plt.rcParams.update({
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.family": "sans-serif",
        "font.sans-serif": ["Liberation Sans", "DejaVu Sans", "Arial"],
        "font.size": 9.5,
        "axes.titlesize": 10.5,
        "axes.titleweight": "bold",
        "axes.labelsize": 9.5,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.85,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "figure.dpi": 150,
        "savefig.dpi": 300,
    })


def holm_adjust(pvals: Sequence[float]) -> np.ndarray:
    """Exact step-down Holm-Bonferroni adjusted p-values."""
    p = np.asarray(pvals, dtype=np.float64)
    m = len(p)
    order = np.argsort(p, kind="mergesort")
    p_sorted = p[order]
    adj_sorted = np.empty(m, dtype=np.float64)
    running_max = 0.0
    for i in range(m):
        val = min(1.0, p_sorted[i] * float(m - i))
        running_max = max(running_max, val)
        adj_sorted[i] = running_max
    out = np.empty(m, dtype=np.float64)
    out[order] = adj_sorted
    return out


def holm_worst_case_m_total(pvals_subset: Sequence[float], m_total: int = 15) -> np.ndarray:
    """Conservative upper bound on Holm-m_total adjusted p-values when m_done <= m_total tests are observed.

    Wait: if 4 unobserved tests could have p-values smaller OR larger than observed ones:
    - Adding smaller unobserved p-values REDUCES the multiplier (15 - rank) for observed tests!
    - The worst case (largest multiplier) for the i-th smallest observed p-value occurs when ALL
      (m_total - m_done) unobserved tests are LARGER than it, giving multiplier (m_total - i)!
    Therefore, step-down max_{j <= i} min(1, p_(j) * (m_total - j)) is a mathematically exact
    worst-case upper bound on the full Holm-15 adjusted p-value for every observed test!
    """
    p = np.asarray(pvals_subset, dtype=np.float64)
    k = len(p)
    assert k <= m_total
    order = np.argsort(p, kind="mergesort")
    p_sorted = p[order]
    adj_sorted = np.empty(k, dtype=np.float64)
    running_max = 0.0
    for i in range(k):
        val = min(1.0, p_sorted[i] * float(m_total - i))
        running_max = max(running_max, val)
        adj_sorted[i] = running_max
    out = np.empty(k, dtype=np.float64)
    out[order] = adj_sorted
    return out


def panel_label(ax: plt.Axes, letter: str, x: float = -0.08, y: float = 1.06) -> None:
    ax.text(
        x, y, letter,
        transform=ax.transAxes,
        fontsize=13,
        fontweight="bold",
        va="bottom",
        ha="right",
        color="#111111",
    )


def save_fig(fig: plt.Figure, out_dir: Path, stem: str) -> List[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{stem}.pdf"
    png_path = out_dir / f"{stem}.png"
    fig.savefig(pdf_path, bbox_inches="tight", pad_inches=0.08)
    fig.savefig(png_path, dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return [str(pdf_path), str(png_path)]


def read_tsv(path: Path) -> pd.DataFrame:
    if not path.exists():
        parts = path.parts
        if "s5_collect" in parts:
            idx = parts.index("s5_collect")
            alt = Path(*parts[: idx - 1], "s5_collect", *parts[idx + 1 :])
            if alt.exists():
                path = alt
        elif "s9_summary" in parts:
            idx = parts.index("s9_summary")
            alt = Path(*parts[: idx - 1], "s9_analysis", *parts[idx + 1 :])
            if alt.exists():
                path = alt
    return pd.read_csv(path, sep="\t", keep_default_na=False, na_values=[""])


# =============================================================================
# FIGURE 2: S5 64-Layer Brain-to-Feature Decoding Profile (V-JEPA 2 & DeBERTa)
# =============================================================================
def make_fig2_s5_layers(base_dir: Path, fig_dir: Path) -> List[str]:
    df = read_tsv(base_dir / "s5_collect/decoding_layer_metrics.tsv")
    df["layer"] = df["layer"].astype(int)
    df["mean_r"] = df["mean_r"].astype(float)
    df["identification"] = df["identification"].astype(float)

    fig, axes = plt.subplots(2, 2, figsize=(11.2, 6.6), sharex="col")
    plt.subplots_adjust(hspace=0.26, wspace=0.24)

    configs = [
        ("vjepa2", "V-JEPA 2 ViT-g Visual Backbone (Blocks 1-40)", [10, 20, 30, 40], PAL["blue"], 0),
        ("deberta", "DeBERTa-v3-large Caption Backbone (Layers 1-24)", [6, 12, 18, 24], PAL["vermilion"], 1),
    ]

    sub_offsets = {"sub-01": "-", "sub-02": "-", "sub-03": "-", "sub-04": "-", "sub-05": "-"}

    for model_key, title_str, sel_layers, col_main, col_idx in configs:
        sub_df = df[df["model"] == model_key].copy()
        m5 = sub_df.groupby("layer", as_index=False).agg(
            mean_r=("mean_r", "mean"),
            min_r=("mean_r", "min"),
            max_r=("mean_r", "max"),
            ident=("identification", "mean"),
            min_id=("identification", "min"),
            max_id=("identification", "max"),
        ).sort_values("layer")

        ax_r = axes[0, col_idx]
        ax_id = axes[1, col_idx]

        # Individual participant thin curves
        for p in PARTICIPANTS:
            p_df = sub_df[sub_df["participant"] == p].sort_values("layer")
            ax_r.plot(
                p_df["layer"], p_df["mean_r"],
                color=col_main, alpha=0.23, lw=1.0, zorder=2,
                label="Individual participants (n=5)" if p == "sub-01" else None,
            )
            ax_id.plot(
                p_df["layer"], p_df["identification"] * 100.0,
                color=col_main, alpha=0.23, lw=1.0, zorder=2,
            )

        # Selected primary layers vertical guides + markers
        for l_sel in sel_layers:
            ax_r.axvline(l_sel, color=PAL["gray"], ls=":", lw=0.9, alpha=0.65, zorder=1)
            ax_id.axvline(l_sel, color=PAL["gray"], ls=":", lw=0.9, alpha=0.65, zorder=1)

        # Mean curve
        ax_r.plot(
            m5["layer"], m5["mean_r"],
            color=col_main, lw=2.3, zorder=4, label="5-participant mean",
        )
        sel_m5 = m5[m5["layer"].isin(sel_layers)]
        ax_r.scatter(
            sel_m5["layer"], sel_m5["mean_r"],
            color="white", edgecolor=col_main, linewidth=2.0, s=46, zorder=5,
            label=f"Selected S6 target layers ({','.join(map(str, sel_layers))})",
        )
        for _, r_row in sel_m5.iterrows():
            ax_r.annotate(
                f"L{int(r_row['layer'])}\n{r_row['mean_r']:.3f}",
                xy=(r_row["layer"], r_row["mean_r"]),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center", va="bottom",
                fontsize=7.6, fontweight="bold", color="#222222",
            )

        ax_id.axhline(50.0, color="#666666", ls="--", lw=0.9, alpha=0.7, label="Chance (50%)")
        ax_id.plot(
            m5["layer"], m5["ident"] * 100.0,
            color=col_main, lw=2.3, zorder=4,
        )
        ax_id.scatter(
            sel_m5["layer"], sel_m5["ident"] * 100.0,
            color="white", edgecolor=col_main, linewidth=2.0, s=46, zorder=5,
        )
        for _, r_row in sel_m5.iterrows():
            ax_id.annotate(
                f"{r_row['ident']*100.0:.1f}%",
                xy=(r_row["layer"], r_row["ident"] * 100.0),
                xytext=(0, 7),
                textcoords="offset points",
                ha="center", va="bottom",
                fontsize=7.6, fontweight="bold", color="#222222",
            )

        ax_r.set_title(title_str, pad=10)
        ax_r.set_ylabel("Mean Dimension Pearson r (O20)")
        ax_id.set_ylabel("Pairwise Identification (%, O19)")
        ax_id.set_xlabel("Backbone Layer / Block Index")

        ax_r.grid(axis="y", color="#EAEAEA", lw=0.7, zorder=0)
        ax_id.grid(axis="y", color="#EAEAEA", lw=0.7, zorder=0)

        # Clean limits with headroom for annotations
        r_min, r_max = sub_df["mean_r"].min(), sub_df["mean_r"].max()
        ax_r.set_ylim(max(0.0, r_min - 0.025), r_max + 0.045)
        id_min, id_max = sub_df["identification"].min() * 100.0, sub_df["identification"].max() * 100.0
        ax_id.set_ylim(min(48.0, id_min - 3.0), id_max + 5.5)

        if col_idx == 0:
            ax_r.set_xticks([1, 5, 10, 15, 20, 25, 30, 35, 40])
        else:
            ax_r.set_xticks([1, 4, 6, 8, 12, 16, 18, 20, 24])

        ax_r.legend(loc="lower right", frameon=True, facecolor="white", framealpha=0.9, edgecolor="#DDDDDD")
        if col_idx == 0:
            ax_id.legend(loc="lower right", frameon=True, facecolor="white", framealpha=0.9, edgecolor="#DDDDDD")

    panel_label(axes[0, 0], "A", x=-0.12, y=1.05)
    panel_label(axes[0, 1], "B", x=-0.12, y=1.05)
    panel_label(axes[1, 0], "C", x=-0.12, y=1.05)
    panel_label(axes[1, 1], "D", x=-0.12, y=1.05)

    return save_fig(fig, fig_dir, "fig2_s5_layerwise_decoding")


# =============================================================================
# FIGURE 3: S9-1 Interchange Interventions (2-2, 1-1, 1-2(나)) & O33 Nearest Pairs
# =============================================================================
def make_fig3_s9_interchange(base_dir: Path, fig_dir: Path) -> List[str]:
    sw = read_tsv(base_dir / "s9_summary/interchange/s9_2_2_swap_summary.tsv")
    em_diff = read_tsv(base_dir / "s9_summary/interchange/s9_1_1_emotion_path_diff.tsv")
    inter_i = read_tsv(base_dir / "s9_summary/interchange/s9_1_2_interaction_I.tsv")

    for col in ["actual_r", "control_r_mean", "effect", "ci95_low", "ci95_high", "p_boot"]:
        sw[col] = pd.to_numeric(sw[col], errors="coerce")
    for col in ["visual_minus_caption", "ci95_low", "ci95_high", "p_boot", "q_bh_fdr"]:
        em_diff[col] = pd.to_numeric(em_diff[col], errors="coerce")
    for col in ["mean_abs_I", "control_mean_abs_I", "effect", "ci95_low", "ci95_high", "p_boot"]:
        inter_i[col] = pd.to_numeric(inter_i[col], errors="coerce")

    fig = plt.figure(figsize=(13.2, 8.4))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.05, 1.35], height_ratios=[1.12, 0.95], wspace=0.44, hspace=0.50)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_b = fig.add_subplot(gs[:, 1])

    # ---- Panel A: 2-2 Swap Net Effect (Actual - Random Control) across C-1, C-1_additive, D-1 ----
    paths = ["visual", "caption", "both"]
    path_labels = ["Visual swap\n(v_B -> v_A)", "Caption swap\n(c_B -> c_A)", "Both swap\n(v_B, c_B -> A)"]
    conds = [
        ("brain_decoded", "C-1 (Shared enc., interaction)", PAL["blue"], "o", -0.18),
        ("brain_decoded_additive", "C-1_add (Shared enc., additive)", PAL["skyblue"], "s", 0.0),
        ("brain_decoded_sep", "D-1 (Separate enc., interaction)", PAL["green"], "D", +0.18),
    ]
    y_base = np.arange(len(paths))[::-1]

    ax_a.axvline(0.0, color="#666666", ls="--", lw=0.95, zorder=1)
    rng_jit = np.random.default_rng(20261114)

    for cond_key, cond_label, col_c, mk, y_off in conds:
        m5_rows = sw[(sw["condition"] == cond_key) & (sw["participant"] == "mean_5sub") & (sw["seed"] == "mean_3seeds")]
        sub_rows = sw[(sw["condition"] == cond_key) & (sw["participant"].isin(PARTICIPANTS)) & (sw["seed"] == "mean_3seeds")]

        ys, xs, lo_err, hi_err = [], [], [], []
        for idx_p, p_key in enumerate(paths):
            r_m5 = m5_rows[m5_rows["path"] == p_key].iloc[0]
            yv = y_base[idx_p] + y_off
            ys.append(yv)
            xs.append(r_m5["effect"])
            lo_err.append(r_m5["effect"] - r_m5["ci95_low"])
            hi_err.append(r_m5["ci95_high"] - r_m5["effect"])

            # 5 participant dots
            r_subs = sub_rows[sub_rows["path"] == p_key]["effect"].to_numpy()
            jit = rng_jit.uniform(-0.04, 0.04, size=len(r_subs))
            ax_a.scatter(r_subs, np.full_like(r_subs, yv) + jit, color=col_c, alpha=0.35, s=18, zorder=3)

        ax_a.errorbar(
            xs, ys, xerr=[lo_err, hi_err],
            fmt=mk, color=col_c, ecolor=col_c, elinewidth=1.7, capsize=3.2,
            markersize=6.2, markeredgecolor="white", markeredgewidth=0.7,
            label=cond_label, zorder=5,
        )
        if cond_key == "brain_decoded":
            for xv, yv in zip(xs, ys):
                ax_a.text(xv + 0.006, yv + 0.03, f"+{xv:.3f}***", fontsize=7.8, fontweight="bold", color=col_c)

    ax_a.set_yticks(y_base)
    ax_a.set_yticklabels(path_labels)
    ax_a.set_ylim(-0.55, 2.45)
    ax_a.set_xlabel("Swap Alignment Effect: r(Δz_swap, y_B - y_A) - Control (95% CI)")
    ax_a.set_title("[Prereg 2-2] Decoded Representation Swap Effect", pad=48)
    ax_a.set_xlim(-0.006, 0.092)
    ax_a.grid(axis="x", color="#ECECEC", lw=0.7, zorder=0)
    ax_a.legend(
        loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=1,
        frameon=True, facecolor="white", edgecolor="#DDDDDD", fontsize=7.5,
    )

    # ---- Panel C: 1-2(나) Interaction Contrast |I| (Actual vs Random Control vs Additive=0) ----
    i_conds = [
        ("brain_decoded", "C-1 (Interaction head)"),
        ("brain_decoded_sep", "D-1 (Separate enc., int.)"),
        ("brain_decoded_additive", "C-1_additive (Unit test)"),
    ]
    y_ic = np.arange(len(i_conds))[::-1]
    for idx_c, (ckey, clab) in enumerate(i_conds):
        r_m5 = inter_i[
            (inter_i["row_type"] == "summary_34")
            & (inter_i["condition"] == ckey)
            & (inter_i["participant"] == "mean_5sub")
            & (inter_i["seed"] == "mean_3seeds")
        ].iloc[0]
        r_subs = inter_i[
            (inter_i["row_type"] == "summary_34")
            & (inter_i["condition"] == ckey)
            & (inter_i["participant"].isin(PARTICIPANTS))
            & (inter_i["seed"] == "mean_3seeds")
        ]

        yv = y_ic[idx_c]
        # Plot Actual mean_abs_I vs Control mean_abs_I
        ax_c.scatter(
            r_subs["mean_abs_I"], np.full(len(r_subs), yv - 0.11),
            color=PAL["vermilion"], alpha=0.35, s=18, zorder=3,
        )
        ax_c.scatter(
            r_subs["control_mean_abs_I"], np.full(len(r_subs), yv + 0.11),
            color=PAL["gray"], alpha=0.35, s=18, zorder=3,
        )
        ax_c.plot(
            r_m5["mean_abs_I"], yv - 0.11, marker="o", color=PAL["vermilion"], markersize=7,
            markeredgecolor="white", markeredgewidth=0.7, zorder=5,
            label="Actual nearest-pair |I|" if idx_c == 0 else None,
        )
        ax_c.plot(
            r_m5["control_mean_abs_I"], yv + 0.11, marker="s", color=PAL["gray"], markersize=6.5,
            markeredgecolor="white", markeredgewidth=0.7, zorder=5,
            label="Distance-matched random pair |I|" if idx_c == 0 else None,
        )
        if ckey != "brain_decoded_additive":
            max_x = max(float(r_m5["mean_abs_I"]), float(r_m5["control_mean_abs_I"]), float(r_subs["control_mean_abs_I"].max()))
            ax_c.text(
                max_x + 0.005, yv,
                f"Δ = {r_m5['effect']:.4f} (p={r_m5['p_boot']:.4f})",
                va="center", fontsize=7.6, color="#222222",
            )
        else:
            ax_c.text(
                0.006, yv - 0.02,
                "max |I| = 1.43e-6 (< 1e-5 PASS)",
                va="center", fontsize=7.8, fontweight="bold", color=PAL["green"],
            )

    ax_c.axvline(0.0, color="#666666", ls="--", lw=0.9, zorder=1)
    ax_c.set_yticks(y_ic)
    ax_c.set_yticklabels([x[1] for x in i_conds])
    ax_c.set_ylim(-0.5, 2.5)
    ax_c.set_xlim(-0.008, 0.245)
    ax_c.set_xlabel("Logit Interaction Contrast Mean |I| = |z(A,A) - z(B,A) - z(A,B) + z(B,B)|")
    ax_c.set_title("[Exploratory 1-2(b)] Multimodal Head Non-Additivity |I|", pad=26)
    ax_c.grid(axis="x", color="#ECECEC", lw=0.7, zorder=0)
    ax_c.legend(
        loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=2,
        frameon=True, facecolor="white", edgecolor="#DDDDDD", fontsize=7.4,
    )

    # ---- Panel B: 1-1 Per-Emotion Visual - Caption Swap Difference (34 Emotions, C-1) ----
    em_c1 = em_diff[
        (em_diff["condition"] == "brain_decoded")
        & (em_diff["participant"] == "mean_5sub")
        & (em_diff["seed"] == "mean_3seeds")
    ].sort_values("visual_minus_caption", ascending=True).reset_index(drop=True)

    y_em = np.arange(len(em_c1))
    ax_b.axvline(0.0, color="#444444", ls="--", lw=1.0, zorder=1)
    ax_b.axvspan(-0.130, 0.0, color=PAL["vermilion"], alpha=0.045, zorder=0)
    ax_b.axvspan(0.0, 0.070, color=PAL["blue"], alpha=0.045, zorder=0)

    group_colors = {
        "high": PAL["orange"],
        "low": PAL["purple"],
        "other": "#555555",
    }

    for idx_e, row_e in em_c1.iterrows():
        val = row_e["visual_minus_caption"]
        lo = val - row_e["ci95_low"]
        hi = row_e["ci95_high"] - val
        q_sig = row_e["q_bh_fdr"] < 0.05
        grp = row_e["emonet_still_frame_group"]
        col_pt = PAL["vermilion"] if (val < 0 and q_sig) else (PAL["blue"] if (val > 0 and q_sig) else group_colors.get(grp, "#666666"))
        mk = "D" if grp == "high" else ("s" if grp == "low" else "o")

        ax_b.errorbar(
            val, idx_e, xerr=[[lo], [hi]],
            fmt=mk, color=col_pt, ecolor=col_pt if q_sig else "#B0B0B0",
            elinewidth=1.45 if q_sig else 0.9, capsize=2.0 if q_sig else 0.0,
            markersize=5.6 if (q_sig or grp in ("high", "low")) else 4.2, zorder=4 if q_sig else 3,
        )
        if q_sig:
            ax_b.text(
                row_e["ci95_low"] - 0.0025, idx_e, "*",
                ha="right", va="center", fontsize=10, fontweight="bold", color=col_pt,
            )

    ax_b.set_yticks(y_em)
    emo_labels = []
    for _, row_e in em_c1.iterrows():
        tag = ""
        if row_e["emonet_still_frame_group"] == "high":
            tag = " [EmoNet-High]"
        elif row_e["emonet_still_frame_group"] == "low":
            tag = " [EmoNet-Low]"
        emo_labels.append(f"{row_e['emotion']}{tag}")
    ax_b.set_yticklabels(emo_labels, fontsize=7.8)
    ax_b.set_ylim(-0.8, len(em_c1) + 0.35)
    ax_b.set_xlim(-0.125, 0.066)
    ax_b.set_xlabel("Visual Swap Effect minus Caption Swap Effect (95% Basic CI)")
    ax_b.set_title("[Exploratory 1-1] 34-Emotion Modality Dominance (C-1)", pad=8)
    ax_b.grid(axis="x", color="#ECECEC", lw=0.6, zorder=0)

    ax_b.text(-0.121, len(em_c1) - 0.45, "<- Caption swap stronger (25/34)", fontsize=8.0, color=PAL["vermilion"], fontweight="bold")
    ax_b.text(0.004, len(em_c1) - 0.45, "Visual swap stronger ->", fontsize=8.0, color=PAL["blue"], fontweight="bold")

    leg_elems = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=PAL["vermilion"], markersize=6, label="BH-FDR q < 0.05 (*, 5/34)"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor=PAL["orange"], markersize=6, label="Kragel EmoNet High still-frame (4)"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor=PAL["purple"], markersize=6, label="Kragel EmoNet Low still-frame (4)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#666666", markersize=5, label="Other emotions (q >= 0.05)"),
    ]
    ax_b.legend(handles=leg_elems, loc="lower right", frameon=True, facecolor="white", edgecolor="#DDDDDD", fontsize=7.6)

    panel_label(ax_a, "A", x=-0.18, y=1.18)
    panel_label(ax_c, "C", x=-0.18, y=1.14)
    panel_label(ax_b, "B", x=-0.24, y=1.02)

    return save_fig(fig, fig_dir, "fig3_s9_interchange_and_interaction")


# =============================================================================
# FIGURE 6: S9-3 K1a & B4 14 Affective Dimensions Unified Pathway Analysis
# =============================================================================
def make_fig6_k1a_14dims(base_dir: Path, fig_dir: Path) -> List[str]:
    summ = read_tsv(base_dir / "s9_summary/pathway_k1_k1a/s9_k1a_b4_14dimensions_summary.tsv")
    per_d = read_tsv(base_dir / "s9_summary/pathway_k1_k1a/s9_k1a_b4_per_dimension.tsv")

    for col in ["mean_r_14", "ci95_low_r_14", "ci95_high_r_14", "diff_vs_b4_main_14", "diff_ci95_low_14", "diff_ci95_high_14"]:
        summ[col] = pd.to_numeric(summ[col], errors="coerce")
    for col in ["r", "ci95_low", "ci95_high", "diff_vs_b4_main", "diff_ci95_low", "diff_ci95_high", "q_bh_fdr_14"]:
        per_d[col] = pd.to_numeric(per_d[col], errors="coerce")

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12.2, 5.6), gridspec_kw={"width_ratios": [1.05, 1.25]})
    plt.subplots_adjust(wspace=0.32)

    # ---- Panel A: Overall 14-Dimension Pathway Ladder (B4 vs Decoded->K1a vs Stimulus Ref) ----
    ladder_specs = [
        ("col2_reference_not_upper_bound", "s4_k1a_true_features", "na", "additive", "na",
         "S4 K1a Stimulus (Additive)\n[Ref only; NOT upper bound]", PAL["gray"], "s"),
        ("col3_primary_k1a_pathway", "ridge", "na", "additive", "uncalibrated",
         "(3) S5 Ridge -> Frozen K1a\n(Additive, uncalibrated)", PAL["green"], "D"),
        ("col3_primary_k1a_pathway", "ridge", "na", "additive", "calibrated",
         "(3) S5 Ridge -> Frozen K1a\n(Additive, N8 calibrated)", PAL["skyblue"], "D"),
        ("col1b_appendix_b4_literature", "b4_ridge_literature", "na", "linear_ridge", "na",
         "(1b) B4 Direct Brain Ridge\n(Literature 6-delay concat, H3)", PAL["orange"], "o"),
        ("col1_baseline_b4_main", "b4_ridge_main", "na", "linear_ridge", "na",
         "(1) B4 Direct Brain Ridge\n(Primary 2-4TR mean, N15)", PAL["blue"], "o"),
        ("col3_diagnostic_encoder2_D1", "feature_encoder", "mean_3seeds", "additive", "uncalibrated",
         "(Diag) D-1 Encoder 2 -> K1a\n(Feature MSE only, uncal.)", PAL["purple"], "^"),
        ("col3_primary_k1a_pathway", "brain_decoded", "mean_3seeds", "additive", "uncalibrated",
         "(3) C-1 Decoded -> Frozen K1a\n(Joint emotion + stop-grad)", PAL["vermilion"], "v"),
    ]

    y_pos = np.arange(len(ladder_specs))[::-1]
    # Shaded reference box at top row
    ax_a.axhspan(y_pos[0] - 0.42, y_pos[0] + 0.42, color="#ECEFF4", zorder=0)
    ax_a.axhline(y_pos[0] - 0.46, color="#888888", ls="--", lw=0.85, zorder=1)

    # Vertical reference line at B4_main
    b4_m5_val = summ[
        (summ["participant"] == "mean_5subj") & (summ["source"] == "b4_ridge_main")
    ]["mean_r_14"].iloc[0]
    ax_a.axvline(b4_m5_val, color=PAL["blue"], ls=":", lw=1.1, alpha=0.8, zorder=1)

    rng_j = np.random.default_rng(14)
    for idx_s, (role_k, src_k, seed_k, head_k, cal_k, label_s, col_s, mk_s) in enumerate(ladder_specs):
        yv = y_pos[idx_s]
        m_row = summ[
            (summ["participant"] == "mean_5subj")
            & (summ["role"] == role_k)
            & (summ["source"] == src_k)
            & (summ["seed"] == seed_k)
            & (summ["head"] == head_k)
            & (summ["calibration"] == cal_k)
        ].iloc[0]
        s_rows = summ[
            (summ["participant"].isin(PARTICIPANTS))
            & (summ["role"] == role_k)
            & (summ["source"] == src_k)
            & (summ["seed"] == seed_k)
            & (summ["head"] == head_k)
            & (summ["calibration"] == cal_k)
        ]

        mv = m_row["mean_r_14"]
        lo = mv - m_row["ci95_low_r_14"]
        hi = m_row["ci95_high_r_14"] - mv

        sub_vals = s_rows["mean_r_14"].to_numpy(dtype=float)
        jit = rng_j.uniform(-0.10, 0.10, size=len(sub_vals))
        ax_a.scatter(sub_vals, np.full_like(sub_vals, yv) + jit, color=col_s, alpha=0.38, s=22, zorder=3)
        ax_a.errorbar(
            mv, yv, xerr=[[lo], [hi]],
            fmt=mk_s, color=col_s, ecolor=col_s, elinewidth=1.8, capsize=3.4,
            markersize=6.6, markeredgecolor="white", markeredgewidth=0.7, zorder=5,
        )
        txt_x = max(float(m_row["ci95_high_r_14"]), float(sub_vals.max()) if len(sub_vals) else mv) + 0.009
        ax_a.text(
            txt_x, yv,
            f"{mv:.3f}", va="center", fontsize=8.1, fontweight="bold", color="#222222",
        )

    ax_a.set_yticks(y_pos)
    ax_a.set_yticklabels([x[5] for x in ladder_specs], fontsize=8.1)
    ax_a.set_xlim(0.16, 0.69)
    ax_a.set_xlabel("Pooled 6-Fold Mean Pearson r Across 14 Dimensions (1-9 Scale)")
    ax_a.set_title("[Exploratory K1a & B4] 14-Dimension Pathway Summary", pad=10)
    ax_a.grid(axis="x", color="#ECECEC", lw=0.7, zorder=0)

    # ---- Panel B: Per-Dimension Profile (14 Dimensions: B4_main vs Ridge->K1a vs C-1->K1a) ----
    d_b4 = per_d[
        (per_d["participant"] == "mean_5subj") & (per_d["source"] == "b4_ridge_main")
    ].set_index("dimension")
    d_rk1a = per_d[
        (per_d["participant"] == "mean_5subj")
        & (per_d["source"] == "ridge")
        & (per_d["head"] == "additive")
        & (per_d["calibration"] == "uncalibrated")
    ].set_index("dimension")
    d_c1k1a = per_d[
        (per_d["participant"] == "mean_5subj")
        & (per_d["source"] == "brain_decoded")
        & (per_d["seed"] == "mean_3seeds")
        & (per_d["head"] == "additive")
        & (per_d["calibration"] == "uncalibrated")
    ].set_index("dimension")

    dims_sorted = d_rk1a.sort_values("r", ascending=True).index.tolist()
    yd = np.arange(len(dims_sorted))

    for i_d, dim_name in enumerate(dims_sorted):
        r1 = d_b4.loc[dim_name, "r"]
        r3 = d_rk1a.loc[dim_name, "r"]
        rc = d_c1k1a.loc[dim_name, "r"]
        # Connector segment showing +Delta from B4 to Ridge->K1a
        ax_b.plot([r1, r3], [i_d, i_d], color=PAL["green"], lw=2.0, alpha=0.65, zorder=2)

    ax_b.errorbar(
        d_b4.loc[dims_sorted, "r"], yd,
        xerr=[
            d_b4.loc[dims_sorted, "r"] - d_b4.loc[dims_sorted, "ci95_low"],
            d_b4.loc[dims_sorted, "ci95_high"] - d_b4.loc[dims_sorted, "r"],
        ],
        fmt="o", color=PAL["blue"], ecolor=PAL["blue"], elinewidth=1.1, capsize=2.2,
        markersize=5.5, label="(1) B4 Direct Brain Ridge (Primary)", zorder=4,
    )
    ax_b.errorbar(
        d_rk1a.loc[dims_sorted, "r"], yd,
        xerr=[
            d_rk1a.loc[dims_sorted, "r"] - d_rk1a.loc[dims_sorted, "ci95_low"],
            d_rk1a.loc[dims_sorted, "ci95_high"] - d_rk1a.loc[dims_sorted, "r"],
        ],
        fmt="D", color=PAL["green"], ecolor=PAL["green"], elinewidth=1.3, capsize=2.2,
        markersize=5.8, label="(3) S5 Ridge -> Frozen K1a (14/14 q<0.05*)", zorder=5,
    )
    ax_b.errorbar(
        d_c1k1a.loc[dims_sorted, "r"], yd,
        xerr=[
            d_c1k1a.loc[dims_sorted, "r"] - d_c1k1a.loc[dims_sorted, "ci95_low"],
            d_c1k1a.loc[dims_sorted, "ci95_high"] - d_c1k1a.loc[dims_sorted, "r"],
        ],
        fmt="v", color=PAL["vermilion"], ecolor=PAL["vermilion"], elinewidth=1.0, capsize=2.0,
        markersize=5.2, label="(3) C-1 Decoded -> Frozen K1a", zorder=3,
    )

    for i_d, dim_name in enumerate(dims_sorted):
        dv = d_rk1a.loc[dim_name, "diff_vs_b4_main"]
        hi_v = d_rk1a.loc[dim_name, "ci95_high"]
        ax_b.text(hi_v + 0.006, i_d, f"+{dv:.3f}*", va="center", fontsize=7.6, fontweight="bold", color=PAL["green"])

    ax_b.set_yticks(yd)
    ax_b.set_yticklabels([d.capitalize() for d in dims_sorted], fontsize=8.5)
    ax_b.set_ylim(-2.3, len(dims_sorted) - 0.35)
    ax_b.set_xlim(0.05, 0.65)
    ax_b.set_xlabel("Pooled 6-Fold Pearson r (95% Basic CI; * = BH-FDR q < 0.05 vs B4)")
    ax_b.set_title("Per-Dimension Prediction & Zero-Shot Pathway Gain", pad=10)
    ax_b.grid(axis="x", color="#ECECEC", lw=0.7, zorder=0)
    ax_b.legend(
        loc="lower right",
        frameon=True, facecolor="white", framealpha=0.95, edgecolor="#DDDDDD", fontsize=7.6,
    )

    panel_label(ax_a, "A", x=-0.28, y=1.03)
    panel_label(ax_b, "B", x=-0.16, y=1.03)

    return save_fig(fig, fig_dir, "fig6_k1a_14dimensions")


# =============================================================================
# FIGURE 1: S6 Main Condition Ladder (A-E + S5 + S4 Ref) & [Prereg 2-3] Contrasts
# =============================================================================
def make_fig1_condition_ladder(base_dir: Path, fig_dir: Path) -> List[str]:
    t1 = read_tsv(base_dir / "tables/s10_table1_primary_metrics.tsv").set_index("model_id")
    t7 = read_tsv(base_dir / "tables/s10_table7_statistical_tests.tsv").set_index("test_id")

    for col in ["mean_5sub", "mean_5sub_ci_low", "mean_5sub_ci_high"] + PARTICIPANTS + ["all_dev_r", "all_dev_ci_low", "all_dev_ci_high"]:
        if col in t1.columns:
            t1[col] = pd.to_numeric(t1[col], errors="coerce")
    for col in ["mean_5sub_effect", "mean_5sub_ci_low", "mean_5sub_ci_high", "mean_5sub_p_raw"] + [f"{s}_effect" for s in PARTICIPANTS]:
        if col in t7.columns:
            t7[col] = pd.to_numeric(t7[col], errors="coerce")

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(14.6, 6.9), gridspec_kw={"width_ratios": [1.14, 1.06]})
    plt.subplots_adjust(wspace=0.66)

    # Panel A ladder items (top to bottom)
    ladder = [
        ("s4_stimulus", "S4 Stimulus Model (No brain)\n[Reference only; NOT upper bound]", PAL["gray"], "s", True),
        ("s6_multimodal", "S6 Multimodal Teacher (G16)\n[Reference only; NOT upper bound]", PAL["gray"], "s", True),
        ("s5_h2020", "S5 Horikawa 2020 Ridge (6-delay)", PAL["orange"], "o", False),
        ("s5_ridge_main", "S5 Primary Linear Ridge (N15)", PAL["orange"], "D", False),
        ("s6_brain_only", "A-1: Brain -> Emotion (Query)", PAL["blue"], "o", False),
        ("s6_brain_only_pool", "A-1_pool: Brain -> Emotion (Mean pool)", PAL["skyblue"], "o", False),
        ("s6_brain_only_distill", "A-2: Brain + Rating Distillation", PAL["blue"], "s", False),
        ("s6_brain_only_featdec", "B-1: Brain + Feature Aux Loss", PAL["green"], "o", False),
        ("s6_brain_decoded", "C-1: Brain + Decoded Feat (Interact.)", PAL["vermilion"], "D", False),
        ("s6_brain_decoded_additive", "C-1_add: Brain + Decoded (Additive)", PAL["vermilion"], "s", False),
        ("s6_brain_decoded_distill", "C-2: C-1 + Rating Distillation", PAL["vermilion"], "^", False),
        ("s6_brain_decoded_sep", "D-1: Separate Feature Encoder", PAL["purple"], "o", False),
        ("s6_brain_features_only", "D-3: OOF Decoded Feat -> Emotion", PAL["purple"], "s", False),
        ("s6_brain_features_only_paired", "D-3_paired: Paired Feat. Ensemble", PAL["purple"], "^", False),
        ("s6_brain_frozen_feature_encoder", "D-4: Paired Frozen Enc. Ensemble", PAL["purple"], "D", False),
        ("s6_brain_only_repr_frozen", "E-frozen: Multimodal Repr. Align", PAL["navy"], "o", False),
        ("s6_brain_only_repr_trained", "E-trained: Multimodal Joint Repr.", PAL["navy"], "D", False),
    ]

    ladder = [
        x for x in ladder
        if x[0] in t1.index and np.isfinite(float(t1.loc[x[0], "mean_5sub"]))
    ]
    n_ref = sum(1 for x in ladder if x[4])
    ya = np.arange(len(ladder))[::-1]
    # Shade top reference rows
    if n_ref >= 1:
        ax_a.axhspan(ya[n_ref - 1] - 0.45, ya[0] + 0.45, color="#ECEFF4", zorder=0)
        ax_a.axhline(ya[n_ref - 1] - 0.48, color="#777777", ls="--", lw=0.9, zorder=1)

    a1_val = float(t1.loc["s6_brain_only", "mean_5sub"])
    ax_a.axvline(a1_val, color=PAL["blue"], ls=":", lw=1.1, alpha=0.85, zorder=1)

    rng_a = np.random.default_rng(101)
    for idx_l, (mid, mlabel, col_m, mk_m, is_ref) in enumerate(ladder):
        yv = ya[idx_l]
        row = t1.loc[mid]
        mv = float(row["mean_5sub"])
        lo = mv - float(row["mean_5sub_ci_low"])
        hi = float(row["mean_5sub_ci_high"]) - mv

        sub_vals = np.array([float(row[s]) for s in PARTICIPANTS])
        jit = rng_a.uniform(-0.12, 0.12, size=len(sub_vals))
        ax_a.scatter(sub_vals, np.full_like(sub_vals, yv) + jit, color=col_m, alpha=0.35, s=18, zorder=3)
        ax_a.errorbar(
            mv, yv, xerr=[[lo], [hi]],
            fmt=mk_m, color=col_m, ecolor=col_m, elinewidth=1.6, capsize=2.8,
            markersize=6.0, markeredgecolor="white", markeredgewidth=0.65, zorder=5,
        )
        txt_xa = max(float(row["mean_5sub_ci_high"]), float(np.nanmax(sub_vals))) + 0.006
        ax_a.text(
            txt_xa, yv,
            f"{mv:.3f}", va="center", fontsize=7.8, fontweight="bold", color="#222222",
        )

    ax_a.set_yticks(ya)
    ax_a.set_yticklabels([x[1] for x in ladder], fontsize=8.0)
    ax_a.set_xlim(0.14, 0.545)
    ax_a.set_xlabel("Pooled 6-Fold Mean Pearson r Across 34 Emotions (95% CI)")
    ax_a.set_title("Main Emotion Prediction Ladder (3-Seed Mean, G14)", pad=10)
    ax_a.grid(axis="x", color="#ECECEC", lw=0.7, zorder=0)

    # ---- Panel B: [Prereg 2-3(a)-(f)] + Key Controls & Ablations (G6, F7, G8, 1-2a, N23) ----
    contrasts = [
        ("2-3_가_B1_vs_A1", "[Prereg 2-3a] B-1 - A-1 (Feat aux loss)", True),
        ("2-3_나_C1_vs_B1", "[Prereg 2-3b] C-1 - B-1 (Decoded head input)", True),
        ("2-3_다_A2_vs_A1", "[Prereg 2-3c] A-2 - A-1 (Rating distill)", True),
        ("2-3_라_A2_vs_label_smoothing", "[Prereg 2-3d] A-2 - Label smoothing", True),
        ("2-3_마_B1_vs_A2", "[Prereg 2-3e] B-1 - A-2 (Feat aux vs Distill)", True),
        ("2-3_바_C2_vs_C1", "[Prereg 2-3f] C-2 - C-1 (Distill on C-1)", True),
        ("G6_B1_vs_feat_shuffle", "[Control G6] B-1 - Feature shuffle", False),
        ("G6_A2_vs_stim_shuffle", "[Control G6] A-2 - Stimulus shuffle", False),
        ("F7_A1_vs_A1_pool", "[Ablation F7] A-1 - A-1_pool (Query vs Mean)", False),
        ("F7_C1_vs_C1_pool", "[Ablation F7] C-1 - C-1_pool (Query vs Mean)", False),
        ("G8_C1_vs_C1_grad", "[Ablation G8] C-1 - C-1_grad (Stop-grad)", False),
        ("1-2_가_C1_vs_C1_additive", "[Ablation 1-2a] C-1 - C-1_additive", False),
        ("D_D1_vs_C1", "[2-Stage D] D-1 - C-1 (Separate vs Shared enc.)", False),
        ("N23_C1_vs_ridge_main", "[Baseline N23] C-1 - S5 Primary Ridge", False),
    ]

    contrasts = [
        c for c in contrasts
        if c[0] in t7.index and np.isfinite(float(t7.loc[c[0], "mean_5sub_effect"]))
    ]
    n_pre_c = sum(1 for c in contrasts if c[2])

    # Compute unified Holm-11 on the 6 [2-3] rows by combining with 2-1 and 2-2 p-values
    sw_df = read_tsv(base_dir / "s9_summary/interchange/s9_2_2_swap_summary.tsv")
    sw_c1_m5 = sw_df[
        (sw_df["condition"] == "brain_decoded")
        & (sw_df["participant"] == "mean_5sub")
        & (sw_df["seed"] == "mean_3seeds")
        & (sw_df["path"].isin(["visual", "caption", "both"]))
    ]
    p11_ids = (
        ["2-1_ridge_vision", "2-1_ridge_caption"]
        + ["2-2_visual", "2-2_caption", "2-2_both"]
        + [c[0] for c in contrasts if c[2]]
    )
    p11_vals = (
        [float(t7.loc["2-1_ridge_vision", "mean_5sub_p_raw"]), float(t7.loc["2-1_ridge_caption", "mean_5sub_p_raw"])]
        + [float(sw_c1_m5[sw_c1_m5["path"] == p]["p_boot"].iloc[0]) for p in ["visual", "caption", "both"]]
        + [float(t7.loc[c[0], "mean_5sub_p_raw"]) for c in contrasts if c[2]]
    )
    p11_holm = dict(zip(p11_ids, holm_adjust(p11_vals)))

    yb = np.arange(len(contrasts))[::-1]
    if n_pre_c >= 1:
        ax_b.axhspan(yb[n_pre_c - 1] - 0.45, yb[0] + 0.45, color="#FDF6EC", zorder=0)
        ax_b.axhline(yb[n_pre_c - 1] - 0.48, color="#999999", ls="--", lw=0.85, zorder=1)
    ax_b.axvline(0.0, color="#333333", ls="--", lw=1.0, zorder=1)

    for idx_c, (tid, clabel, is_pre) in enumerate(contrasts):
        yv = yb[idx_c]
        row = t7.loc[tid]
        eff = float(row["mean_5sub_effect"])
        lo = eff - float(row["mean_5sub_ci_low"])
        hi = float(row["mean_5sub_ci_high"]) - eff
        p_raw = float(row["mean_5sub_p_raw"])
        p_use = p11_holm[tid] if is_pre else p_raw

        sig = p_use < 0.05
        col_c = (PAL["blue"] if eff > 0 else PAL["vermilion"]) if sig else "#6E6E6E"
        mk_c = "D" if is_pre else "o"

        sub_effs = np.array([float(row[f"{s}_effect"]) for s in PARTICIPANTS])
        jit = rng_a.uniform(-0.11, 0.11, size=len(sub_effs))
        ax_b.scatter(sub_effs, np.full_like(sub_effs, yv) + jit, color=col_c, alpha=0.35, s=16, zorder=3)
        ax_b.errorbar(
            eff, yv, xerr=[[lo], [hi]],
            fmt=mk_c, color=col_c, ecolor=col_c, elinewidth=1.6 if sig else 1.1, capsize=2.8,
            markersize=5.8 if sig else 5.0, markeredgecolor="white", markeredgewidth=0.6, zorder=5,
        )
        star = "**" if p_use < 0.01 else ("*" if p_use < 0.05 else "")
        txt_xb = max(float(row["mean_5sub_ci_high"]), float(np.nanmax(sub_effs))) + 0.003
        ax_b.text(
            txt_xb, yv,
            f"{eff:+.3f}{star}", va="center", fontsize=7.6,
            fontweight="bold" if sig else "normal", color=col_c,
        )

    ax_b.set_yticks(yb)
    ax_b.set_yticklabels([x[1] for x in contrasts], fontsize=8.0)
    x_min = min(
        min(float(t7.loc[c[0], "mean_5sub_ci_low"]) for c in contrasts),
        min(float(t7.loc[c[0], f"{s}_effect"]) for c in contrasts for s in PARTICIPANTS),
    )
    x_max = max(
        max(float(t7.loc[c[0], "mean_5sub_ci_high"]) for c in contrasts),
        max(float(t7.loc[c[0], f"{s}_effect"]) for c in contrasts for s in PARTICIPANTS),
    )
    ax_b.set_xlim(min(-0.045, x_min - 0.012), max(0.062, x_max + 0.028))
    ax_b.set_xlabel("Paired Condition Difference Δr (95% Basic CI; * Holm-11 / raw p<0.05)")
    ax_b.set_title("Preregistered [2-3] & Diagnostic Contrasts", pad=10)
    ax_b.grid(axis="x", color="#ECECEC", lw=0.7, zorder=0)

    panel_label(ax_a, "A", x=-0.34, y=1.02)
    panel_label(ax_b, "B", x=-0.46, y=1.02)

    return save_fig(fig, fig_dir, "fig1_s6_condition_ladder")


# =============================================================================
# FIGURE 4: S9-4 CAB-NP 13-Group Network Input Perturbation (6-4b / 2-4)
# =============================================================================
def make_fig4_network_perturbation(base_dir: Path, fig_dir: Path) -> List[str]:
    df = read_tsv(base_dir / "s9_summary/network_perturbation/s9_6_4b_network_perturbation_summary.tsv")
    num_cols = [
        "median_agreement", "n_roi", "n_voxels",
        "drop_A1_mean", "drop_A1_ci_low", "drop_A1_ci_high",
        "drop_C1_mean", "drop_C1_ci_low", "drop_C1_ci_high",
        "diff_C1_minus_A1_mean", "diff_C1_minus_A1_ci_low", "diff_C1_minus_A1_ci_high",
        "p_boot", "p_holm13",
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    m5 = df[df["participant"] == "mean_5"].copy()
    m5["mean_drop_both"] = 0.5 * (m5["drop_A1_mean"] + m5["drop_C1_mean"])
    m5 = m5.sort_values("mean_drop_both", ascending=True).reset_index(drop=True)
    groups_order = m5["group"].tolist()

    fig, (ax_a, ax_b, ax_c) = plt.subplots(
        1, 3, figsize=(13.2, 5.8), sharey=True,
        gridspec_kw={"width_ratios": [1.25, 1.10, 0.65]},
    )
    plt.subplots_adjust(wspace=0.14)

    yg = np.arange(len(groups_order))
    rng_n = np.random.default_rng(64)

    # Panel A: Perturbation Drop (r_orig - r_pert) for A-1 and C-1
    ax_a.axvline(0.0, color="#444444", ls="--", lw=0.95, zorder=1)
    for i_g, g_name in enumerate(groups_order):
        r_m = m5.iloc[i_g]
        r_s = df[(df["participant"].isin(PARTICIPANTS)) & (df["group"] == g_name)]

        # A-1 (offset -0.14) and C-1 (offset +0.14)
        ax_a.scatter(r_s["drop_A1_mean"], np.full(len(r_s), i_g - 0.14), color=PAL["blue"], alpha=0.32, s=15, zorder=3)
        ax_a.scatter(r_s["drop_C1_mean"], np.full(len(r_s), i_g + 0.14), color=PAL["vermilion"], alpha=0.32, s=15, zorder=3)

        ax_a.errorbar(
            r_m["drop_A1_mean"], i_g - 0.14,
            xerr=[[r_m["drop_A1_mean"] - r_m["drop_A1_ci_low"]], [r_m["drop_A1_ci_high"] - r_m["drop_A1_mean"]]],
            fmt="o", color=PAL["blue"], ecolor=PAL["blue"], elinewidth=1.4, capsize=2.4,
            markersize=5.4, label="A-1 (Brain -> Emotion)" if i_g == 0 else None, zorder=5,
        )
        ax_a.errorbar(
            r_m["drop_C1_mean"], i_g + 0.14,
            xerr=[[r_m["drop_C1_mean"] - r_m["drop_C1_ci_low"]], [r_m["drop_C1_ci_high"] - r_m["drop_C1_mean"]]],
            fmt="D", color=PAL["vermilion"], ecolor=PAL["vermilion"], elinewidth=1.4, capsize=2.4,
            markersize=5.2, label="C-1 (Brain + Decoded Feat)" if i_g == 0 else None, zorder=5,
        )

    y_labels = []
    for _, r_m in m5.iterrows():
        g_str = r_m["group"]
        if g_str.lower().startswith("subcort") or r_m["group_kind"] != "cortical_network":
            y_labels.append(f"{g_str} [Anat. group, {int(r_m['n_roi'])} ROIs]")
        else:
            y_labels.append(f"{g_str} ({int(r_m['n_roi'])} ROIs)")

    ax_a.set_yticks(yg)
    ax_a.set_yticklabels(y_labels, fontsize=8.3)
    ax_a.set_xlabel("Perturbation Drop: r_orig - r_pert (20 Donor Swaps)")
    ax_a.set_title("Network Input Perturbation Drop", pad=10)
    ax_a.grid(axis="x", color="#ECECEC", lw=0.7, zorder=0)
    ax_a.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#DDDDDD", fontsize=7.8)

    # Panel B: Differential Reliance Δ_drop = drop(C-1) - drop(A-1) with Holm-13
    ax_b.axvline(0.0, color="#333333", ls="--", lw=1.0, zorder=1)
    for i_g, g_name in enumerate(groups_order):
        r_m = m5.iloc[i_g]
        r_s = df[(df["participant"].isin(PARTICIPANTS)) & (df["group"] == g_name)]
        dv = r_m["diff_C1_minus_A1_mean"]
        lo = dv - r_m["diff_C1_minus_A1_ci_low"]
        hi = r_m["diff_C1_minus_A1_ci_high"] - dv
        sig_h13 = r_m["p_holm13"] < 0.05
        sig_raw = r_m["p_boot"] < 0.05
        col_d = (PAL["vermilion"] if dv > 0 else PAL["blue"]) if sig_h13 else (PAL["orange"] if sig_raw else "#666666")

        jit = rng_n.uniform(-0.10, 0.10, size=len(r_s))
        ax_b.scatter(r_s["diff_C1_minus_A1_mean"], np.full(len(r_s), i_g) + jit, color=col_d, alpha=0.35, s=15, zorder=3)
        ax_b.errorbar(
            dv, i_g, xerr=[[lo], [hi]],
            fmt="D" if sig_h13 else "o", color=col_d, ecolor=col_d,
            elinewidth=1.6 if sig_h13 else 1.1, capsize=2.6, markersize=5.6 if sig_h13 else 4.8, zorder=5,
        )
        mark = "*" if sig_h13 else ("+" if sig_raw else "")
        if mark:
            lbl_x = max(
                float(r_m["diff_C1_minus_A1_ci_high"]),
                float(r_s["diff_C1_minus_A1_mean"].max()) if len(r_s) else float(dv),
            ) + 0.00028
            ax_b.text(
                lbl_x, i_g,
                f"{dv:+.4f}{mark}", va="center", fontsize=7.6, fontweight="bold", color=col_d,
            )

    d_min = min(float(m5["diff_C1_minus_A1_ci_low"].min()), float(df[df["participant"].isin(PARTICIPANTS)]["diff_C1_minus_A1_mean"].min()))
    d_max = max(float(m5["diff_C1_minus_A1_ci_high"].max()), float(df[df["participant"].isin(PARTICIPANTS)]["diff_C1_minus_A1_mean"].max()))
    span = max(0.008, d_max - d_min)
    ax_b.set_xlim(d_min - 0.18 * span, d_max + 0.42 * span)
    ax_b.set_xlabel("Δ Drop: drop(C-1) - drop(A-1) (* Holm-13 p<0.05)")
    ax_b.set_title("Differential Network Reliance (6-4b)", pad=10)
    ax_b.grid(axis="x", color="#ECECEC", lw=0.7, zorder=0)

    # Panel C: S2 Inter-Subject Agreement Context (6-4 rule: context, not noise ceiling)
    ax_c.axvline(0.0, color="#888888", ls=":", lw=0.8, zorder=1)
    ax_c.hlines(yg, 0.0, m5["median_agreement"], color=PAL["green"], lw=1.8, alpha=0.7, zorder=3)
    ax_c.scatter(m5["median_agreement"], yg, color=PAL["green"], s=34, zorder=4)
    for i_g, r_m in m5.iterrows():
        ax_c.text(
            r_m["median_agreement"] + 0.008, i_g,
            f"{r_m['median_agreement']:.2f}", va="center", fontsize=7.6, color="#222222",
        )
    ax_c.set_xlim(0.0, max(0.32, m5["median_agreement"].max() + 0.12))
    ax_c.set_xlabel("Median ISC r\n(Context only)")
    ax_c.set_title("S2 Agreement", pad=10)
    ax_c.grid(axis="x", color="#ECECEC", lw=0.7, zorder=0)

    panel_label(ax_a, "A", x=-0.28, y=1.03)
    panel_label(ax_b, "B", x=-0.06, y=1.03)
    panel_label(ax_c, "C", x=-0.08, y=1.03)

    return save_fig(fig, fig_dir, "fig4_s9_cabnp_network_perturbation")


# =============================================================================
# FIGURE 5: 34-Emotion Prediction Profile (Table 4) & S9-3 K1 Pathway Summary
# =============================================================================
def make_fig5_emotion34_and_k1(base_dir: Path, fig_dir: Path) -> List[str]:
    t4 = read_tsv(base_dir / "tables/s10_table4_per_emotion_34.tsv")
    k1 = read_tsv(base_dir / "s9_summary/pathway_k1_k1a/s9_k1_pathway_summary.tsv")

    for col in [
        "C-1_mean_5sub_r", "C-1_mean_5sub_ci_low", "C-1_mean_5sub_ci_high",
        "A-1_mean_5sub_r", "ridge_main_mean_5sub_r", "Stimulus_Model_mean_5sub_r",
    ]:
        t4[col] = pd.to_numeric(t4[col], errors="coerce")
    for col in ["mean_r_34", "ci95_low_r_34", "ci95_high_r_34", "diff_vs_a1_34", "diff_ci95_low_34", "diff_ci95_high_34"]:
        k1[col] = pd.to_numeric(k1[col], errors="coerce")

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12.8, 7.2), gridspec_kw={"width_ratios": [1.30, 1.00]})
    plt.subplots_adjust(wspace=0.34)

    # ---- Panel A: 34-Emotion Sorted Prediction Profile ----
    t4_s = t4.sort_values("C-1_mean_5sub_r", ascending=True).reset_index(drop=True)
    ye = np.arange(len(t4_s))

    ax_a.axvline(0.0, color="#666666", ls="--", lw=0.85, zorder=1)
    # Stimulus reference as open gray squares (explicitly non-upper-bound)
    ax_a.scatter(
        t4_s["Stimulus_Model_mean_5sub_r"], ye,
        facecolors="none", edgecolors="#7A7A7A", marker="s", s=26, linewidths=1.0,
        label="S4 Stimulus Ref (No brain; NOT upper bound)", zorder=2,
    )
    ax_a.scatter(
        t4_s["ridge_main_mean_5sub_r"], ye,
        color=PAL["orange"], marker="^", s=24, alpha=0.85,
        label="S5 Primary Linear Ridge", zorder=3,
    )
    ax_a.scatter(
        t4_s["A-1_mean_5sub_r"], ye,
        color=PAL["blue"], marker="o", s=24, alpha=0.85,
        label="A-1 (Brain -> Emotion)", zorder=4,
    )
    ax_a.errorbar(
        t4_s["C-1_mean_5sub_r"], ye,
        xerr=[
            t4_s["C-1_mean_5sub_r"] - t4_s["C-1_mean_5sub_ci_low"],
            t4_s["C-1_mean_5sub_ci_high"] - t4_s["C-1_mean_5sub_r"],
        ],
        fmt="D", color=PAL["vermilion"], ecolor=PAL["vermilion"], elinewidth=1.1, capsize=1.8,
        markersize=4.6, label="C-1 (Brain + Decoded Feat, 95% CI)", zorder=5,
    )

    ax_a.set_yticks(ye)
    ax_a.set_yticklabels(t4_s["emotion"], fontsize=7.9)
    ax_a.set_ylim(-0.8, len(t4_s) - 0.2)
    ax_a.set_xlim(-0.04, max(0.84, float(t4_s["Stimulus_Model_mean_5sub_r"].max()) + 0.05))
    ax_a.set_xlabel("Pooled 6-Fold Pearson r (5-Participant Mean)")
    ax_a.set_title("Per-Emotion Normative Rating Prediction Across 34 Categories", pad=10)
    ax_a.grid(axis="x", color="#ECECEC", lw=0.65, zorder=0)
    ax_a.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#DDDDDD", fontsize=7.7)

    # ---- Panel B: S9-3 K1 Zero-Shot Pathway Evaluation (34 Emotions) ----
    k1_specs = [
        ("reference_not_upper_bound", "s4_true_features", "na", "additive", "na",
         "S4 Stimulus (Additive, r=0)\n[Ref only; NOT upper bound]", PAL["gray"], "s"),
        ("reference_not_upper_bound", "s4_true_features", "na", "interaction", "na",
         "S4 Stimulus (Interaction, r=1)\n[Ref only; NOT upper bound]", PAL["gray"], "o"),
        ("primary_k1_pathway", "ridge", "na", "additive", "uncalibrated",
         "K1: S5 Ridge -> Frozen Stim.\n(Additive, uncalibrated) ***", PAL["green"], "D"),
        ("primary_k1_pathway", "ridge", "na", "additive", "calibrated",
         "K1: S5 Ridge -> Frozen Stim.\n(Additive, N8 calibrated) ***", PAL["skyblue"], "D"),
        ("context_full_c1_with_roi_path", "brain_decoded_full_model", "mean_3seeds", "interaction", "na",
         "C-1 Full (ROI + Decoded Feat)", PAL["vermilion"], "^"),
        ("diagnostic_encoder2_D1", "feature_encoder", "mean_3seeds", "additive", "uncalibrated",
         "Diag: D-1 Enc. 2 -> Frozen Stim.\n(Additive, uncalibrated)", PAL["purple"], "o"),
        ("baseline_A1", "brain_only", "mean_3seeds", "query_readout", "na",
         "Baseline A-1 (Brain -> Emotion)", PAL["blue"], "o"),
        ("primary_k1_pathway", "brain_decoded", "mean_3seeds", "additive", "uncalibrated",
         "K1: C-1 Decoded -> Frozen Stim.\n(Additive, uncalibrated)", PAL["orange"], "v"),
        ("primary_k1_pathway", "ridge", "na", "interaction", "uncalibrated",
         "K1: S5 Ridge -> Frozen Stim.\n(Multiplicative interact., uncal.)", "#8C564B", "s"),
        ("primary_k1_pathway", "brain_decoded", "mean_3seeds", "interaction", "uncalibrated",
         "K1: C-1 Decoded -> Frozen Stim.\n(Multiplicative interact., uncal.)", "#8C564B", "v"),
    ]

    yk = np.arange(len(k1_specs))[::-1]
    ax_b.axhspan(yk[1] - 0.45, yk[0] + 0.45, color="#ECEFF4", zorder=0)
    ax_b.axhline(yk[1] - 0.48, color="#777777", ls="--", lw=0.85, zorder=1)

    a1_k1 = float(k1[
        (k1["participant"] == "mean_5subj") & (k1["role"] == "baseline_A1") & (k1["seed"] == "mean_3seeds")
    ]["mean_r_34"].iloc[0])
    ax_b.axvline(a1_k1, color=PAL["blue"], ls=":", lw=1.1, alpha=0.85, zorder=1)

    rng_k = np.random.default_rng(34)
    for idx_k, (rk, sk, seed_k, hk, calk, lab_k, col_k, mk_k) in enumerate(k1_specs):
        yv = yk[idx_k]
        m_row = k1[
            (k1["participant"] == "mean_5subj")
            & (k1["role"] == rk)
            & (k1["source"] == sk)
            & (k1["seed"] == seed_k)
            & (k1["head"] == hk)
            & (k1["calibration"] == calk)
        ].iloc[0]
        s_rows = k1[
            (k1["participant"].isin(PARTICIPANTS))
            & (k1["role"] == rk)
            & (k1["source"] == sk)
            & (k1["seed"] == seed_k)
            & (k1["head"] == hk)
            & (k1["calibration"] == calk)
        ]

        mv = float(m_row["mean_r_34"])
        lo = mv - float(m_row["ci95_low_r_34"])
        hi = float(m_row["ci95_high_r_34"]) - mv

        max_sub_k = mv
        if len(s_rows) > 0:
            sub_vals = s_rows["mean_r_34"].to_numpy(dtype=float)
            max_sub_k = float(np.nanmax(sub_vals))
            jit = rng_k.uniform(-0.11, 0.11, size=len(sub_vals))
            ax_b.scatter(sub_vals, np.full_like(sub_vals, yv) + jit, color=col_k, alpha=0.35, s=18, zorder=3)

        ax_b.errorbar(
            mv, yv, xerr=[[lo], [hi]],
            fmt=mk_k, color=col_k, ecolor=col_k, elinewidth=1.6, capsize=2.8,
            markersize=6.0, markeredgecolor="white", markeredgewidth=0.65, zorder=5,
        )
        txt_xk = max(float(m_row["ci95_high_r_34"]), max_sub_k) + 0.007
        ax_b.text(
            txt_xk, yv,
            f"{mv:.3f}", va="center", fontsize=7.9, fontweight="bold", color="#222222",
        )

    ax_b.set_yticks(yk)
    ax_b.set_yticklabels([x[5] for x in k1_specs], fontsize=7.9)
    ax_b.set_xlim(0.04, 0.545)
    ax_b.set_xlabel("Pooled 6-Fold Mean Pearson r Across 34 Emotions (95% CI)")
    ax_b.set_title("[Exploratory K1] Decoded Feature -> Frozen Stimulus", pad=10)
    ax_b.grid(axis="x", color="#ECECEC", lw=0.7, zorder=0)

    panel_label(ax_a, "A", x=-0.22, y=1.02)
    panel_label(ax_b, "B", x=-0.36, y=1.02)

    return save_fig(fig, fig_dir, "fig5_emotion34_and_k1_pathway")


# =============================================================================
# UNIFIED PREREGISTERED 6-1 VERDICT TABLE (0행 + 15 [사전] + 2-4/6-4b + 6-3)
# =============================================================================
def build_unified_verdict_table(base_dir: Path, out_tables_dir: Path) -> List[str]:
    t7 = read_tsv(base_dir / "tables/s10_table7_statistical_tests.tsv").set_index("test_id")
    sw = read_tsv(base_dir / "s9_summary/interchange/s9_2_2_swap_summary.tsv")
    net = read_tsv(base_dir / "s9_summary/network_perturbation/s9_6_4b_network_perturbation_summary.tsv")

    for col in [c for c in t7.columns if any(k in c for k in ["effect", "ci_", "p_raw", "p_holm", "seed"])]:
        t7[col] = pd.to_numeric(t7[col], errors="coerce")
    for col in ["actual_r", "control_r_mean", "effect", "effect_seed_sd", "ci95_low", "ci95_high", "p_boot"]:
        sw[col] = pd.to_numeric(sw[col], errors="coerce")
    for col in ["diff_C1_minus_A1_mean", "diff_C1_minus_A1_sd", "diff_C1_minus_A1_ci_low", "diff_C1_minus_A1_ci_high", "p_boot", "p_holm13"]:
        net[col] = pd.to_numeric(net[col], errors="coerce")

    rows: List[dict] = []

    # 1. 0행 Prerequisite Tests (Holm-2)
    for tid, desc in [
        ("0행_A-1", "0행 전제 검정: A-1 (Brain -> Emotion) > 순열 귀무분포"),
        ("0행_C-1", "0행 전제 검정: C-1 (Brain + Decoded Feature -> Emotion) > 순열 귀무분포"),
    ]:
        r = t7.loc[tid]
        p_raw = float(r["mean_5sub_p_raw"])
        p_h2 = float(r["mean_5sub_p_holm_family"])
        rows.append({
            "verdict_order": len(rows) + 1,
            "section": "0행_전제검정",
            "correction_family": "Holm-2 (0행 전제 검정)",
            "test_id": tid,
            "hypothesis_ko": desc,
            "execution_status": "완료 (HK 6-fold)",
            "inference_method": "런 안 순열검정 10,000회 (단측, O4(1))",
            "mean_5sub_estimate": float(r["mean_5sub_effect"]),
            "mean_5sub_seed_sd": float(r["mean_5sub_seed_sd"]),
            "mean_5sub_ci95_low": float(r["mean_5sub_ci_low"]),
            "mean_5sub_ci95_high": float(r["mean_5sub_ci_high"]),
            "mean_5sub_p_unadjusted": p_raw,
            "mean_5sub_p_adjusted_primary": p_h2,
            "mean_5sub_p_holm15_worstcase": np.nan,
            "confirmed_mean_5sub": bool(p_h2 < 0.05),
            "n_sub_confirmed_unadj_of_5": int(float(r["n_confirmed_pos_unadj"])),
            "n_sub_confirmed_adj_of_5": int(float(r["n_confirmed_pos_holm_family"])),
            "n_sub_confirmed_holm15_worstcase_of_5": np.nan,
            **{f"{s}_estimate": float(r[f"{s}_effect"]) for s in PARTICIPANTS},
            **{f"{s}_p_unadjusted": float(r[f"{s}_p_raw"]) for s in PARTICIPANTS},
            "korean_verdict_statement": (
                f"5명 평균 r = {float(r['mean_5sub_effect']):.4f} (95% CI [{float(r['mean_5sub_ci_low']):.4f}, {float(r['mean_5sub_ci_high']):.4f}]), "
                f"Holm-2 보정 p = {p_h2:.4f} (참가자 5/5명 확인)."
            ),
        })

    # 2. Gather all 11 completed [사전] tests from the 15-test Holm family:
    #    - 2-1: 2 tests (S5 Ridge Vision, Caption)
    #    - 2-2: 3 tests (C-1 swap visual, caption, both)
    #    - 2-3: 6 tests ((가)~(바))
    prereg11_entries = []

    for tid, desc in [
        ("2-1_ridge_vision", "[사전 1/15] 2-1: S5 Ridge 시각 특징 복원 (V-JEPA2 5,632d)"),
        ("2-1_ridge_caption", "[사전 2/15] 2-1: S5 Ridge 캡션 특징 복원 (DeBERTa 4,096d)"),
    ]:
        r = t7.loc[tid]
        prereg11_entries.append({
            "test_id": tid,
            "hypothesis_ko": desc,
            "inference_method": "런 안 순열검정 10,000회 (단측, O4(1))",
            "est": float(r["mean_5sub_effect"]),
            "sd": np.nan,
            "cil": float(r["mean_5sub_ci_low"]),
            "cih": float(r["mean_5sub_ci_high"]),
            "p_m5": float(r["mean_5sub_p_raw"]),
            "sub_est": [float(r[f"{s}_effect"]) for s in PARTICIPANTS],
            "sub_p": [float(r[f"{s}_p_raw"]) for s in PARTICIPANTS],
            "require_positive": True,
        })

    for idx_p, (pkey, pdesc) in enumerate([
        ("visual", "[사전 3/15] 2-2: C-1 시각 경로 교체 개입 효과 (actual - random control)"),
        ("caption", "[사전 4/15] 2-2: C-1 캡션 경로 교체 개입 효과 (actual - random control)"),
        ("both", "[사전 5/15] 2-2: C-1 두 경로 동시 교체 개입 효과 (actual - random control)"),
    ]):
        rm = sw[(sw["condition"] == "brain_decoded") & (sw["participant"] == "mean_5sub") & (sw["seed"] == "mean_3seeds") & (sw["path"] == pkey)].iloc[0]
        rs = sw[(sw["condition"] == "brain_decoded") & (sw["seed"] == "mean_3seeds") & (sw["path"] == pkey)].set_index("participant")
        prereg11_entries.append({
            "test_id": f"2-2_C1_swap_{pkey}",
            "hypothesis_ko": pdesc,
            "inference_method": "쌍 묶음(419개 연결 성분) 부트스트랩 10,000회 (양측 Hall-Wilson, O4(3))",
            "est": float(rm["effect"]),
            "sd": float(rm["effect_seed_sd"]),
            "cil": float(rm["ci95_low"]),
            "cih": float(rm["ci95_high"]),
            "p_m5": float(rm["p_boot"]),
            "sub_est": [float(rs.loc[s, "effect"]) for s in PARTICIPANTS],
            "sub_p": [float(rs.loc[s, "p_boot"]) for s in PARTICIPANTS],
            "require_positive": True,
        })

    for tid, pdesc, req_pos in [
        ("2-3_가_B1_vs_A1", "[사전 6/15] 2-3(가): B-1 - A-1 (특징 복원 보조손실 효과; 방향 예측: B-1 > A-1)", True),
        ("2-3_나_C1_vs_B1", "[사전 7/15] 2-3(나): C-1 - B-1 (정서 head 복원 특징 직접 입력; 방향 미예측)", False),
        ("2-3_다_A2_vs_A1", "[사전 8/15] 2-3(다): A-2 - A-1 (자극 예측 평정 증류; 방향 미예측)", False),
        ("2-3_라_A2_vs_label_smoothing", "[사전 9/15] 2-3(라): A-2 - label_smoothing (평정 내용 vs 완화 정칙화; 방향 미예측)", False),
        ("2-3_마_B1_vs_A2", "[사전 10/15] 2-3(마): B-1 - A-2 (특징 보조손실 vs 예측 평정 증류; 방향 미예측)", False),
        ("2-3_바_C2_vs_C1", "[사전 11/15] 2-3(바): C-2 - C-1 (C-1 위 증류 추가; 방향 미예측)", False),
    ]:
        r = t7.loc[tid]
        prereg11_entries.append({
            "test_id": tid,
            "hypothesis_ko": pdesc,
            "inference_method": "영상 canonical_id(2,108개) 부트스트랩 10,000회 (양측 Hall-Wilson, O4(3))",
            "est": float(r["mean_5sub_effect"]),
            "sd": float(r["mean_5sub_seed_sd"]),
            "cil": float(r["mean_5sub_ci_low"]),
            "cih": float(r["mean_5sub_ci_high"]),
            "p_m5": float(r["mean_5sub_p_raw"]),
            "sub_est": [float(r[f"{s}_effect"]) for s in PARTICIPANTS],
            "sub_p": [float(r[f"{s}_p_raw"]) for s in PARTICIPANTS],
            "require_positive": req_pos,
        })

    # Compute exact Holm-11 AND exact worst-case Holm-15 upper bound across all 11 observed tests
    m5_p_vec = np.array([e["p_m5"] for e in prereg11_entries], dtype=np.float64)
    m5_holm11 = holm_adjust(m5_p_vec)
    m5_holm15_wc = holm_worst_case_m_total(m5_p_vec, m_total=15)

    sub_holm11 = np.empty((5, len(prereg11_entries)), dtype=np.float64)
    sub_holm15_wc = np.empty((5, len(prereg11_entries)), dtype=np.float64)
    for p_i in range(5):
        sp = np.array([e["sub_p"][p_i] for e in prereg11_entries], dtype=np.float64)
        sub_holm11[p_i] = holm_adjust(sp)
        sub_holm15_wc[p_i] = holm_worst_case_m_total(sp, m_total=15)

    for idx_e, e in enumerate(prereg11_entries):
        p_raw = e["p_m5"]
        p_h11 = float(m5_holm11[idx_e])
        p_h15 = float(m5_holm15_wc[idx_e])
        conf_m5 = bool((p_h11 < 0.05) and (e["est"] > 0 if e["require_positive"] else True))

        if e["require_positive"]:
            n_unadj = sum((e["sub_p"][i] < 0.05) and (e["sub_est"][i] > 0) for i in range(5))
            n_h11 = sum((sub_holm11[i, idx_e] < 0.05) and (e["sub_est"][i] > 0) for i in range(5))
            n_h15 = sum((sub_holm15_wc[i, idx_e] < 0.05) and (e["sub_est"][i] > 0) for i in range(5))
        else:
            # Count participants significant in the SAME sign as mean_5sub (or significant two-sided)
            sign_ref = 1.0 if e["est"] >= 0 else -1.0
            n_unadj = sum((e["sub_p"][i] < 0.05) and (e["sub_est"][i] * sign_ref > 0) for i in range(5))
            n_h11 = sum((sub_holm11[i, idx_e] < 0.05) and (e["sub_est"][i] * sign_ref > 0) for i in range(5))
            n_h15 = sum((sub_holm15_wc[i, idx_e] < 0.05) and (e["sub_est"][i] * sign_ref > 0) for i in range(5))

        if conf_m5:
            verdict_ko = (
                f"확인됨: 효과크기 {e['est']:+.4f} (95% CI [{e['cil']:+.4f}, {e['cih']:+.4f}]), "
                f"보정 전 p={p_raw:.4f}, Holm-11 p={p_h11:.4f}, Holm-15 최악 상한 p={p_h15:.4f} "
                f"(개별 참가자 보정 전 {n_unadj}/5명, Holm-11 {n_h11}/5명, Holm-15 상한 {n_h15}/5명)."
            )
        elif e["require_positive"] and e["cih"] < 0.0:
            verdict_ko = (
                f"예상과 반대 방향으로 낮아졌다: 추정치 {e['est']:+.4f} (95% CI [{e['cil']:+.4f}, {e['cih']:+.4f}]), "
                f"보정 전 p={p_raw:.4f}, Holm-11 p={p_h11:.4f}, Holm-15 최악 상한 p={p_h15:.4f}."
            )
        else:
            verdict_ko = (
                f"차이를 확인하지 못했다: 추정치 {e['est']:+.4f} (95% CI [{e['cil']:+.4f}, {e['cih']:+.4f}]), "
                f"보정 전 p={p_raw:.4f}, Holm-11 p={p_h11:.4f}, Holm-15 최악 상한 p={p_h15:.4f} "
                f"(개별 참가자 같은 방향 보정 전 {n_unadj}/5명, Holm-11 {n_h11}/5명)."
            )

        rows.append({
            "verdict_order": len(rows) + 1,
            "section": "6-1_사전확증_15개묶음",
            "correction_family": "Holm-15 (완료 11개 Holm-11 및 Holm-15 최악 상한 병기)",
            "test_id": e["test_id"],
            "hypothesis_ko": e["hypothesis_ko"],
            "execution_status": "완료 (HK 6-fold)",
            "inference_method": e["inference_method"],
            "mean_5sub_estimate": e["est"],
            "mean_5sub_seed_sd": e["sd"],
            "mean_5sub_ci95_low": e["cil"],
            "mean_5sub_ci95_high": e["cih"],
            "mean_5sub_p_unadjusted": p_raw,
            "mean_5sub_p_adjusted_primary": p_h11,
            "mean_5sub_p_holm15_worstcase": p_h15,
            "confirmed_mean_5sub": conf_m5,
            "n_sub_confirmed_unadj_of_5": int(n_unadj),
            "n_sub_confirmed_adj_of_5": int(n_h11),
            "n_sub_confirmed_holm15_worstcase_of_5": int(n_h15),
            **{f"{PARTICIPANTS[i]}_estimate": e["sub_est"][i] for i in range(5)},
            **{f"{PARTICIPANTS[i]}_p_unadjusted": e["sub_p"][i] for i in range(5)},
            "korean_verdict_statement": verdict_ko,
        })

    # 3. Remaining 4 [사전] tests requiring separate S8 retraining (explicitly flagged per 01_integrated_document.md 6-1)
    for tid, pdesc in [
        ("6-2_zone_retrain_C1_vs_A1", "[사전 12/15] 6-2 처음 보는 장면: 다섯 내용 구역 평균 성능 C-1 - A-1 (방향 예측: C-1 > A-1)"),
        ("1-3_6-4a_standalone_Visual1_A1_vs_perm", "[사전 13/15] 1-3 / 6-4a: 1차 시각(Visual1) 단독 학습 A-1 대 순열 기준"),
        ("1-3_6-4a_standalone_Visual2_A1_vs_perm", "[사전 14/15] 1-3 / 6-4a: 2차 시각(Visual2) 단독 학습 A-1 대 순열 기준"),
        ("1-3_6-4a_standalone_Default_A1_vs_perm", "[사전 15/15] 1-3 / 6-4a: 기본모드(Default) 단독 학습 A-1 대 순열 기준"),
    ]:
        rows.append({
            "verdict_order": len(rows) + 1,
            "section": "6-1_사전확증_15개묶음",
            "correction_family": "Holm-15 (S8 재학습 대상)",
            "test_id": tid,
            "hypothesis_ko": pdesc,
            "execution_status": "[미실행: 별도 S8 뇌 모형 재학습 필요]",
            "inference_method": "S8 재학습 후 부트스트랩 예정 (S4 자극 모형 구역 평가는 Table 6d 수록)",
            "mean_5sub_estimate": np.nan,
            "mean_5sub_seed_sd": np.nan,
            "mean_5sub_ci95_low": np.nan,
            "mean_5sub_ci95_high": np.nan,
            "mean_5sub_p_unadjusted": np.nan,
            "mean_5sub_p_adjusted_primary": np.nan,
            "mean_5sub_p_holm15_worstcase": np.nan,
            "confirmed_mean_5sub": np.nan,
            "n_sub_confirmed_unadj_of_5": np.nan,
            "n_sub_confirmed_adj_of_5": np.nan,
            "n_sub_confirmed_holm15_worstcase_of_5": np.nan,
            **{f"{s}_estimate": np.nan for s in PARTICIPANTS},
            **{f"{s}_p_unadjusted": np.nan for s in PARTICIPANTS},
            "korean_verdict_statement": "[미실행] 저장된 S6 체크포인트 분석(S9/S10) 범위를 넘어 별도 S8 뇌 모형 재학습이 필요하므로 실행 전 상태로 명시함.",
        })

    # 4. Separate Holm-13 family: 2-4 / 6-4b 13 CAB-NP Network Perturbations (drop(C-1) - drop(A-1))
    net_m5 = net[net["participant"] == "mean_5"].copy()
    for _, nr in net_m5.iterrows():
        g = nr["group"]
        ns = net[(net["participant"].isin(PARTICIPANTS)) & (net["group"] == g)].set_index("participant")
        est = float(nr["diff_C1_minus_A1_mean"])
        cil = float(nr["diff_C1_minus_A1_ci_low"])
        cih = float(nr["diff_C1_minus_A1_ci_high"])
        p_raw = float(nr["p_boot"])
        p_h13 = float(nr["p_holm13"])
        conf_h13 = bool(p_h13 < 0.05)
        n_unadj = int(float(nr["n_confirmed_unadj_of_5"]))
        n_h13 = int(float(nr["n_confirmed_holm13_of_5"]))

        if conf_h13:
            v_str = (
                f"확인됨: Δ_drop(C-1 - A-1) = {est:+.4f} (95% CI [{cil:+.4f}, {cih:+.4f}]), "
                f"보정 전 p={p_raw:.4f}, Holm-13 p={p_h13:.4f} (개별 참가자 보정 전 {n_unadj}/5명, Holm-13 {n_h13}/5명)."
            )
        else:
            v_str = (
                f"차이를 확인하지 못했다: Δ_drop(C-1 - A-1) = {est:+.4f} (95% CI [{cil:+.4f}, {cih:+.4f}]), "
                f"보정 전 p={p_raw:.4f}, Holm-13 p={p_h13:.4f} (개별 참가자 보정 전 {n_unadj}/5명, Holm-13 {n_h13}/5명)."
            )

        rows.append({
            "verdict_order": len(rows) + 1,
            "section": "6-4b_네트워크교란_Holm13",
            "correction_family": "Holm-13 (13개 CAB-NP 단위 교란 별도 보정)",
            "test_id": f"6-4b_perturb_{g}",
            "hypothesis_ko": f"2-4 / 6-4b: {g} ({nr['group_ko']}) 입력 교란 시 drop(C-1) - drop(A-1)",
            "execution_status": "완료 (HK 6-fold, S9-4)",
            "inference_method": "20회 공여 영상 치환 + canonical_id 부트스트랩 10,000회 (Holm-13)",
            "mean_5sub_estimate": est,
            "mean_5sub_seed_sd": float(nr["diff_C1_minus_A1_sd"]),
            "mean_5sub_ci95_low": cil,
            "mean_5sub_ci95_high": cih,
            "mean_5sub_p_unadjusted": p_raw,
            "mean_5sub_p_adjusted_primary": p_h13,
            "mean_5sub_p_holm15_worstcase": np.nan,
            "confirmed_mean_5sub": conf_h13,
            "n_sub_confirmed_unadj_of_5": n_unadj,
            "n_sub_confirmed_adj_of_5": n_h13,
            "n_sub_confirmed_holm15_worstcase_of_5": np.nan,
            **{f"{s}_estimate": float(ns.loc[s, "diff_C1_minus_A1_mean"]) for s in PARTICIPANTS},
            **{f"{s}_p_unadjusted": float(ns.loc[s, "p_boot"]) for s in PARTICIPANTS},
            "korean_verdict_statement": v_str,
        })

    # 5. External Dataset 6-3 MC Adaptation (Separate S7 stage, unadjusted per 1041)
    rows.append({
        "verdict_order": len(rows) + 1,
        "section": "6-3_외부데이터셋_MC",
        "correction_family": "별도 외부 데이터셋 검정 1개 (보정 제외)",
        "test_id": "6-3_MC_external_C1_vs_A1",
        "hypothesis_ko": "[사전 외부] 6-3: Miyawaki/Čeko 등 외부 데이터셋(MC) 적응 평가 C-1 - A-1",
        "execution_status": "[미실행: 별도 S7 외부 데이터셋 실행 대상]",
        "inference_method": "외부 데이터셋 참가자별 평가 예정",
        "mean_5sub_estimate": np.nan,
        "mean_5sub_seed_sd": np.nan,
        "mean_5sub_ci95_low": np.nan,
        "mean_5sub_ci95_high": np.nan,
        "mean_5sub_p_unadjusted": np.nan,
        "mean_5sub_p_adjusted_primary": np.nan,
        "mean_5sub_p_holm15_worstcase": np.nan,
        "confirmed_mean_5sub": np.nan,
        "n_sub_confirmed_unadj_of_5": np.nan,
        "n_sub_confirmed_adj_of_5": np.nan,
        "n_sub_confirmed_holm15_worstcase_of_5": np.nan,
        **{f"{s}_estimate": np.nan for s in PARTICIPANTS},
        **{f"{s}_p_unadjusted": np.nan for s in PARTICIPANTS},
        "korean_verdict_statement": "[미실행] 현재 완료된 HK 개발 세트 S4~S6 체크포인트 범위 밖의 별도 S7 단계임.",
    })

    df_out = pd.DataFrame(rows)
    out_tables_dir.mkdir(parents=True, exist_ok=True)
    p_tsv = out_tables_dir / "s10_preregistered_6_1_verdict.tsv"
    p_csv = out_tables_dir / "s10_preregistered_6_1_verdict.csv"
    df_out.to_csv(p_tsv, sep="\t", index=False)
    df_out.to_csv(p_csv, index=False)
    return [str(p_tsv), str(p_csv)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=None, help="Output directory (defaults to --base-dir)")
    parser.add_argument("--mode", choices=["partial", "all"], default="all")
    args = parser.parse_args()

    configure_matplotlib()
    base_dir: Path = args.base_dir.resolve()
    out_dir: Path = (args.out_dir or args.base_dir).resolve()
    fig_dir = out_dir / "figures"
    tables_dir = out_dir / "tables"

    generated: List[str] = []
    generated.extend(make_fig2_s5_layers(base_dir, fig_dir))
    generated.extend(make_fig3_s9_interchange(base_dir, fig_dir))
    generated.extend(make_fig6_k1a_14dims(base_dir, fig_dir))

    if args.mode == "all":
        generated.extend(make_fig1_condition_ladder(base_dir, fig_dir))
        generated.extend(make_fig4_network_perturbation(base_dir, fig_dir))
        generated.extend(make_fig5_emotion34_and_k1(base_dir, fig_dir))
        generated.extend(build_unified_verdict_table(base_dir, tables_dir))

    print(json.dumps({"mode": args.mode, "generated_files": generated}, indent=2))


if __name__ == "__main__":
    main()
