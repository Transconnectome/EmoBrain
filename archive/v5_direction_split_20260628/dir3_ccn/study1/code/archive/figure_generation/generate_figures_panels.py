"""
Per-panel figure generation for CCN 2026 camera-ready.

Each panel saved as a SEPARATE PDF and PNG so the user can place them
independently in the .tex (subfigure or freeform includegraphics).

Outputs (in ccn2026_template/):
  panel_A_pcscree.pdf / .png      - R^2 per V-JEPA2 PC scree
  panel_B_maxr.pdf   / .png       - max |r| bar (brain-aligned vs unaligned)
  panel_C_decoding.pdf / .png     - 34-cat + V/A decoding bar
  panel_D_ratio.pdf  / .png       - Category/V-A ratio bar
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams

ROOT     = '/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn'
DATA     = os.path.join(ROOT, 'study1', 'data')
FIGREC   = os.path.join(ROOT, 'study1', 'results', 'figures')
TEMPLATE = os.path.join(ROOT, 'ccn2026_template')
os.makedirs(FIGREC, exist_ok=True)

import matplotlib.font_manager as fm
available = [f.name for f in fm.fontManager.ttflist]
FONT = ('Helvetica' if 'Helvetica' in available else
        'Arial' if 'Arial' in available else
        'Liberation Sans' if 'Liberation Sans' in available else
        'DejaVu Sans')

rcParams['font.family'] = FONT
rcParams['font.size'] = 8
rcParams['axes.titlesize'] = 9
rcParams['axes.labelsize'] = 8
rcParams['xtick.labelsize'] = 7
rcParams['ytick.labelsize'] = 7
rcParams['legend.fontsize'] = 6.5
rcParams['axes.linewidth'] = 0.75
rcParams['xtick.major.width'] = 0.75
rcParams['ytick.major.width'] = 0.75
rcParams['xtick.major.size'] = 2.5
rcParams['ytick.major.size'] = 2.5
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42

C_ALN   = '#2166AC'
C_UNALN = '#B2B2B2'
C_EMO   = '#2166AC'
C_DIM   = '#D6604D'
C_FULL  = '#92C5DE'

d_pc  = np.load(os.path.join(DATA, 'brain_predictable_dims.npz'),        allow_pickle=True)
d_cor = np.load(os.path.join(DATA, 'pc_emotion_correlation.npz'),        allow_pickle=True)
d_17  = np.load(os.path.join(DATA, 'exp17_av2d_results.npz'),            allow_pickle=True)

r2_vjepa   = d_pc['r2_vjepa_per_dim']
mask_vjepa = d_cor['brain_pred_mask_vjepa']
corr_emo   = d_cor['corr_vjepa_emo']
emo_labels = d_cor['emotion_labels']
r2_pred_17 = d_17['r2_pred_vjepa']
r2_all_17  = d_17['r2_all_vjepa']
max_r_per_pc = np.max(np.abs(corr_emo), axis=1)

mean_cat_pred = r2_pred_17[:34].mean()
mean_av_pred  = r2_pred_17[34:].mean()
ratio_pred    = mean_cat_pred / mean_av_pred
mean_cat_full = r2_all_17[:34].mean()
mean_av_full  = r2_all_17[34:].mean()
ratio_full    = mean_cat_full / mean_av_full


def save(fig, name):
    for d in (FIGREC, TEMPLATE):
        fig.savefig(os.path.join(d, name + '.pdf'), bbox_inches='tight', facecolor='white')
    fig.savefig(os.path.join(FIGREC, name + '.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"saved: {name}")

# Unified figsize for all panels so LaTeX scaling preserves label sizes
FIGSIZE_WIDE   = (3.5, 2.3)   # for panels A and C (wide content)
FIGSIZE_SQUARE = (3.5, 2.3)   # for panels B and D (compact content) — same width

# ============================================================================
#  Panel A: PC scree (R^2 per V-JEPA2 PC predicted from Brain-JEPA)
# ============================================================================
fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
n_show = 40
colors = [C_ALN if mask_vjepa[i] else C_UNALN for i in range(n_show)]
x = np.arange(1, n_show + 1)
ax.bar(x, r2_vjepa[:n_show], color=colors, width=0.85, linewidth=0, zorder=2)
for i in [0, 1, 2]:
    ax.text(i + 1, r2_vjepa[i] + 0.008, '*', ha='center', va='bottom',
            fontsize=9, color=C_ALN, fontweight='bold')
ax.set_xlabel('V-JEPA2 PC index', labelpad=2)
ax.set_ylabel('R² predicted\nby Brain-JEPA', labelpad=3)
ax.set_xlim(0.3, n_show + 0.7)
ax.set_xticks([1, 2, 3, 10, 20, 30, 40])
ax.set_ylim(0, 0.44)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.legend(handles=[
    mpatches.Patch(facecolor=C_ALN,   label='Brain-aligned (n=3)'),
    mpatches.Patch(facecolor=C_UNALN, label='Brain-unaligned (n=97)'),
    plt.Line2D([0], [0], color='none', label='* p<0.001 (perm., FDR)'),
], loc='upper right', frameon=False, handlelength=1.0, handletextpad=0.4)
ax.text(-0.16, 1.10, '(A)', transform=ax.transAxes,
        fontsize=11, fontweight='bold', va='top')
save(fig, 'panel_A_pcscree')

# ============================================================================
#  Panel B: max |r| bar (brain-aligned vs unaligned)
# ============================================================================
fig, ax = plt.subplots(figsize=FIGSIZE_SQUARE)
pred_vals   = max_r_per_pc[mask_vjepa == 1]
unpred_vals = max_r_per_pc[mask_vjepa == 0]
ax.bar([0, 1], [pred_vals.mean(), unpred_vals.mean()],
       color=[C_ALN, C_UNALN], width=0.55, linewidth=0, zorder=2)
np.random.seed(42)
ax.scatter(np.zeros(len(pred_vals))  + np.random.uniform(-0.10, 0.10, len(pred_vals)),
           pred_vals,   s=14, color='white', edgecolors=C_ALN, linewidth=0.7, zorder=4)
ax.scatter(np.ones(len(unpred_vals)) + np.random.uniform(-0.10, 0.10, len(unpred_vals)),
           unpred_vals, s=3,  color='white', edgecolors=C_UNALN, linewidth=0.5, zorder=4, alpha=0.6)
ax.set_xticks([0, 1])
ax.set_xticklabels(['Brain-\naligned', 'Brain-\nunaligned'], fontsize=7)
ax.set_ylabel('Mean max |r|\nwith 34 emotion cats.', labelpad=3)
ax.set_ylim(0, 0.44)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(-0.28, 1.10, '(B)', transform=ax.transAxes,
        fontsize=11, fontweight='bold', va='top')
save(fig, 'panel_B_maxr')

# ============================================================================
#  Panel C: 34-cat + V/A decoding bar
# ============================================================================
fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
emo_r2 = r2_pred_17[:34]
av_r2  = r2_pred_17[34:]
av_names = list(d_17['dim_labels'])
sort_idx = np.argsort(emo_r2)[::-1]
emo_sorted = [emo_labels[i] for i in sort_idx]
r2_sorted  = emo_r2[sort_idx]
x_emo = np.arange(34)
x_av  = np.array([35.5, 36.5])
ax.bar(x_emo, r2_sorted, color=C_EMO, width=0.82, linewidth=0, zorder=2)
ax.bar(x_av,  av_r2,     color=C_DIM, width=0.82, linewidth=0, zorder=2)
ax.axhline(y=emo_r2.mean(), color=C_EMO, linewidth=0.8, linestyle='--', alpha=0.7, zorder=3)
ax.axhline(y=av_r2.mean(),  color=C_DIM, linewidth=0.8, linestyle='--', alpha=0.7, zorder=3)
ax.set_xticks(list(x_emo) + list(x_av))
ax.set_xticklabels(emo_sorted + av_names, rotation=90, fontsize=5.2, ha='center')
ax.set_ylabel('Decoding R²\n(brain-aligned subspace → target)', labelpad=3)
ax.set_xlim(-0.8, 38.0)
ax.set_ylim(0, 0.38)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.legend(handles=[
    mpatches.Patch(facecolor=C_EMO, label=f'Emotion categories (n=34, R²={emo_r2.mean():.3f})'),
    mpatches.Patch(facecolor=C_DIM, label=f'Valence, Arousal (R²={av_r2.mean():.3f})'),
], loc='upper right', frameon=False, handlelength=1.0, handletextpad=0.4, fontsize=6)
ax.text(-0.22, 1.08, '(A)', transform=ax.transAxes,
        fontsize=11, fontweight='bold', va='top')
save(fig, 'panel_C_decoding')

# ============================================================================
#  Panel D: cat/V-A ratio
# ============================================================================
fig, ax = plt.subplots(figsize=FIGSIZE_SQUARE)
ax.bar([0, 1], [ratio_pred, ratio_full], color=[C_ALN, C_FULL],
       width=0.55, linewidth=0, zorder=2)
ax.axhline(y=1.0, color='black', linewidth=0.75, linestyle=':', zorder=3)
ax.text(1.32, 1.04, 'equal', fontsize=6, color='black', va='bottom')
ax.set_xticks([0, 1])
ax.set_xticklabels(['Brain-aligned\nsubspace', 'Full V-JEPA2\n(100 PCs)'], fontsize=7)
ax.set_ylabel('Category / V-A ratio', labelpad=3)
ax.set_ylim(0, 3.2)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(0, ratio_pred + 0.10, f'{ratio_pred:.2f}', ha='center',
        fontsize=8, color=C_ALN, fontweight='bold')
ax.text(1, ratio_full + 0.10, f'{ratio_full:.2f}', ha='center',
        fontsize=8, color='#4A4A4A')
ax.text(-0.28, 1.08, '(B)', transform=ax.transAxes,
        fontsize=11, fontweight='bold', va='top')
save(fig, 'panel_D_ratio')

print("All 4 panels saved as separate PDFs and PNGs.")
