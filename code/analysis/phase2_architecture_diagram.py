"""
Phase 2 architecture diagram. 8 methods on one canvas.
Top row    : 4 joint paradigms (A token-attn / B cross-attn / C contrastive / D late fusion).
Bottom row : 4 brain-only paradigms (I supervised / II distillation / III multitask / IV subject-aware).

Output: reports/phase2_wrapup/figs/architecture_8methods.png
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams

rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 8,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,
})

OUT = Path("/pscratch/sd/s/sjmoon/FEELIN/reports/phase2_wrapup/figs/architecture_8methods.png")
OUT.parent.mkdir(parents=True, exist_ok=True)

COL_BRAIN  = "#3182BD"  # blue
COL_VIDEO  = "#E6550D"  # orange
COL_TRAIN  = "#9E9E9E"  # grey block (trainable)
COL_FROZEN = "#E0E0E0"  # light grey block (frozen)
COL_OUT    = "#252525"
COL_LOSS   = "#D62728"
COL_TEACH  = "#A1D99B"


def box(ax, x, y, w, h, label, fc="#FFFFFF", ec=COL_OUT, lw=0.7, fontsize=7, italic=False):
    rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                   linewidth=lw, edgecolor=ec, facecolor=fc)
    ax.add_patch(rect)
    style = "italic" if italic else "normal"
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            fontsize=fontsize, color=COL_OUT, style=style)


def arrow(ax, x1, y1, x2, y2, color=COL_OUT, lw=0.7, style="-|>"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw))


def draw_panel_title(ax, title, sub=""):
    ax.text(0.5, 0.96, title, ha="center", va="top", fontsize=9, fontweight="bold",
            transform=ax.transAxes, color=COL_OUT)
    if sub:
        ax.text(0.5, 0.89, sub, ha="center", va="top", fontsize=7,
                transform=ax.transAxes, color="#555555", style="italic")


def setup_panel(ax):
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.set_aspect("equal")
    ax.axis("off")


# ============================================================
# Joint paradigms (top row)
# ============================================================

def panel_A_token_attention(ax):
    setup_panel(ax)
    draw_panel_title(ax, "A. Token attention", "brain + video as 2 tokens → transformer → CLS")
    box(ax, 0.6, 7.0, 2.4, 1.0, "brain\nfeature", fc=COL_BRAIN + "33", ec=COL_BRAIN)
    box(ax, 7.0, 7.0, 2.4, 1.0, "video\nfeature", fc=COL_VIDEO + "33", ec=COL_VIDEO)
    box(ax, 0.6, 5.4, 2.4, 0.9, "linear proj", fc=COL_TRAIN)
    box(ax, 7.0, 5.4, 2.4, 0.9, "linear proj", fc=COL_TRAIN)
    arrow(ax, 1.8, 7.0, 1.8, 6.3); arrow(ax, 8.2, 7.0, 8.2, 6.3)
    box(ax, 1.6, 3.6, 6.8, 1.4, "[CLS] + brain_tok + video_tok\n→ 2-layer Transformer encoder",
        fc=COL_TRAIN, fontsize=7)
    arrow(ax, 1.8, 5.4, 3.0, 5.0); arrow(ax, 8.2, 5.4, 7.0, 5.0)
    box(ax, 4.0, 1.7, 2.0, 0.9, "CLS → linear", fc=COL_TRAIN)
    arrow(ax, 5.0, 3.6, 5.0, 2.6)
    box(ax, 4.0, 0.3, 2.0, 0.9, "V / A", fc=COL_OUT, ec=COL_OUT, fontsize=8)
    ax.text(5.0, 0.75, "V / A", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    arrow(ax, 5.0, 1.7, 5.0, 1.2)


def panel_B_cross_attention(ax):
    setup_panel(ax)
    draw_panel_title(ax, "B. Cross-attention", "brain ↔ video bidirectional attn")
    box(ax, 0.6, 7.4, 2.4, 1.0, "brain\nfeature", fc=COL_BRAIN + "33", ec=COL_BRAIN)
    box(ax, 7.0, 7.4, 2.4, 1.0, "video\nfeature", fc=COL_VIDEO + "33", ec=COL_VIDEO)
    box(ax, 0.6, 5.4, 2.4, 1.0, "brain ←attend←\nvideo", fc=COL_TRAIN, fontsize=6.5)
    box(ax, 7.0, 5.4, 2.4, 1.0, "video ←attend←\nbrain", fc=COL_TRAIN, fontsize=6.5)
    arrow(ax, 1.8, 7.4, 1.8, 6.4); arrow(ax, 8.2, 7.4, 8.2, 6.4)
    arrow(ax, 3.0, 5.9, 7.0, 5.9, lw=0.5)
    arrow(ax, 7.0, 5.7, 3.0, 5.7, lw=0.5)
    box(ax, 0.6, 3.6, 2.4, 1.0, "brain'", fc=COL_TRAIN)
    box(ax, 7.0, 3.6, 2.4, 1.0, "video'", fc=COL_TRAIN)
    arrow(ax, 1.8, 5.4, 1.8, 4.6); arrow(ax, 8.2, 5.4, 8.2, 4.6)
    box(ax, 3.0, 1.8, 4.0, 1.0, "concat → linear", fc=COL_TRAIN)
    arrow(ax, 1.8, 3.6, 3.5, 2.8); arrow(ax, 8.2, 3.6, 6.5, 2.8)
    box(ax, 4.0, 0.3, 2.0, 0.9, "", fc=COL_OUT, ec=COL_OUT)
    ax.text(5.0, 0.75, "V / A", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    arrow(ax, 5.0, 1.8, 5.0, 1.2)


def panel_C_contrastive(ax):
    setup_panel(ax)
    draw_panel_title(ax, "C. Contrastive alignment", "InfoNCE align then probe")
    box(ax, 0.6, 7.6, 2.4, 1.0, "brain\nfeature", fc=COL_BRAIN + "33", ec=COL_BRAIN)
    box(ax, 7.0, 7.6, 2.4, 1.0, "video\nfeature", fc=COL_VIDEO + "33", ec=COL_VIDEO)
    box(ax, 0.6, 5.8, 2.4, 1.0, "MLP proj\n(brain)", fc=COL_TRAIN, fontsize=6.5)
    box(ax, 7.0, 5.8, 2.4, 1.0, "MLP proj\n(video)", fc=COL_TRAIN, fontsize=6.5)
    arrow(ax, 1.8, 7.6, 1.8, 6.8); arrow(ax, 8.2, 7.6, 8.2, 6.8)
    ax.plot([3.0, 7.0], [6.3, 6.3], color=COL_LOSS, lw=1.0, linestyle="--")
    ax.text(5.0, 6.55, "InfoNCE", ha="center", fontsize=7, color=COL_LOSS, fontweight="bold")
    box(ax, 3.0, 3.2, 4.0, 1.0, "concat (or brain only)", fc=COL_TRAIN, fontsize=6.5)
    arrow(ax, 1.8, 5.8, 3.5, 4.2); arrow(ax, 8.2, 5.8, 6.5, 4.2)
    box(ax, 4.0, 1.7, 2.0, 0.9, "linear probe", fc=COL_FROZEN, ec=COL_OUT, fontsize=6.5)
    arrow(ax, 5.0, 3.2, 5.0, 2.6)
    box(ax, 4.0, 0.3, 2.0, 0.9, "", fc=COL_OUT)
    ax.text(5.0, 0.75, "V / A", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    arrow(ax, 5.0, 1.7, 5.0, 1.2)


def panel_D_late_fusion(ax):
    setup_panel(ax)
    draw_panel_title(ax, "D. Late linear fusion", "concat → logistic / ridge")
    box(ax, 0.6, 7.0, 2.4, 1.0, "brain\nfeature", fc=COL_BRAIN + "33", ec=COL_BRAIN)
    box(ax, 7.0, 7.0, 2.4, 1.0, "video\nfeature", fc=COL_VIDEO + "33", ec=COL_VIDEO)
    box(ax, 3.0, 4.6, 4.0, 1.0, "concat", fc=COL_FROZEN, ec=COL_OUT)
    arrow(ax, 1.8, 7.0, 3.5, 5.6); arrow(ax, 8.2, 7.0, 6.5, 5.6)
    box(ax, 3.0, 2.4, 4.0, 1.0, "logistic / ridge\n(closed form)", fc=COL_TRAIN, fontsize=6.5)
    arrow(ax, 5.0, 4.6, 5.0, 3.4)
    box(ax, 4.0, 0.3, 2.0, 0.9, "", fc=COL_OUT)
    ax.text(5.0, 0.75, "V / A", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    arrow(ax, 5.0, 2.4, 5.0, 1.2)


# ============================================================
# Brain-only paradigms (bottom row)
# ============================================================

def panel_I_supervised(ax):
    setup_panel(ax)
    draw_panel_title(ax, "I. Supervised MLP", "brain only → MLP → V/A")
    box(ax, 4.0, 7.4, 2.0, 1.0, "brain\nfeature", fc=COL_BRAIN + "33", ec=COL_BRAIN)
    box(ax, 3.5, 4.0, 3.0, 1.4, "2-layer MLP\n(GELU + dropout)", fc=COL_TRAIN, fontsize=7)
    arrow(ax, 5.0, 7.4, 5.0, 5.4)
    box(ax, 4.0, 2.0, 2.0, 1.0, "linear head", fc=COL_TRAIN)
    arrow(ax, 5.0, 4.0, 5.0, 3.0)
    box(ax, 4.0, 0.3, 2.0, 0.9, "", fc=COL_OUT)
    ax.text(5.0, 0.75, "V / A", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    arrow(ax, 5.0, 2.0, 5.0, 1.2)


def panel_II_distillation(ax):
    setup_panel(ax)
    draw_panel_title(ax, "II. Distillation", "video teacher → brain student (KL)")
    # teacher (video) on left
    box(ax, 0.4, 7.4, 2.4, 1.0, "video\nfeature", fc=COL_VIDEO + "33", ec=COL_VIDEO)
    box(ax, 0.4, 5.4, 2.4, 1.0, "TEACHER\nlinear", fc=COL_TEACH, fontsize=6.5)
    arrow(ax, 1.6, 7.4, 1.6, 6.4)
    box(ax, 0.4, 3.4, 2.4, 1.0, "soft labels", fc=COL_TEACH, ec=COL_OUT, fontsize=6.5)
    arrow(ax, 1.6, 5.4, 1.6, 4.4)
    # student (brain) on right
    box(ax, 6.6, 7.4, 2.4, 1.0, "brain\nfeature", fc=COL_BRAIN + "33", ec=COL_BRAIN)
    box(ax, 6.6, 5.4, 2.4, 1.4, "STUDENT\n2-layer MLP", fc=COL_TRAIN, fontsize=6.5)
    arrow(ax, 7.8, 7.4, 7.8, 6.8)
    box(ax, 6.6, 3.4, 2.4, 1.0, "student preds", fc=COL_TRAIN, fontsize=6.5)
    arrow(ax, 7.8, 5.4, 7.8, 4.4)
    # KL loss arrow
    ax.plot([2.8, 6.6], [3.9, 3.9], color=COL_LOSS, lw=1.0, linestyle="--")
    ax.text(4.7, 4.15, "KL (α=0.5,T=4)", ha="center", fontsize=6.5, color=COL_LOSS, fontweight="bold")
    box(ax, 4.0, 1.6, 2.0, 1.0, "CE / MSE\n(on V/A)", fc=COL_LOSS + "33", ec=COL_LOSS, fontsize=6.5)
    arrow(ax, 7.8, 3.4, 6.0, 2.1)
    box(ax, 4.0, 0.3, 2.0, 0.9, "", fc=COL_OUT)
    ax.text(5.0, 0.75, "V / A", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    arrow(ax, 5.0, 1.6, 5.0, 1.2)


def panel_III_multitask(ax):
    setup_panel(ax)
    draw_panel_title(ax, "III. Multitask", "brain → V/A + video recon (λ=0.3)")
    box(ax, 4.0, 7.6, 2.0, 1.0, "brain\nfeature", fc=COL_BRAIN + "33", ec=COL_BRAIN)
    box(ax, 3.5, 5.6, 3.0, 1.2, "shared MLP\nbackbone", fc=COL_TRAIN, fontsize=7)
    arrow(ax, 5.0, 7.6, 5.0, 6.8)
    # two heads
    box(ax, 0.8, 3.5, 2.6, 1.0, "V/A head", fc=COL_TRAIN)
    box(ax, 6.6, 3.5, 2.6, 1.0, "video-recon\nhead", fc=COL_TRAIN, fontsize=6.5)
    arrow(ax, 4.5, 5.6, 2.1, 4.5)
    arrow(ax, 5.5, 5.6, 7.9, 4.5)
    box(ax, 0.8, 1.8, 2.6, 1.0, "V / A", fc=COL_OUT)
    ax.text(2.1, 2.3, "V / A", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    arrow(ax, 2.1, 3.5, 2.1, 2.8)
    box(ax, 6.6, 1.8, 2.6, 1.0, "video pred", fc=COL_OUT)
    ax.text(7.9, 2.3, "video pred", ha="center", va="center", fontsize=7, color="white", fontweight="bold")
    arrow(ax, 7.9, 3.5, 7.9, 2.8)
    ax.text(7.9, 1.4, "vs CLIP feat (MSE)", ha="center", fontsize=6, color=COL_LOSS, style="italic")
    ax.text(2.1, 1.4, "vs target (CE/MSE)", ha="center", fontsize=6, color=COL_LOSS, style="italic")


def panel_IV_subject_aware(ax):
    setup_panel(ax)
    draw_panel_title(ax, "IV. Subject-aware", "brain ⊕ subject embedding → MLP")
    box(ax, 0.6, 7.4, 2.4, 1.0, "brain\nfeature", fc=COL_BRAIN + "33", ec=COL_BRAIN)
    box(ax, 7.0, 7.4, 2.4, 1.0, "subj_id\n∈ {1..5}", fc="#F0F0F0", ec=COL_OUT, fontsize=6.5)
    box(ax, 7.0, 5.6, 2.4, 1.0, "nn.Embedding\n(5, 16)", fc=COL_TRAIN, fontsize=6.5)
    arrow(ax, 8.2, 7.4, 8.2, 6.6)
    box(ax, 3.5, 4.0, 3.0, 1.0, "concat\n(brain, subj_emb)", fc=COL_FROZEN, ec=COL_OUT, fontsize=6.5)
    arrow(ax, 1.8, 7.4, 4.0, 5.0); arrow(ax, 8.2, 5.6, 6.0, 5.0)
    box(ax, 3.5, 2.0, 3.0, 1.2, "2-layer MLP", fc=COL_TRAIN)
    arrow(ax, 5.0, 4.0, 5.0, 3.2)
    box(ax, 4.0, 0.3, 2.0, 0.9, "", fc=COL_OUT)
    ax.text(5.0, 0.75, "V / A", ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    arrow(ax, 5.0, 2.0, 5.0, 1.2)


# ============================================================
# Compose
# ============================================================

def main():
    fig, axes = plt.subplots(2, 4, figsize=(15.5, 8.0))

    # Top row: joint paradigms
    panel_A_token_attention(axes[0, 0])
    panel_B_cross_attention(axes[0, 1])
    panel_C_contrastive(axes[0, 2])
    panel_D_late_fusion(axes[0, 3])

    # Bottom row: brain-only paradigms
    panel_I_supervised(axes[1, 0])
    panel_II_distillation(axes[1, 1])
    panel_III_multitask(axes[1, 2])
    panel_IV_subject_aware(axes[1, 3])

    # Row labels on the left
    fig.text(0.005, 0.74, "JOINT\n(brain + video)", ha="left", va="center",
             fontsize=10, fontweight="bold", color="#3182BD", rotation=90)
    fig.text(0.005, 0.28, "BRAIN-ONLY\n(brain only at inference)", ha="left", va="center",
             fontsize=10, fontweight="bold", color="#E6550D", rotation=90)

    # Legend at bottom
    legend_handles = [
        mpatches.Patch(facecolor=COL_BRAIN + "33", edgecolor=COL_BRAIN, label="brain input (Brain-JEPA frozen)"),
        mpatches.Patch(facecolor=COL_VIDEO + "33", edgecolor=COL_VIDEO, label="video input (CLIP frozen)"),
        mpatches.Patch(facecolor=COL_TRAIN, edgecolor=COL_OUT, label="trainable module"),
        mpatches.Patch(facecolor=COL_FROZEN, edgecolor=COL_OUT, label="non-learned (concat / probe)"),
        mpatches.Patch(facecolor=COL_TEACH, edgecolor=COL_OUT, label="teacher model (II)"),
        mpatches.Patch(facecolor=COL_OUT, edgecolor=COL_OUT, label="output (V/A scores)"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=6, fontsize=7.5,
               frameon=False, bbox_to_anchor=(0.5, -0.01))

    plt.subplots_adjust(left=0.03, right=0.99, top=0.97, bottom=0.07, wspace=0.05, hspace=0.18)
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    print(f"wrote {OUT}")
    plt.close(fig)


if __name__ == "__main__":
    main()
