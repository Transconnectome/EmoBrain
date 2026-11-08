"""
3-BFM comparison figure: SwiFT NewE96 + Brain-JEPA + NeuroSTORM (padding=mean = spatial-only).

Pooled mode only (cross-subject shared representation).
Shows 3 BFM x 2 init (resting/scratch) x 2 head (linear/mlp) bars per task panel.

Output:
  results/main_grid_3bfm/fig_3bfm_pooled.png
  results/main_grid_3bfm/fig_3bfm_persubj.png
"""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path("/pscratch/sd/s/sjmoon/EmoBrain/results")
OUT = ROOT / "main_grid_3bfm"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 13, "axes.labelsize": 12,
    "legend.fontsize": 9, "xtick.labelsize": 10, "ytick.labelsize": 10,
    "axes.spines.top": False, "axes.spines.right": False,
})

# Load SwiFT NewE96 results (padding=mean only, to match BJ/NS extraction)
swift_pool = pd.read_csv(ROOT / "padding_ablation/allsubj_pooled_swift_probe.csv")
swift_pers = pd.read_csv(ROOT / "padding_ablation/allsubj_persubj_swift_probe.csv")
swift_pool = swift_pool[swift_pool["padding"] == "mean"].copy()
swift_pers = swift_pers[swift_pers["padding"] == "mean"].copy()
swift_pool["model"] = "SwiFT_NewE96"
swift_pers["model"] = "SwiFT_NewE96"

# Load new BJ+NS results
bjns = pd.read_csv(OUT / "probe_full.csv")
bjns_pool = bjns[bjns["mode"] == "pooled"].copy()
bjns_pers = bjns[bjns["mode"] == "per_subject"].copy()

# Combine
common_cols = ["model","init","task","head","seed","test_auroc","test_auprc","test_bal_acc"]
pool = pd.concat([swift_pool[common_cols], bjns_pool[common_cols]], ignore_index=True)
pers = pd.concat([swift_pers[common_cols], bjns_pers[common_cols]], ignore_index=True)

MODELS = ["SwiFT_NewE96", "Brain-JEPA", "NeuroSTORM"]
INITS = ["resting", "scratch"]
HEADS = ["linear", "mlp"]
TASKS = ["V", "A"]

INIT_HEAD_COLORS = {
    ("resting", "linear"): "#1f4e79",
    ("resting", "mlp"):    "#5b9bd5",
    ("scratch", "linear"): "#7f7f7f",
    ("scratch", "mlp"):    "#bfbfbf",
}
INIT_HEAD_LABELS = {
    ("resting", "linear"): "Resting + Linear",
    ("resting", "mlp"):    "Resting + MLP",
    ("scratch", "linear"): "Scratch + Linear",
    ("scratch", "mlp"):    "Scratch + MLP",
}


def make_panel(ax, df, task, task_name, ylim, title_suffix=""):
    """4 bars (init x head) per BFM, side by side."""
    n_bars = 4
    x = np.arange(len(MODELS))
    width = 0.20
    bar_specs = [(i, ih) for i, ih in enumerate(
        [("resting","linear"), ("resting","mlp"),
         ("scratch","linear"), ("scratch","mlp")])]

    for i, (init, head) in [(idx, ih) for idx, ih in bar_specs]:
        means, stds = [], []
        for m in MODELS:
            sub = df[(df["model"]==m) & (df["init"]==init) &
                     (df["task"]==task) & (df["head"]==head)]
            means.append(sub["test_auroc"].mean())
            stds.append(sub["test_auroc"].std())
        offset = (i - 1.5) * width
        ax.bar(x + offset, means, width, yerr=stds, capsize=2.5,
               color=INIT_HEAD_COLORS[(init, head)],
               edgecolor="black", linewidth=0.5,
               label=INIT_HEAD_LABELS[(init, head)],
               error_kw={"linewidth": 0.7})
        for j, (m_, s_) in enumerate(zip(means, stds)):
            ax.annotate(f"{m_:.3f}",
                        xy=(x[j] + offset, m_ + (s_ if not np.isnan(s_) else 0) + 0.006),
                        ha="center", va="bottom", fontsize=7,
                        color=INIT_HEAD_COLORS[(init, head)])

    ax.axhline(0.5, color="grey", ls="--", lw=0.8, alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(MODELS, fontsize=11)
    ax.set_ylabel("Test AUROC")
    ax.set_title(f"{task_name}{title_suffix}")
    ax.set_ylim(*ylim)
    ax.grid(axis="y", alpha=0.25, ls=":")


# ============ POOLED FIGURE ============
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
make_panel(axes[0], pool, "V", "Valence (Q4 vs Q1)", (0.40, 0.82))
make_panel(axes[1], pool, "A", "Arousal (Q4 vs Q1)", (0.40, 0.82))
axes[1].legend(title="Init × Head", loc="upper right", framealpha=0.95, fontsize=8.5)
fig.suptitle("3-BFM Comparison (Pooled, n_train ≈ 4,525; padding = mean = spatial-only)",
             fontsize=14, y=1.02)
plt.tight_layout()
out_path = OUT / "fig_3bfm_pooled.png"
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"[saved] {out_path}")

# ============ PER-SUBJECT FIGURE ============
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
make_panel(axes[0], pers, "V", "Valence (Q4 vs Q1)", (0.40, 0.82))
make_panel(axes[1], pers, "A", "Arousal (Q4 vs Q1)", (0.40, 0.82))
axes[1].legend(title="Init × Head", loc="upper right", framealpha=0.95, fontsize=8.5)
fig.suptitle("3-BFM Comparison (Per-subject, 5 subj mean ± std; padding = mean = spatial-only)",
             fontsize=14, y=1.02)
plt.tight_layout()
out_path = OUT / "fig_3bfm_persubj.png"
plt.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"[saved] {out_path}")

# ============ Summary numbers ============
print("\n=== Aggregate per (BFM, head) [pooled] ===")
print(pool.groupby(["model","head"])["test_auroc"].agg(["mean","std"]).round(4))
print("\n=== Aggregate per (BFM, head) [per-subject] ===")
print(pers.groupby(["model","head"])["test_auroc"].agg(["mean","std"]).round(4))
print("\n=== Best cell per BFM (pooled, resting, linear) ===")
best = pool[(pool["init"]=="resting") & (pool["head"]=="linear")]
print(best.groupby(["model","task"])[["test_auroc","test_auprc","test_bal_acc"]].mean().round(4))
