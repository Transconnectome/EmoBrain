"""
Two single-column figures for CCN 2026 camera-ready.

Figure 1 (left column): subspace identification
  (A) R^2 per V-JEPA2 PC predicted from Brain-JEPA, PC1-3 marked
  (B) Mean max |r| with 34 emotion categories, brain-aligned vs unaligned

Figure 2 (right column): categorical structure
  (A) Decoding R^2 across 34 categories from brain-aligned subspace
  (B) Category/V-A ratio, brain-aligned subspace vs full V-JEPA2
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams

ROOT     = '/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn'
DATA     = os.path.join(ROOT, 'study1', 'data')
FIGREC   = os.path.join(ROOT, 'study1', 'results', 'figures')
TEMPLATE = os.path.join(ROOT, 'ccn2026_template')
os.makedirs(FIGREC, exist_ok=True)

import matplotlib.font_manager as fm
available = [f.name for f in fm.fontManager.ttflist]
if 'Helvetica' in available:    FONT = 'Helvetica'
elif 'Arial' in available:      FONT = 'Arial'
elif 'Liberation Sans' in available: FONT = 'Liberation Sans'
else: FONT = 'DejaVu Sans'

rcParams['font.family'] = FONT
rcParams['font.size'] = 7
rcParams['axes.titlesize'] = 8
rcParams['axes.labelsize'] = 7
rcParams['xtick.labelsize'] = 6
rcParams['ytick.labelsize'] = 6
rcParams['legend.fontsize'] = 5.5
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

SINGLE_COL_WIDTH = 3.3  # inches; CCN single column ~3.4"

# ============================================================================
#  FIGURE 1 (left column): subspace identification
# ============================================================================
fig1 = plt.figure(figsize=(SINGLE_COL_WIDTH, 3.4))
gs1 = fig1.add_gridspec(2, 1, height_ratios=[1, 1], hspace=0.85)

# A: R^2 per PC
axA = fig1.add_subplot(gs1[0])
n_show = 40
colors = [C_ALN if mask_vjepa[i] else C_UNALN for i in range(n_show)]
x = np.arange(1, n_show + 1)
axA.bar(x, r2_vjepa[:n_show], color=colors, width=0.85, linewidth=0, zorder=2)
for i in [0, 1, 2]:
    axA.text(i + 1, r2_vjepa[i] + 0.008, '*', ha='center', va='bottom',
             fontsize=8, color=C_ALN, fontweight='bold')
axA.set_xlabel('V-JEPA2 PC index', labelpad=2)
axA.set_ylabel('R² by Brain-JEPA', labelpad=3)
axA.set_xlim(0.3, n_show + 0.7)
axA.set_xticks([1, 2, 3, 10, 20, 30, 40])
axA.set_ylim(0, 0.44)
axA.spines['top'].set_visible(False); axA.spines['right'].set_visible(False)
legend_A = [
    mpatches.Patch(facecolor=C_ALN,   label='Brain-aligned (n=3)'),
    mpatches.Patch(facecolor=C_UNALN, label='Brain-unaligned (n=97)'),
    plt.Line2D([0], [0], color='none', label='* p<0.001 (perm., FDR)'),
]
axA.legend(handles=legend_A, loc='upper right', frameon=False,
           handlelength=0.9, handletextpad=0.3)
axA.text(-0.15, 1.08, 'A', transform=axA.transAxes,
         fontsize=10, fontweight='bold', va='top')

# B: mean max|r|
axB = fig1.add_subplot(gs1[1])
pred_vals   = max_r_per_pc[mask_vjepa == 1]
unpred_vals = max_r_per_pc[mask_vjepa == 0]
bar_means = [pred_vals.mean(), unpred_vals.mean()]
axB.bar([0, 1], bar_means, color=[C_ALN, C_UNALN], width=0.5, linewidth=0, zorder=2)
np.random.seed(42)
axB.scatter(np.zeros(len(pred_vals))   + np.random.uniform(-0.10, 0.10, len(pred_vals)),
            pred_vals,   s=12, color='white', edgecolors=C_ALN, linewidth=0.7, zorder=4)
axB.scatter(np.ones(len(unpred_vals))  + np.random.uniform(-0.10, 0.10, len(unpred_vals)),
            unpred_vals, s=2,  color='white', edgecolors=C_UNALN, linewidth=0.5, zorder=4, alpha=0.6)
axB.set_xticks([0, 1])
axB.set_xticklabels(['Brain-aligned', 'Brain-unaligned'], fontsize=7)
axB.set_ylabel('Mean max |r|\nwith 34 emotion cats.', labelpad=3)
axB.set_ylim(0, 0.44)
axB.spines['top'].set_visible(False); axB.spines['right'].set_visible(False)
axB.text(-0.15, 1.08, 'B', transform=axB.transAxes,
         fontsize=10, fontweight='bold', va='top')

for d in (FIGREC, TEMPLATE):
    fig1.savefig(os.path.join(d, 'figure1_ccn.pdf'), bbox_inches='tight', facecolor='white')
fig1.savefig(os.path.join(FIGREC, 'figure1_ccn.png'), dpi=300, bbox_inches='tight', facecolor='white')
print("Figure 1 saved.")

# ============================================================================
#  FIGURE 2 (right column): categorical structure
# ============================================================================
fig2 = plt.figure(figsize=(SINGLE_COL_WIDTH, 3.4))
gs2 = fig2.add_gridspec(2, 1, height_ratios=[1, 1], hspace=1.3)

# A: 34-cat + V/A decoding bar
axC = fig2.add_subplot(gs2[0])
emo_r2 = r2_pred_17[:34]
av_r2  = r2_pred_17[34:]
av_names = list(d_17['dim_labels'])
sort_idx = np.argsort(emo_r2)[::-1]
emo_sorted = [emo_labels[i] for i in sort_idx]
r2_sorted  = emo_r2[sort_idx]
x_emo = np.arange(34)
x_av  = np.array([35.5, 36.5])
axC.bar(x_emo, r2_sorted, color=C_EMO, width=0.82, linewidth=0, zorder=2)
axC.bar(x_av,  av_r2,     color=C_DIM, width=0.82, linewidth=0, zorder=2)
axC.axhline(y=emo_r2.mean(), color=C_EMO, linewidth=0.8, linestyle='--', alpha=0.7, zorder=3)
axC.axhline(y=av_r2.mean(),  color=C_DIM, linewidth=0.8, linestyle='--', alpha=0.7, zorder=3)
axC.set_xticks(list(x_emo) + list(x_av))
axC.set_xticklabels(emo_sorted + av_names, rotation=90, fontsize=3.8, ha='center')
axC.set_ylabel('Decoding R² (brain-\naligned subspace → target)', labelpad=3)
axC.set_xlim(-0.8, 38.0)
axC.set_ylim(0, 0.38)
axC.spines['top'].set_visible(False); axC.spines['right'].set_visible(False)
legend_C = [
    mpatches.Patch(facecolor=C_EMO, label=f'Cats (n=34, R²={emo_r2.mean():.3f})'),
    mpatches.Patch(facecolor=C_DIM, label=f'Val, Aro (R²={av_r2.mean():.3f})'),
]
axC.legend(handles=legend_C, loc='upper right', frameon=False,
           handlelength=0.9, handletextpad=0.3, fontsize=5)
axC.text(-0.15, 1.08, 'A', transform=axC.transAxes,
         fontsize=10, fontweight='bold', va='top')

# B: cat/V-A ratio
axD = fig2.add_subplot(gs2[1])
axD.bar([0, 1], [ratio_pred, ratio_full], color=[C_ALN, C_FULL],
        width=0.5, linewidth=0, zorder=2)
axD.axhline(y=1.0, color='black', linewidth=0.75, linestyle=':', zorder=3)
axD.text(1.32, 1.04, 'equal', fontsize=5, color='black', va='bottom')
axD.set_xticks([0, 1])
axD.set_xticklabels(['Brain-aligned\nsubspace', 'Full V-JEPA2\n(100 PCs)'], fontsize=7)
axD.set_ylabel('Category / V-A ratio', labelpad=3)
axD.set_ylim(0, 3.2)
axD.spines['top'].set_visible(False); axD.spines['right'].set_visible(False)
axD.text(0, ratio_pred + 0.10, f'{ratio_pred:.2f}', ha='center',
         fontsize=7, color=C_ALN, fontweight='bold')
axD.text(1, ratio_full + 0.10, f'{ratio_full:.2f}', ha='center',
         fontsize=7, color='#4A4A4A')
axD.text(-0.15, 1.08, 'B', transform=axD.transAxes,
         fontsize=10, fontweight='bold', va='top')

for d in (FIGREC, TEMPLATE):
    fig2.savefig(os.path.join(d, 'figure2_ccn.pdf'), bbox_inches='tight', facecolor='white')
fig2.savefig(os.path.join(FIGREC, 'figure2_ccn.png'), dpi=300, bbox_inches='tight', facecolor='white')
print("Figure 2 saved.")
