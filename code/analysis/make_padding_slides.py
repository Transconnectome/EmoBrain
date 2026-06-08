"""
Generate 3 slide-ready figures for padding ablation results.
Outputs PNG (300 DPI) to /pscratch/sd/s/sjmoon/FEELIN/results/background/padding_ablation/figures/
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path("/pscratch/sd/s/sjmoon/FEELIN/results/background/padding_ablation")
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Load all 4 runs
d_sub01 = pd.read_csv(ROOT / "sub01_NewE96_probe.csv")
d_small = pd.read_csv(ROOT / "sub01_smallmlp_probe.csv")
d_pool = pd.read_csv(ROOT / "allsubj_pooled_swift_probe.csv")
d_psub = pd.read_csv(ROOT / "allsubj_persubj_swift_probe.csv")

PAD_ORDER = ["replicate", "zero", "mean"]
PAD_COLORS = {"replicate": "#d4a373", "zero": "#a8d5ba", "mean": "#5a8dee"}

# ============================================================
# FIGURE 1: PADDING WINNER (V + A panels, 4 runs)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

RUN_LABELS = ["Sub-01\nSwift MLP\n(n=905)",
              "Sub-01\nSmall MLP\n(n=905)",
              "Pooled\nSwift MLP\n(n=4,525)",
              "Per-subject\nSwift MLP\n(n=905×5)"]
RUNS = [d_sub01, d_small, d_pool, d_psub]

x = np.arange(len(RUN_LABELS))
width = 0.27

for ax, task, task_name in [(axes[0], "V", "Valence (Q4 vs Q1)"),
                              (axes[1], "A", "Arousal (Q4 vs Q1)")]:
    for i, pad in enumerate(PAD_ORDER):
        means, stds = [], []
        for df in RUNS:
            sub = df[(df["task"] == task) & (df["padding"] == pad)]
            means.append(sub["test_auroc"].mean())
            stds.append(sub["test_auroc"].std())
        offset = (i - 1) * width
        bars = ax.bar(x + offset, means, width, yerr=stds, capsize=3,
                      color=PAD_COLORS[pad], edgecolor="black", linewidth=0.5,
                      label=pad, error_kw={"linewidth": 0.8})
        for j, (m, s) in enumerate(zip(means, stds)):
            ax.annotate(f"{m:.3f}", xy=(x[j] + offset, m + s + 0.008),
                        ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    ax.axhline(0.5, color="grey", ls="--", lw=0.8, alpha=0.7, label="chance")
    ax.set_xticks(x)
    ax.set_xticklabels(RUN_LABELS)
    ax.set_ylabel("Test AUROC")
    ax.set_title(task_name)
    ax.set_ylim(0.40, 0.78)
    ax.grid(axis="y", alpha=0.25, ls=":")
    if task == "V":
        ax.legend(title="Padding", loc="lower right", ncol=2)

fig.suptitle("Padding ablation: 'mean' wins across all 4 runs (SwiFT NewE96)",
             fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(OUT / "fig1_padding_winner.png", dpi=300, bbox_inches="tight")
plt.close()
print(f"[saved] {OUT / 'fig1_padding_winner.png'}")

# ============================================================
# FIGURE 2: LINEAR vs MLP across modes
# ============================================================
fig, ax = plt.subplots(figsize=(9, 5.5))

mode_specs = [
    ("Sub-01\n(n=905)", d_sub01),
    ("Per-subject\n(n=905 × 5)", d_psub),
    ("Pooled\n(n=4,525)", d_pool),
]
HEAD_COLORS = {"linear": "#2d7d6a", "mlp": "#c0392b"}
head_labels = ["linear", "mlp"]

x = np.arange(len(mode_specs))
width = 0.35

# aggregate mean+std over (init, padding, task, seed) -> per head
means_lin, stds_lin, means_mlp, stds_mlp = [], [], [], []
for label, df in mode_specs:
    lin = df[df["head"] == "linear"]["test_auroc"]
    mlp = df[df["head"] == "mlp"]["test_auroc"]
    means_lin.append(lin.mean()); stds_lin.append(lin.std())
    means_mlp.append(mlp.mean()); stds_mlp.append(mlp.std())

ax.bar(x - width/2, means_lin, width, yerr=stds_lin, capsize=4,
       color=HEAD_COLORS["linear"], edgecolor="black", linewidth=0.5,
       label="Linear (logistic L2)")
ax.bar(x + width/2, means_mlp, width, yerr=stds_mlp, capsize=4,
       color=HEAD_COLORS["mlp"], edgecolor="black", linewidth=0.5,
       label="MLP (SwiFT 9.4M)")

# Bar value labels
for i, (lm, ls, mm, ms) in enumerate(zip(means_lin, stds_lin, means_mlp, stds_mlp)):
    ax.annotate(f"{lm:.3f}", xy=(i - width/2, lm + ls + 0.005),
                ha="center", va="bottom", fontsize=9, fontweight="bold",
                color=HEAD_COLORS["linear"])
    ax.annotate(f"{mm:.3f}", xy=(i + width/2, mm + ms + 0.005),
                ha="center", va="bottom", fontsize=9, fontweight="bold",
                color=HEAD_COLORS["mlp"])

# Annotate deltas
for i, (lm, mm) in enumerate(zip(means_lin, means_mlp)):
    delta = lm - mm
    y = max(lm + stds_lin[i], mm + stds_mlp[i]) + 0.040
    ax.annotate(f"Δ = {delta:+.3f}", xy=(i, y), ha="center", fontsize=10,
                color="black", fontweight="bold")

ax.axhline(0.5, color="grey", ls="--", lw=0.8, alpha=0.7)
ax.set_xticks(x)
ax.set_xticklabels([m[0] for m in mode_specs])
ax.set_ylabel("Test AUROC (mean across cells)")
ax.set_title("Linear consistently beats MLP — MLP overfits even at n=4,525")
ax.set_ylim(0.45, 0.76)
ax.grid(axis="y", alpha=0.25, ls=":")
ax.legend(loc="upper left")

plt.tight_layout()
plt.savefig(OUT / "fig2_linear_vs_mlp.png", dpi=300, bbox_inches="tight")
plt.close()
print(f"[saved] {OUT / 'fig2_linear_vs_mlp.png'}")

# ============================================================
# FIGURE 3: Resting vs Scratch (pretrain effect)
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5.5))

# 4 groups: (Sub-01 linear, Sub-01 MLP, Pooled linear, Pooled MLP, Per-subj linear, Per-subj MLP)
groups = [
    ("Sub-01\nlinear",  d_sub01, "linear"),
    ("Sub-01\nMLP",     d_sub01, "mlp"),
    ("Per-subject\nlinear", d_psub, "linear"),
    ("Per-subject\nMLP",    d_psub, "mlp"),
    ("Pooled\nlinear",  d_pool, "linear"),
    ("Pooled\nMLP",     d_pool, "mlp"),
]
INIT_COLORS = {"resting": "#3498db", "scratch": "#95a5a6"}

x = np.arange(len(groups))
width = 0.36

means_rest, stds_rest, means_scr, stds_scr = [], [], [], []
for label, df, head in groups:
    r = df[(df["init"]=="resting") & (df["head"]==head)]["test_auroc"]
    s = df[(df["init"]=="scratch") & (df["head"]==head)]["test_auroc"]
    means_rest.append(r.mean()); stds_rest.append(r.std())
    means_scr.append(s.mean()); stds_scr.append(s.std())

ax.bar(x - width/2, means_rest, width, yerr=stds_rest, capsize=4,
       color=INIT_COLORS["resting"], edgecolor="black", linewidth=0.5,
       label="Resting-pretrained")
ax.bar(x + width/2, means_scr, width, yerr=stds_scr, capsize=4,
       color=INIT_COLORS["scratch"], edgecolor="black", linewidth=0.5,
       label="Scratch (random init)")

# Bar value labels
for i, (rm, rs, sm, ss) in enumerate(zip(means_rest, stds_rest, means_scr, stds_scr)):
    ax.annotate(f"{rm:.3f}", xy=(i - width/2, rm + rs + 0.005),
                ha="center", va="bottom", fontsize=8.5, fontweight="bold",
                color=INIT_COLORS["resting"])
    ax.annotate(f"{sm:.3f}", xy=(i + width/2, sm + ss + 0.005),
                ha="center", va="bottom", fontsize=8.5, fontweight="bold",
                color=INIT_COLORS["scratch"])

for i, (rm, sm) in enumerate(zip(means_rest, means_scr)):
    delta = rm - sm
    y = max(rm + stds_rest[i], sm + stds_scr[i]) + 0.034
    color = "black" if abs(delta) > 0.02 else "grey"
    ax.annotate(f"Δ = {delta:+.3f}", xy=(i, y), ha="center", fontsize=9.5,
                color=color, fontweight="bold" if abs(delta) > 0.02 else "normal")

ax.axhline(0.5, color="grey", ls="--", lw=0.8, alpha=0.7)
ax.set_xticks(x)
ax.set_xticklabels([g[0] for g in groups])
ax.set_ylabel("Test AUROC (mean across padding × task × seed)")
ax.set_title("Pretrain effect: visible only with Linear + Pooled (Δ = +6.5pt)")
ax.set_ylim(0.45, 0.76)
ax.grid(axis="y", alpha=0.25, ls=":")
ax.legend(loc="upper left")

plt.tight_layout()
plt.savefig(OUT / "fig3_pretrain_effect.png", dpi=300, bbox_inches="tight")
plt.close()
print(f"[saved] {OUT / 'fig3_pretrain_effect.png'}")

print(f"\nAll 3 figures in: {OUT}/")
