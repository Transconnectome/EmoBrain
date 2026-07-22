"""
CCN 2026 Figure Generation — Nature style, Helvetica font
Figure 1: Brain-predictable subspace identification
Figure 2: Affective structure of brain-predictable subspace
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams

# ─── Font setup ────────────────────────────────────────────────────────────────
# Try Helvetica; fall back to DejaVu Sans if unavailable
import matplotlib.font_manager as fm
available = [f.name for f in fm.fontManager.ttflist]
if 'Helvetica' in available:
    FONT = 'Helvetica'
elif 'Arial' in available:
    FONT = 'Arial'
elif 'Liberation Sans' in available:
    FONT = 'Liberation Sans'   # metrically equivalent to Arial/Helvetica
else:
    FONT = 'DejaVu Sans'
print(f"Using font: {FONT}")

rcParams['font.family'] = FONT
rcParams['font.size'] = 7
rcParams['axes.titlesize'] = 8
rcParams['axes.labelsize'] = 7
rcParams['xtick.labelsize'] = 6
rcParams['ytick.labelsize'] = 6
rcParams['legend.fontsize'] = 6
rcParams['axes.linewidth'] = 0.75
rcParams['xtick.major.width'] = 0.75
rcParams['ytick.major.width'] = 0.75
rcParams['xtick.major.size'] = 2.5
rcParams['ytick.major.size'] = 2.5
rcParams['pdf.fonttype'] = 42
rcParams['ps.fonttype'] = 42

# ─── Colors ────────────────────────────────────────────────────────────────────
C_PRED   = '#2166AC'   # blue  — brain-predictable
C_UNPRED = '#B2B2B2'   # gray  — brain-unpredictable
C_EMO    = '#2166AC'   # blue  — emotion categories
C_DIM    = '#D6604D'   # red   — affective dimensions
C_FULL   = '#92C5DE'   # light blue — full space

# ─── Load data ─────────────────────────────────────────────────────────────────
d_pc  = np.load('results/brain_predictable_dims.npz',     allow_pickle=True)
d_cor = np.load('results/pc_emotion_correlation.npz',     allow_pickle=True)
d_17  = np.load('results/exp17_av2d_results.npz',         allow_pickle=True)
d_18  = np.load('results/exp18_subjectwise_claim_check.npz', allow_pickle=True)

r2_vjepa   = d_pc['r2_vjepa_per_dim']          # (100,) R² per PC from brain
mask_vjepa = d_cor['brain_pred_mask_vjepa']     # (100,) binary

corr_emo   = d_cor['corr_vjepa_emo']            # (100, 34)
emo_labels = d_cor['emotion_labels']            # (34,)

r2_pred_17 = d_17['r2_pred_vjepa']             # (36,)  34 emo + AV
r2_all_17  = d_17['r2_all_vjepa']              # (36,)

r2_subj    = d_18['r2_2d_vjepa']               # (6, 36) row0=mean, rows1-5=subjects

# Per-PC max|r|
max_r_per_pc = np.max(np.abs(corr_emo), axis=1)  # (100,)

# Subject-wise cat/AV ratios (brain-pred)
subj_ratios_pred = []
for i in range(1, 6):
    cat = r2_subj[i, :34].mean()
    av  = r2_subj[i, 34:].mean()
    subj_ratios_pred.append(cat / max(av, 1e-10))
subj_ratios_pred = np.array(subj_ratios_pred)

mean_cat_pred = r2_pred_17[:34].mean()
mean_av_pred  = r2_pred_17[34:].mean()
ratio_pred    = mean_cat_pred / mean_av_pred      # 1.441

mean_cat_full = r2_all_17[:34].mean()
mean_av_full  = r2_all_17[34:].mean()
ratio_full    = mean_cat_full / mean_av_full      # 1.258

print(f"Brain-pred ratio: {ratio_pred:.3f}")
print(f"Full space ratio: {ratio_full:.3f}")
print(f"Per-subject ratios (pred): {subj_ratios_pred}")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1
# ═══════════════════════════════════════════════════════════════════════════════
# Nature double-column: 183mm ≈ 7.2in, height ~3in
fig1, axes1 = plt.subplots(1, 2, figsize=(7.2, 2.5),
                            gridspec_kw={'width_ratios': [3, 1.2],
                                         'wspace': 0.38})

# ── Figure 1A: R² per PC ────────────────────────────────────────────────────
ax = axes1[0]
n_show = 40
colors = [C_PRED if mask_vjepa[i] else C_UNPRED for i in range(n_show)]
x = np.arange(1, n_show + 1)

bars = ax.bar(x, r2_vjepa[:n_show], color=colors, width=0.85, linewidth=0, zorder=2)

# Significance marker on PC1-3
for i in [0, 1, 2]:
    ax.text(i + 1, r2_vjepa[i] + 0.008, '*', ha='center', va='bottom',
            fontsize=8, color=C_PRED, fontweight='bold')

ax.set_xlabel('V-JEPA2 PC index', labelpad=3)
ax.set_ylabel('Variance explained\nby Brain-JEPA (R²)', labelpad=3)
ax.set_xlim(0.3, n_show + 0.7)
ax.set_xticks([1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40])
ax.set_ylim(0, 0.44)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

legend_elements = [
    mpatches.Patch(facecolor=C_PRED,   label='Brain-predictable (n=3)'),
    mpatches.Patch(facecolor=C_UNPRED, label='Brain-unpredictable (n=97)'),
    plt.Line2D([0], [0], color='none', label='* p < 0.001 (permutation, FDR)'),
]
ax.legend(handles=legend_elements, loc='upper right', frameon=False,
          handlelength=1.2, handletextpad=0.4)
ax.text(-0.08, 1.05, 'A', transform=ax.transAxes,
        fontsize=9, fontweight='bold', va='top')

# ── Figure 1B: mean max|r| ──────────────────────────────────────────────────
ax = axes1[1]

pred_vals   = max_r_per_pc[mask_vjepa == 1]   # (3,)
unpred_vals = max_r_per_pc[mask_vjepa == 0]   # (97,)

bar_means = [pred_vals.mean(), unpred_vals.mean()]
bar_x     = [0, 1]
bar_cols  = [C_PRED, C_UNPRED]
bar_labs  = ['Brain-\npredictable', 'Brain-\nunpredictable']

ax.bar(bar_x, bar_means, color=bar_cols, width=0.5, linewidth=0, zorder=2)

# Scatter individual PCs
np.random.seed(42)
jitter_pred   = np.random.uniform(-0.10, 0.10, size=len(pred_vals))
jitter_unpred = np.random.uniform(-0.10, 0.10, size=len(unpred_vals))

ax.scatter(0 + jitter_pred,   pred_vals,   s=10, color='white',
           edgecolors=C_PRED,   linewidth=0.7, zorder=4)
ax.scatter(1 + jitter_unpred, unpred_vals, s=2,  color='white',
           edgecolors=C_UNPRED, linewidth=0.5, zorder=4, alpha=0.6)

ax.set_xticks([0, 1])
ax.set_xticklabels(bar_labs, fontsize=6)
ax.set_ylabel('Mean max |r| with\n34 emotion categories', labelpad=3)
ax.set_ylim(0, 0.44)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.20, 1.05, 'B', transform=ax.transAxes,
        fontsize=9, fontweight='bold', va='top')

fig1.savefig('figures/figure1_ccn.png', dpi=300, bbox_inches='tight',
             facecolor='white')
fig1.savefig('figures/figure1_ccn.pdf', bbox_inches='tight', facecolor='white')
print("Figure 1 saved.")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2
# ═══════════════════════════════════════════════════════════════════════════════
fig2, axes2 = plt.subplots(1, 2, figsize=(7.2, 2.8),
                            gridspec_kw={'width_ratios': [3.2, 1.0],
                                         'wspace': 0.40})

# ── Figure 2A: Emotion decoding R² ──────────────────────────────────────────
ax = axes2[0]

emo_r2 = r2_pred_17[:34]
av_r2  = r2_pred_17[34:]   # [Arousal, Valence]
av_names = list(d_17['dim_labels'])  # ['Arousal', 'Valence']

# Sort emotions by R² descending
sort_idx  = np.argsort(emo_r2)[::-1]
emo_sorted = [emo_labels[i] for i in sort_idx]
r2_sorted  = emo_r2[sort_idx]

# x positions: 34 emotions + gap + 2 AV dims
x_emo = np.arange(34)
x_av  = np.array([35.5, 36.5])

ax.bar(x_emo, r2_sorted, color=C_EMO, width=0.82, linewidth=0, zorder=2)
ax.bar(x_av,  av_r2,     color=C_DIM, width=0.82, linewidth=0, zorder=2)

# Mean lines
ax.axhline(y=emo_r2.mean(), color=C_EMO, linewidth=0.8, linestyle='--',
           alpha=0.7, zorder=3)
ax.axhline(y=av_r2.mean(),  color=C_DIM, linewidth=0.8, linestyle='--',
           alpha=0.7, zorder=3)

# Labels on x-axis
all_names = emo_sorted + ['', '', 'Arousal', 'Valence']
all_x     = list(x_emo) + [34.5, 35.5, 36.5, 37.5]
# Simpler: just label the 34 emotions + 2 AV at correct x
tick_x    = list(x_emo) + list(x_av)
tick_lab  = emo_sorted + av_names

ax.set_xticks(tick_x)
ax.set_xticklabels(tick_lab, rotation=90, fontsize=4.8, ha='center')

# Keep all x-axis labels black (Arousal/Valence same as emotion labels)
ax.set_ylabel('Decoding R²\n(brain-pred subspace → target)', labelpad=3)
ax.set_xlim(-0.8, 38.0)
ax.set_ylim(0, 0.38)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

legend_elements2 = [
    mpatches.Patch(facecolor=C_EMO, label=f'Emotion categories (n=34, mean R²={emo_r2.mean():.3f})'),
    mpatches.Patch(facecolor=C_DIM, label=f'Valence, Arousal (mean R²={av_r2.mean():.3f})'),
]
ax.legend(handles=legend_elements2, loc='upper right', frameon=False,
          handlelength=1.0, handletextpad=0.4)
ax.text(-0.06, 1.05, 'A', transform=ax.transAxes,
        fontsize=9, fontweight='bold', va='top')

# ── Figure 2B: Category/A-V ratio ───────────────────────────────────────────
ax = axes2[1]

bar_x2   = [0, 1]
ratios   = [ratio_pred, ratio_full]
bar_cols2 = [C_PRED, C_FULL]
bar_labs2 = ['Brain-pred\nsubspace', 'Full V-JEPA2\n(100 PCs)']

ax.bar(bar_x2, ratios, color=bar_cols2, width=0.5, linewidth=0, zorder=2)

# Reference line at 1.0 (equal category and dimension)
ax.axhline(y=1.0, color='black', linewidth=0.75, linestyle=':', zorder=3)
ax.text(1.35, 1.02, 'equal', fontsize=5, color='black', va='bottom')

ax.set_xticks([0, 1])
ax.set_xticklabels(bar_labs2, fontsize=6)
ax.set_ylabel('Category / V-A ratio\n(mean R²$_{cat}$ / mean R²$_{V-A}$)', labelpad=3)
ax.set_ylim(0, 3.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.22, 1.05, 'B', transform=ax.transAxes,
        fontsize=9, fontweight='bold', va='top')

# Annotate ratio values
ax.text(0, ratio_pred + 0.08, f'{ratio_pred:.2f}', ha='center',
        fontsize=6, color=C_PRED, fontweight='bold')
ax.text(1, ratio_full + 0.08, f'{ratio_full:.2f}', ha='center',
        fontsize=6, color='#4A4A4A')


fig2.savefig('figures/figure2_ccn.png', dpi=300, bbox_inches='tight',
             facecolor='white')
fig2.savefig('figures/figure2_ccn.pdf', bbox_inches='tight', facecolor='white')
print("Figure 2 saved.")
print("Done.")
