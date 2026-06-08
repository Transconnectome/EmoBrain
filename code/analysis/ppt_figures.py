"""
PPT slide figures (4 + reuse).

Slide 1  ablation_4axes.png       SwiFT NewE96 × V_binary 의 padding/head/init/mode 4 panel
Slide 2  bfm_comparison.png       3 BFM × 4 task best-condition bar chart
Slide 3  video_comparison.png     5 video × 4 task best-condition bar chart
Slide 4  reuse Phase 2 figures
Slide 5  brainvlm_architecture.png  fMRI → PatchEmbed → ViT → Merger → LLM flow
"""
from pathlib import Path
import warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,
})

OUT = Path("/pscratch/sd/s/sjmoon/FEELIN/docs/reports/ppt_slides_figs")
OUT.mkdir(parents=True, exist_ok=True)

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
RANK = pd.read_csv(FEELIN / "results/phase1/_unified_ranking_per_task.csv").fillna("-")

TASKS = ["V_binary", "A_binary", "V_reg", "A_reg"]
TASK_METRIC = {"V_binary": "AUROC", "A_binary": "AUROC",
               "V_reg": "Pearson r", "A_reg": "Pearson r"}

COL_BFM    = "#3182BD"
COL_VIDEO  = "#E6550D"
COL_GROUP1 = "#6BAED6"
COL_GROUP2 = "#FDAE6B"
COL_GROUP3 = "#74C476"
COL_GROUP4 = "#9E9AC8"
COL_GROUP5 = "#FD8D3C"


# ============================================================
# Slide 1. Ablation 4 axes (SwiFT NewE96 × V_binary as representative)
# ============================================================

def fig_ablation_4axes():
    """4 ablation axes on SwiFT NewE96. For each axis × value, show V_binary + A_binary
    paired (best across other 3 axes, ± across-fold std). NO averaging — each bar is
    'best you can do at this value of the focal axis with the other 3 axes optimized'."""
    AXES = [
        ("padding", ["replicate", "zero", "mean"], COL_GROUP1, "Padding"),
        ("head",    ["linear", "mlp"],             COL_GROUP2, "Head"),
        ("init",    ["resting", "scratch"],        COL_GROUP3, "Pre-training"),
        ("mode",    ["pooled", "per_subject"],     COL_GROUP4, "Subject mode"),
    ]
    LABEL_MAP = {
        ("head", "linear"): "Linear\n(L2 logistic)",
        ("head", "mlp"):    "MLP\n(SwiFT 9.4M)",
        ("init", "resting"): "Resting\npretrained",
        ("init", "scratch"): "Scratch\n(random init)",
        ("mode", "pooled"):    "Pooled\n(shared)",
        ("mode", "per_subject"): "Per-subject\n(individual)",
    }
    TASKS_AB = ["V_binary", "A_binary"]
    TASK_COLOR = {"V_binary": "#3182BD", "A_binary": "#E6550D"}

    base = RANK[(RANK["feature"] == "SwiFT_NewE96") & (RANK["task"].isin(TASKS_AB))].copy()
    base = base[base["padding"].isin(["replicate", "zero", "mean"])]

    fig, axes_plt = plt.subplots(1, 4, figsize=(15, 4.0), sharey=True)
    bar_w = 0.36

    for ax_idx, (axis_name, values, color, title) in enumerate(AXES):
        ax = axes_plt[ax_idx]
        x = np.arange(len(values))
        for ti, task in enumerate(TASKS_AB):
            sub_t = base[base["task"] == task]
            means, stds = [], []
            for v in values:
                cell = sub_t[sub_t[axis_name] == v]
                if len(cell) == 0:
                    means.append(np.nan); stds.append(np.nan); continue
                # best across other 3 axes for this focal value
                top = cell.sort_values("test_main_mean", ascending=False).iloc[0]
                means.append(top["test_main_mean"])
                stds.append(top["test_main_std"] if not pd.isna(top["test_main_std"]) else 0.0)
            bars = ax.bar(x + (ti - 0.5) * bar_w, means, bar_w,
                          yerr=stds, color=TASK_COLOR[task], edgecolor="#252525",
                          linewidth=0.4, capsize=3, label=task)
            for bar, m in zip(bars, means):
                if pd.isna(m): continue
                ax.text(bar.get_x() + bar.get_width()/2, m + 0.008, f"{m:.3f}",
                        ha="center", va="bottom", fontsize=7.5)
        ax.set_xticks(x)
        ax.set_xticklabels([LABEL_MAP.get((axis_name, v), v) for v in values])
        ax.set_title(title)
        if ax_idx == 0:
            ax.set_ylabel("AUROC")
        if ax_idx == 0:
            ax.legend(loc="upper left", frameon=False, fontsize=8, ncol=2)
        ax.set_ylim(0.5, 0.85)
        ax.grid(axis="y", alpha=0.3, linestyle=":")

    fig.suptitle("Phase 1 Ablation 4 axes (SwiFT NewE96, V_binary + A_binary paired, best across other 3 axes)",
                 fontsize=11, y=1.02)
    fig.tight_layout()
    out = OUT / "ablation_4axes.png"
    fig.savefig(out); plt.close(fig)
    print(f"wrote {out}")


# ============================================================
# Slide 2. 3 BFM × 4 task (best condition per BFM × task)
# ============================================================

def fig_bfm_comparison():
    bfms = ["SwiFT_NewE96", "Brain-JEPA", "NeuroSTORM"]
    rows = []
    for bfm in bfms:
        for task in TASKS:
            sub = RANK[(RANK["feature"] == bfm) & (RANK["task"] == task)]
            if len(sub) == 0: continue
            top = sub.sort_values("test_main_mean", ascending=False).iloc[0]
            rows.append({"bfm": bfm, "task": task,
                         "mean": top["test_main_mean"], "std": top["test_main_std"]})
    d = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    x = np.arange(len(TASKS))
    w = 0.26
    colors = [COL_GROUP1, COL_GROUP3, COL_GROUP5]
    for i, bfm in enumerate(bfms):
        sub = d[d["bfm"] == bfm].set_index("task").reindex(TASKS)
        means = sub["mean"].values; stds = sub["std"].values
        bars = ax.bar(x + (i - 1) * w, means, w, yerr=stds, color=colors[i],
                      edgecolor="#252525", linewidth=0.5, capsize=3,
                      label=bfm.replace("_", " "))
        for bar, m in zip(bars, means):
            if pd.isna(m): continue
            ax.text(bar.get_x() + bar.get_width()/2, m + 0.008, f"{m:.3f}",
                    ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels([f"{t}\n({TASK_METRIC[t]})" for t in TASKS])
    ax.set_ylabel("Test main metric")
    ax.set_title("Brain Foundation Model comparison (best condition per BFM × task)")
    ax.legend(loc="upper right", frameon=False, ncol=3)
    ax.set_ylim(0, 0.85)
    ax.grid(axis="y", alpha=0.3, linestyle=":")
    fig.tight_layout()
    out = OUT / "bfm_comparison.png"
    fig.savefig(out); plt.close(fig)
    print(f"wrote {out}")


# ============================================================
# Slide 3. 5 video encoder × 4 task
# ============================================================

def fig_video_comparison():
    videos = ["CLIP_pretrained", "DINOv2_pretrained", "V-JEPA2_pretrained",
              "VideoMAE_pretrained", "Qwen-VL_caption"]
    short  = {"CLIP_pretrained": "CLIP",
              "DINOv2_pretrained": "DINOv2",
              "V-JEPA2_pretrained": "V-JEPA2",
              "VideoMAE_pretrained": "VideoMAE",
              "Qwen-VL_caption": "Qwen-VL caption"}
    rows = []
    for v in videos:
        for task in TASKS:
            sub = RANK[(RANK["feature"] == v) & (RANK["task"] == task)]
            if len(sub) == 0: continue
            top = sub.sort_values("test_main_mean", ascending=False).iloc[0]
            rows.append({"video": v, "task": task,
                         "mean": top["test_main_mean"], "std": top["test_main_std"]})
    d = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    x = np.arange(len(TASKS))
    w = 0.16
    colors = [COL_VIDEO, COL_GROUP2, COL_GROUP3, COL_GROUP4, COL_GROUP5]
    for i, v in enumerate(videos):
        sub = d[d["video"] == v].set_index("task").reindex(TASKS)
        means = sub["mean"].values; stds = sub["std"].values
        bars = ax.bar(x + (i - 2) * w, means, w, yerr=stds, color=colors[i],
                      edgecolor="#252525", linewidth=0.5, capsize=2.5, label=short[v])
        for bar, m in zip(bars, means):
            if pd.isna(m): continue
            ax.text(bar.get_x() + bar.get_width()/2, m + 0.012, f"{m:.3f}",
                    ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels([f"{t}\n({TASK_METRIC[t]})" for t in TASKS])
    ax.set_ylabel("Test main metric")
    ax.set_title("Video Foundation Model prediction (best condition per encoder × task)")
    ax.legend(loc="upper right", frameon=False, ncol=5, fontsize=7.5)
    ax.set_ylim(0, 1.08)
    ax.grid(axis="y", alpha=0.3, linestyle=":")
    fig.tight_layout()
    out = OUT / "video_comparison.png"
    fig.savefig(out); plt.close(fig)
    print(f"wrote {out}")


# ============================================================
# Slide 5. BrainVLM architecture diagram
# ============================================================

def fig_brainvlm_architecture():
    """Clean linear dataflow. fMRI input on left → trainable patch embed → frozen ViT
    → trainable merger → frozen LLM → XML output on right."""
    fig, ax = plt.subplots(figsize=(14, 5.5))
    ax.set_xlim(0, 28); ax.set_ylim(0, 10)
    ax.set_aspect("equal"); ax.axis("off")

    COL_INPUT  = "#3182BD33"; EDGE_INPUT  = "#3182BD"
    COL_TRAIN  = "#9E9E9E"
    COL_FROZEN = "#E0E0E0"
    COL_OUT    = "#252525"
    COL_OUTPUT_BOX = "#E6550D33"; EDGE_OUTPUT = "#E6550D"

    def box(x, y, w, h, label, fc, ec="#252525", lw=0.7, fs=9, fw="normal"):
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.15",
                                       linewidth=lw, edgecolor=ec, facecolor=fc)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, label, ha="center", va="center",
                fontsize=fs, color=COL_OUT, fontweight=fw)

    def arrow(x1, y1, x2, y2, color="#252525", lw=1.0):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw))

    # 7 columns left-to-right (linear flow)
    # x positions of each stage
    XS = [0.5, 4.5, 7.8, 11.6, 15.4, 19.2, 23.0]
    Y_BAR = 4.0  # vertical center of main row
    BH = 2.0
    BW = 3.4

    # 1. Input fMRI
    box(XS[0], Y_BAR, BW, BH,
        "fMRI volume\n\n(1, 1, 96, 96, 96, 20)",
        fc=COL_INPUT, ec=EDGE_INPUT, fs=8.5, fw="bold")

    # 2. PatchEmbedQwen (trainable)
    box(XS[1], Y_BAR, BW, BH,
        "PatchEmbedQwen.fMRI\n\ntrainable ~30M\npatch (16,16,16,5)",
        fc=COL_TRAIN, fs=8.5)

    # 3. Qwen3-VL ViT (frozen)
    box(XS[2], Y_BAR, BW, BH,
        "Qwen3-VL ViT\n\nFROZEN\n~700M",
        fc=COL_FROZEN, fs=9, fw="bold")

    # 4. visual hidden (intermediate, slim)
    box(XS[3], Y_BAR + 0.4, BW - 0.6, BH - 0.8,
        "visual hidden\n(N, 1152)",
        fc="white", fs=8)

    # 5. Custom Merger (trainable)
    box(XS[4], Y_BAR, BW, BH,
        "CustomMerger\n\ntrainable ~12M\n1152 → 2048",
        fc=COL_TRAIN, fs=8.5)

    # 6. Qwen3-VL LLM (frozen)
    box(XS[5], Y_BAR, BW, BH,
        "Qwen3-VL LLM\n\nFROZEN\n~1.5B",
        fc=COL_FROZEN, fs=9, fw="bold")

    # 7. XML output
    box(XS[6], Y_BAR - 0.5, BW + 1.6, BH + 1.0,
        "<Emotion_Analysis>\n  <Valence>2.22</Valence>\n  <Arousal>5.56</Arousal>\n  <Caption>...</Caption>\n</Emotion_Analysis>",
        fc=COL_OUTPUT_BOX, ec=EDGE_OUTPUT, fs=8)

    # Arrows between stages
    for i in range(len(XS) - 1):
        x1 = XS[i] + BW
        x2 = XS[i+1]
        arrow(x1, Y_BAR + BH/2, x2, Y_BAR + BH/2, lw=1.2)

    # Tokens / patches label between PatchEmbed and ViT
    ax.text((XS[1] + BW + XS[2]) / 2, Y_BAR + BH + 0.5,
            "vision tokens\n(N, 1152)", ha="center", fontsize=7.5, style="italic", color="#555")
    ax.text((XS[4] + BW + XS[5]) / 2, Y_BAR + BH + 0.5,
            "LLM tokens\n(N, 2048)", ha="center", fontsize=7.5, style="italic", color="#555")
    ax.text((XS[5] + BW + XS[6]) / 2, Y_BAR + BH + 0.5,
            "autoregressive\ngenerate", ha="center", fontsize=7.5, style="italic", color="#555")

    # Title
    ax.text(14, 8.8, "BrainVLM (Phase 3, currently training)",
            ha="center", fontsize=14, fontweight="bold")
    ax.text(14, 7.9,
            "fMRI volume → trainable patch embed → frozen Qwen3-VL ViT → trainable merger → frozen LLM → V/A XML",
            ha="center", fontsize=9, color="#555", style="italic")

    # Legend at bottom
    leg = [
        mpatches.Patch(facecolor=COL_INPUT, edgecolor=EDGE_INPUT, label="fMRI input"),
        mpatches.Patch(facecolor=COL_TRAIN, edgecolor="#252525",
                       label="trainable (PatchEmbedQwen + Merger = ~42M, 2% of Qwen3-VL)"),
        mpatches.Patch(facecolor=COL_FROZEN, edgecolor="#252525",
                       label="frozen (Qwen3-VL ViT + LLM = ~2.2B)"),
        mpatches.Patch(facecolor=COL_OUTPUT_BOX, edgecolor=EDGE_OUTPUT, label="output (V/A XML)"),
    ]
    ax.legend(handles=leg, loc="lower center", bbox_to_anchor=(0.5, -0.05),
              frameon=False, fontsize=9, ncol=4)

    fig.tight_layout()
    out = OUT / "brainvlm_architecture.png"
    fig.savefig(out, bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"wrote {out}")


# ============================================================

# ============================================================
# Slide 2 Cat34 add-on. 3 BFM × 2 Cat34 task
# ============================================================

def fig_bfm_cat34():
    cat34 = pd.read_csv(FEELIN / "results/phase1/cat34_probe_linear.csv").fillna("-")
    cat34 = cat34[cat34["mode"].isin(["pooled", "per_subject"])]
    bfms = ["SwiFT_NewE96", "Brain-JEPA", "NeuroSTORM"]
    cat_tasks = ["Cat34_multilabel", "Cat34_soft"]
    metric_label = {"Cat34_multilabel": "macro AUROC", "Cat34_soft": "mean Pearson r"}

    rows = []
    for bfm in bfms:
        for task in cat_tasks:
            sub = cat34[(cat34["feature"] == bfm) & (cat34["task"] == task)]
            if len(sub) == 0: continue
            agg = sub.groupby(["init", "mode"]).agg(m=("test_main", "mean"),
                                                     s=("test_main", "std")).reset_index()
            best = agg.sort_values("m", ascending=False).iloc[0]
            rows.append({"bfm": bfm, "task": task, "mean": best["m"], "std": best["s"]})
    d = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(9, 4.6))
    x = np.arange(len(cat_tasks))
    w = 0.26
    colors = [COL_GROUP1, COL_GROUP3, COL_GROUP5]
    for i, bfm in enumerate(bfms):
        sub = d[d["bfm"] == bfm].set_index("task").reindex(cat_tasks)
        means = sub["mean"].values; stds = sub["std"].values
        bars = ax.bar(x + (i - 1) * w, means, w, yerr=stds, color=colors[i],
                      edgecolor="#252525", linewidth=0.5, capsize=4,
                      label=bfm.replace("_", " "))
        for bar, m in zip(bars, means):
            if pd.isna(m): continue
            ax.text(bar.get_x() + bar.get_width()/2, m + 0.012, f"{m:.3f}",
                    ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels([f"{t}\n({metric_label[t]})" for t in cat_tasks])
    ax.set_ylabel("Test main metric")
    ax.set_title("Brain Foundation Model on Cat34 (best condition per BFM × task)")
    ax.legend(loc="upper right", frameon=False, ncol=3)
    ax.set_ylim(0, 0.8)
    ax.grid(axis="y", alpha=0.3, linestyle=":")
    fig.tight_layout()
    out = OUT / "bfm_cat34.png"
    fig.savefig(out); plt.close(fig)
    print(f"wrote {out}")


# ============================================================
# Slide 4 Cat34 add-on. 9 paradigm × 2 Cat34 task heatmap
# ============================================================

def fig_phase2_cat34():
    import glob
    rows = []
    for f in glob.glob(str(FEELIN / "results/phase2/brain_only/*/Cat34_*.csv")):
        d = pd.read_csv(f)
        method = f.split("brain_only/")[1].split("/")[0]
        task = f.split("/")[-1].replace(".csv", "")
        rows.append({"method": method, "task": task,
                     "mean": d["test_main"].mean(), "kind": "brain_only"})
    for arch in ["A", "B", "D"]:
        for task in ["Cat34_multilabel", "Cat34_soft"]:
            f = str(FEELIN / f"results/phase2/{arch}/{task}.csv")
            d = pd.read_csv(f)
            method = {"A": "A_token", "B": "B_cross", "D": "D_late"}[arch]
            rows.append({"method": method, "task": task,
                         "mean": d["test_main"].mean(), "kind": "joint"})
    for v in ["joint", "brain_only"]:
        for task in ["Cat34_multilabel", "Cat34_soft"]:
            f = str(FEELIN / f"results/phase2/C/probe_{v}_{task}.csv")
            d = pd.read_csv(f)
            rows.append({"method": f"C_contrastive_{v}", "task": task,
                         "mean": d["test_main"].mean(),
                         "kind": "joint" if v == "joint" else "brain_only"})
    df = pd.DataFrame(rows)

    pv = df.pivot_table(index="method", columns="task", values="mean").reindex(
        columns=["Cat34_multilabel", "Cat34_soft"])
    # Order: joint top (A, B, C_joint, D), brain_only bottom (I, II, III, IV, C_brain)
    order_joint = ["A_token", "B_cross", "C_contrastive_joint", "D_late"]
    order_brain = ["I_supervised", "II_distillation", "III_multitask",
                   "IV_subject_aware", "C_contrastive_brain_only"]
    pv = pv.reindex(order_joint + order_brain)

    fig, ax = plt.subplots(figsize=(6.5, max(3.8, 0.35 * len(pv))))
    vmin, vmax = 0.2, 0.9
    im = ax.imshow(pv.values, aspect="auto", cmap="viridis", vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(pv.columns))); ax.set_xticklabels(
        [f"{c}\n({'macro AUROC' if 'multi' in c else 'mean r'})" for c in pv.columns])
    ax.set_yticks(range(len(pv))); ax.set_yticklabels(pv.index)
    for i in range(len(pv)):
        for j in range(len(pv.columns)):
            v = pv.values[i, j]
            if pd.isna(v): continue
            color = "white" if v < (vmax - vmin) * 0.5 + vmin else "black"
            ax.text(j, i, f"{v:.3f}", ha="center", va="center", fontsize=8, color=color)
    ax.axhline(len(order_joint) - 0.5, color="white", linewidth=1.2)
    cbar = plt.colorbar(im, ax=ax, fraction=0.05, pad=0.04)
    cbar.set_label("Test main metric", fontsize=8)
    ax.set_title("Phase 2 paradigm × Cat34 task heatmap")
    fig.tight_layout()
    out = OUT / "phase2_cat34_heatmap.png"
    fig.savefig(out); plt.close(fig)
    print(f"wrote {out}")


# ============================================================
# Slide 5 add-on. BrainVLM training loss curve
# ============================================================

def fig_brainvlm_loss():
    df = pd.read_csv("/tmp/brainvlm_loss.csv")
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(df["epoch"], df["loss"], color="#3182BD", linewidth=1.2)
    # epoch dividers
    for e in [1, 2]:
        ax.axvline(e, color="#9E9E9E", linestyle="--", linewidth=0.5)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Training loss (causal LM)")
    ax.set_title("BrainVLM training loss (fold 1, 3 epochs, 6,555 samples × 5 subj)")
    ax.set_xlim(0, 3.0)
    ax.set_yscale("log")
    ax.grid(True, alpha=0.3, which="both")
    # annotate endpoints
    ax.text(0.05, df["loss"].iloc[0], f"  start = {df['loss'].iloc[0]:.2f}",
            fontsize=8, va="center")
    ax.text(2.95, df["loss"].iloc[-1], f"end = {df['loss'].iloc[-1]:.3f}  ",
            fontsize=8, va="center", ha="right")
    fig.tight_layout()
    out = OUT / "brainvlm_loss_curve.png"
    fig.savefig(out); plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    fig_ablation_4axes()
    fig_bfm_comparison()
    fig_video_comparison()
    fig_brainvlm_architecture()
    fig_bfm_cat34()
    fig_phase2_cat34()
    fig_brainvlm_loss()
