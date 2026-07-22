"""
Generate all main figures for the research storyline.
Saves to /pscratch/sd/s/sjmoon/EmoFM/main/figures/

Figure 1: Brain-predictable subspace (PCA+Ridge)
  A: R² per V-JEPA2 PC
  B: Mean max|r| with emotions (brain-pred vs unpred)

Figure 2: Categorical organization of brain-predictable subspace
  A: 34 emotion decoding R² (sorted) + Arousal/Valence
  B: Category/V-A ratio (brain-pred vs full space)

Figure 3: CCA — Brain-Video shared space
  A: Canonical correlations (CC1-30)
  B: CC emotion profiles (top 5 CCs × top emotions)

Figure 4: Method comparison
  A: Decoding R² comparison across methods
  B: Cat/VA ratio comparison
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
from pathlib import Path

# ── Font setup ────────────────────────────────────────────────────────────────
import matplotlib.font_manager as fm
available = [f.name for f in fm.fontManager.ttflist]
if 'Helvetica' in available:
    FONT = 'Helvetica'
elif 'Arial' in available:
    FONT = 'Arial'
elif 'Liberation Sans' in available:
    FONT = 'Liberation Sans'
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

# ── Colors ────────────────────────────────────────────────────────────────────
C_PRED   = '#2166AC'   # blue
C_UNPRED = '#B2B2B2'   # gray
C_EMO    = '#2166AC'   # blue
C_DIM    = '#D6604D'   # red/orange
C_FULL   = '#92C5DE'   # light blue
C_CCA    = '#4DAF4A'   # green (CCA)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
RES  = BASE / "CCN2026/results"
OUT  = BASE / "main/figures"
OUT.mkdir(parents=True, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────
d_pc   = np.load(RES / 'brain_predictable_dims.npz', allow_pickle=True)
d_cor  = np.load(RES / 'pc_emotion_correlation.npz', allow_pickle=True)
d_17   = np.load(RES / 'exp17_av2d_results.npz', allow_pickle=True)
d_cca  = np.load(RES / 'cca_brain_video_results.npz', allow_pickle=True)

r2_vjepa   = d_pc['r2_vjepa_per_dim']
mask_vjepa = (d_cor['brain_pred_mask_vjepa'] == 1)
# Override: use permutation-based mask (PC1-3 only, exclude PC4 artifact)
mask_vjepa = np.zeros(100, dtype=bool)
mask_vjepa[:3] = True

corr_emo   = d_cor['corr_vjepa_emo']
emo_labels = list(d_cor['emotion_labels'])

r2_pred = d_17['r2_pred_vjepa']
r2_all  = d_17['r2_all_vjepa']

cc_r       = d_cca['cc_r']
sig_mask   = d_cca['sig_mask']
corr_cc    = d_cca['corr_cc_emo']
corr_cc_av = d_cca['corr_cc_av']
max_r_cc   = d_cca['max_r_per_cc']
r2_cca_sig = d_cca['r2_cca_sig']
r2_pca3    = d_cca['r2_pca_3']
r2_pca10   = d_cca['r2_pca_10']
r2_pca100  = d_cca['r2_pca_100']
cc_subj    = d_cca['cc_r_per_subj']

max_r_per_pc = np.max(np.abs(corr_emo), axis=1)

print("Data loaded.")

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Brain-Predictable Subspace (PCA+Ridge)
# ═════════════════════════════════════════════════════════════════════════════
fig1, axes1 = plt.subplots(1, 2, figsize=(7.2, 2.5),
                            gridspec_kw={'width_ratios': [3, 1.2], 'wspace': 0.38})

# ── 1A: R² per PC ──
ax = axes1[0]
n_show = 40
colors = [C_PRED if mask_vjepa[i] else C_UNPRED for i in range(n_show)]
x = np.arange(1, n_show + 1)
ax.bar(x, r2_vjepa[:n_show], color=colors, width=0.85, linewidth=0, zorder=2)

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
    mpatches.Patch(facecolor=C_PRED, label='Brain-predictable (n=3)'),
    mpatches.Patch(facecolor=C_UNPRED, label='Brain-unpredictable (n=97)'),
    plt.Line2D([0], [0], color='none', label='* p < 0.001 (permutation, FDR)'),
]
ax.legend(handles=legend_elements, loc='upper right', frameon=False,
          handlelength=1.2, handletextpad=0.4)
ax.text(-0.08, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# ── 1B: mean max|r| ──
ax = axes1[1]
pred_vals   = max_r_per_pc[mask_vjepa]
unpred_vals = max_r_per_pc[~mask_vjepa]

bar_means = [pred_vals.mean(), unpred_vals.mean()]
ax.bar([0, 1], bar_means, color=[C_PRED, C_UNPRED], width=0.5, linewidth=0, zorder=2)

np.random.seed(42)
ax.scatter(0 + np.random.uniform(-0.10, 0.10, len(pred_vals)), pred_vals,
           s=10, color='white', edgecolors=C_PRED, linewidth=0.7, zorder=4)
ax.scatter(1 + np.random.uniform(-0.10, 0.10, len(unpred_vals)), unpred_vals,
           s=2, color='white', edgecolors=C_UNPRED, linewidth=0.5, zorder=4, alpha=0.6)

ax.set_xticks([0, 1])
ax.set_xticklabels(['Brain-\npredictable', 'Brain-\nunpredictable'], fontsize=6)
ax.set_ylabel('Mean max |r| with\n34 emotion categories', labelpad=3)
ax.set_ylim(0, 0.44)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.20, 1.05, 'B', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

fig1.savefig(OUT / 'figure1_brain_predictable_subspace.png', dpi=300, bbox_inches='tight', facecolor='white')
fig1.savefig(OUT / 'figure1_brain_predictable_subspace.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig1)
print("Figure 1 saved.")

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 2: Categorical Organization
# ═════════════════════════════════════════════════════════════════════════════
fig2, axes2 = plt.subplots(1, 2, figsize=(7.2, 2.8),
                            gridspec_kw={'width_ratios': [3.2, 1.0], 'wspace': 0.40})

# ── 2A: Emotion decoding R² ──
ax = axes2[0]
emo_r2 = r2_pred[:34]
av_r2  = r2_pred[34:]
av_names = ['Arousal', 'Valence']

sort_idx  = np.argsort(emo_r2)[::-1]
emo_sorted = [emo_labels[i] for i in sort_idx]
r2_sorted  = emo_r2[sort_idx]

x_emo = np.arange(34)
x_av  = np.array([35.5, 36.5])

ax.bar(x_emo, r2_sorted, color=C_EMO, width=0.82, linewidth=0, zorder=2)
ax.bar(x_av, av_r2, color=C_DIM, width=0.82, linewidth=0, zorder=2)

ax.axhline(y=emo_r2.mean(), color=C_EMO, linewidth=0.8, linestyle='--', alpha=0.7, zorder=3)
ax.axhline(y=av_r2.mean(), color=C_DIM, linewidth=0.8, linestyle='--', alpha=0.7, zorder=3)

tick_x   = list(x_emo) + list(x_av)
tick_lab = emo_sorted + av_names
ax.set_xticks(tick_x)
ax.set_xticklabels(tick_lab, rotation=90, fontsize=4.8, ha='center')
ax.set_ylabel('Decoding R²\n(brain-pred subspace \u2192 target)', labelpad=3)
ax.set_xlim(-0.8, 38.0)
ax.set_ylim(0, 0.38)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

legend_el = [
    mpatches.Patch(facecolor=C_EMO, label=f'Emotion categories (n=34, mean R²={emo_r2.mean():.3f})'),
    mpatches.Patch(facecolor=C_DIM, label=f'Valence, Arousal (mean R²={av_r2.mean():.3f})'),
]
ax.legend(handles=legend_el, loc='upper right', frameon=False, handlelength=1.0, handletextpad=0.4)
ax.text(-0.06, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# ── 2B: Category/VA ratio ──
ax = axes2[1]
ratio_pred = emo_r2.mean() / av_r2.mean()
ratio_full = r2_all[:34].mean() / r2_all[34:].mean()

ax.bar([0, 1], [ratio_pred, ratio_full], color=[C_PRED, C_FULL], width=0.5, linewidth=0, zorder=2)
ax.axhline(y=1.0, color='black', linewidth=0.75, linestyle=':', zorder=3)
ax.text(1.35, 1.02, 'equal', fontsize=5, color='black', va='bottom')

ax.set_xticks([0, 1])
ax.set_xticklabels(['Brain-pred\nsubspace', 'Full V-JEPA2\n(100 PCs)'], fontsize=6)
ax.set_ylabel('Category / V-A ratio\n(mean R²$_{cat}$ / mean R²$_{V-A}$)', labelpad=3)
ax.set_ylim(0, 3.2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.text(0, ratio_pred + 0.08, f'{ratio_pred:.2f}', ha='center', fontsize=6, color=C_PRED, fontweight='bold')
ax.text(1, ratio_full + 0.08, f'{ratio_full:.2f}', ha='center', fontsize=6, color='#4A4A4A')
ax.text(-0.22, 1.05, 'B', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

fig2.savefig(OUT / 'figure2_categorical_organization.png', dpi=300, bbox_inches='tight', facecolor='white')
fig2.savefig(OUT / 'figure2_categorical_organization.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig2)
print("Figure 2 saved.")

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 3: CCA Brain-Video Shared Space
# ═════════════════════════════════════════════════════════════════════════════
fig3, axes3 = plt.subplots(1, 2, figsize=(7.2, 2.8),
                            gridspec_kw={'width_ratios': [1.5, 2.0], 'wspace': 0.35})

# ── 3A: Canonical correlations ──
ax = axes3[0]
n_show_cc = len(cc_r)  # all CCs
x_cc = np.arange(1, n_show_cc + 1)
colors_cc = [C_CCA if sig_mask[i] else C_UNPRED for i in range(n_show_cc)]
ax.bar(x_cc, cc_r[:n_show_cc], color=colors_cc, width=0.85, linewidth=0, zorder=2)

# null distribution: mean + 95th percentile
null_mean = d_cca['cc_r_null'].mean(axis=1)[:n_show_cc]
null_95 = np.percentile(d_cca['cc_r_null'], 95, axis=1)[:n_show_cc]
ax.plot(x_cc, null_95, 'r--', linewidth=0.8, alpha=0.7, label='Null 95th percentile', zorder=3)

ax.set_xlabel('Canonical component index', labelpad=3)
ax.set_ylabel('Canonical correlation (r)', labelpad=3)
ax.set_xlim(0.3, n_show_cc + 0.7)
ax.set_xticks([1, 5, 10, 15, 20, 25, 30])
ax.set_ylim(0, 0.85)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

legend_cc = [
    mpatches.Patch(facecolor=C_CCA, label=f'Significant (n={int(sig_mask.sum())})'),
    plt.Line2D([0], [0], color='r', linestyle='--', linewidth=0.8, label='Null 95th %ile'),
]
ax.legend(handles=legend_cc, loc='upper right', frameon=False, handlelength=1.2, handletextpad=0.4)
ax.text(-0.12, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# ── 3B: CC emotion profiles (top 5) ──
ax = axes3[1]
n_top = 5
top_emo_per_cc = np.zeros((n_top, 5))  # 5 CCs × top 5 emotions
top_emo_names = set()

for i in range(n_top):
    top5_idx = np.argsort(np.abs(corr_cc[i]))[-5:][::-1]
    for j in top5_idx:
        top_emo_names.add(emo_labels[j])

# Unique emotions across top 5 CCs
sel_emo = sorted(top_emo_names)
sel_idx = [emo_labels.index(e) for e in sel_emo]

# Heatmap: 5 CCs × selected emotions
data_hm = corr_cc[:n_top, :][:, sel_idx]
im = ax.imshow(data_hm, aspect='auto', cmap='RdBu_r', vmin=-0.5, vmax=0.5, interpolation='nearest')
plt.colorbar(im, ax=ax, label='Spearman r', shrink=0.8, pad=0.02)

for i in range(n_top):
    for j in range(len(sel_emo)):
        val = data_hm[i, j]
        color = 'white' if abs(val) > 0.3 else 'black'
        ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=5, color=color)

ax.set_xticks(np.arange(len(sel_emo)))
ax.set_xticklabels(sel_emo, rotation=45, fontsize=5.5, ha='right')
ax.set_yticks(np.arange(n_top))
ax.set_yticklabels([f'CC{i+1} (r={cc_r[i]:.2f})' for i in range(n_top)], fontsize=6)
ax.set_ylabel('Canonical component', labelpad=3)
ax.text(-0.15, 1.05, 'B', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

fig3.savefig(OUT / 'figure3_cca_shared_space.png', dpi=300, bbox_inches='tight', facecolor='white')
fig3.savefig(OUT / 'figure3_cca_shared_space.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig3)
print("Figure 3 saved.")

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 4: Method Comparison
# ═════════════════════════════════════════════════════════════════════════════
fig4, axes4 = plt.subplots(1, 2, figsize=(7.2, 2.5),
                            gridspec_kw={'width_ratios': [1.5, 1.0], 'wspace': 0.35})

# ── 4A: Decoding R² comparison ──
ax = axes4[0]
methods = ['PCA\n(PC1-3)', 'PCA\n(PC1-10)', 'PCA\n(all 100)', 'CCA\n(30 sig)']
cat_r2 = [r2_pca3[:34].mean(), r2_pca10[:34].mean(), r2_pca100[:34].mean(), r2_cca_sig[:34].mean()]
av_r2_vals = [r2_pca3[34:].mean(), r2_pca10[34:].mean(), r2_pca100[34:].mean(), r2_cca_sig[34:].mean()]

x_m = np.arange(len(methods))
w = 0.35
bars1 = ax.bar(x_m - w/2, cat_r2, w, color=C_EMO, label='Category (34)', zorder=2)
bars2 = ax.bar(x_m + w/2, av_r2_vals, w, color=C_DIM, label='Valence/Arousal', zorder=2)

ax.set_xticks(x_m)
ax.set_xticklabels(methods, fontsize=6)
ax.set_ylabel('Mean decoding R²', labelpad=3)
ax.set_ylim(0, 0.22)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(frameon=False, loc='upper left')
ax.text(-0.10, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# ── 4B: Cat/VA ratio ──
ax = axes4[1]
ratios = [cat_r2[i] / max(av_r2_vals[i], 1e-10) for i in range(len(methods))]
colors_ratio = [C_PRED, C_PRED, C_FULL, C_CCA]
ax.bar(np.arange(len(methods)), ratios, color=colors_ratio, width=0.6, linewidth=0, zorder=2)
ax.axhline(y=1.0, color='black', linewidth=0.75, linestyle=':', zorder=3)

for i, r in enumerate(ratios):
    ax.text(i, r + 0.03, f'{r:.2f}', ha='center', fontsize=6, fontweight='bold')

ax.set_xticks(np.arange(len(methods)))
ax.set_xticklabels(methods, fontsize=6)
ax.set_ylabel('Category / V-A ratio', labelpad=3)
ax.set_ylim(0, 2.0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.18, 1.05, 'B', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

fig4.savefig(OUT / 'figure4_method_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
fig4.savefig(OUT / 'figure4_method_comparison.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig4)
print("Figure 4 saved.")

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 5: Subject-level CCA stability
# ═════════════════════════════════════════════════════════════════════════════
fig5, ax5 = plt.subplots(1, 1, figsize=(3.5, 2.5))
n_show_s = 10
x_s = np.arange(1, n_show_s + 1)
for s in range(5):
    ax5.plot(x_s, cc_subj[s, :n_show_s], 'o-', markersize=3, linewidth=0.8,
             alpha=0.5, color=C_UNPRED, label=f'Subj {s+1}' if s == 0 else None)
ax5.plot(x_s, cc_subj[:, :n_show_s].mean(axis=0), 's-', markersize=4, linewidth=1.5,
         color=C_PRED, zorder=5, label='Mean')
ax5.fill_between(x_s,
    cc_subj[:, :n_show_s].mean(axis=0) - cc_subj[:, :n_show_s].std(axis=0),
    cc_subj[:, :n_show_s].mean(axis=0) + cc_subj[:, :n_show_s].std(axis=0),
    alpha=0.2, color=C_PRED, zorder=4)

ax5.set_xlabel('Canonical component', labelpad=3)
ax5.set_ylabel('Canonical correlation (r)', labelpad=3)
ax5.set_xticks(x_s)
ax5.set_ylim(0, 0.85)
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)
ax5.legend(frameon=False, fontsize=5, loc='upper right')

fig5.savefig(OUT / 'figure5_subject_cca_stability.png', dpi=300, bbox_inches='tight', facecolor='white')
fig5.savefig(OUT / 'figure5_subject_cca_stability.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig5)
print("Figure 5 saved.")

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 6: CCA Full Heatmap — CC1-10 × all 34 emotions
# ═════════════════════════════════════════════════════════════════════════════
fig6, ax6 = plt.subplots(1, 1, figsize=(7.2, 10.0))

n_cc_show = len(cc_r)  # all CCs (50)
data_full = corr_cc[:n_cc_show, :]  # (10, 34)

# Sort emotions by CC1 correlation (most interesting ordering)
sort_by_cc1 = np.argsort(corr_cc[0])[::-1]
data_sorted = data_full[:, sort_by_cc1]
emo_sorted_cc = [emo_labels[i] for i in sort_by_cc1]

im = ax6.imshow(data_sorted, aspect='auto', cmap='RdBu_r', vmin=-0.5, vmax=0.5,
                interpolation='nearest')
plt.colorbar(im, ax=ax6, label='Spearman r', shrink=0.7, pad=0.02)

# Annotate significant cells
for i in range(n_cc_show):
    for j in range(34):
        val = data_sorted[i, j]
        if abs(val) > 0.15:
            color = 'white' if abs(val) > 0.3 else 'black'
            ax6.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=4, color=color)

ax6.set_xticks(np.arange(34))
ax6.set_xticklabels(emo_sorted_cc, rotation=90, fontsize=5)
ax6.set_yticks(np.arange(n_cc_show))
ax6.set_yticklabels([f'CC{i+1} (r={cc_r[i]:.2f})' for i in range(n_cc_show)], fontsize=6)
ax6.set_xlabel('Emotion category', labelpad=3)
ax6.set_ylabel('Canonical component', labelpad=3)

fig6.savefig(OUT / 'figure6_cca_full_heatmap.png', dpi=300, bbox_inches='tight', facecolor='white')
fig6.savefig(OUT / 'figure6_cca_full_heatmap.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig6)
print("Figure 6 saved.")

# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 7: PCA vs CCA — Side-by-side Conceptual Comparison
# ═════════════════════════════════════════════════════════════════════════════
fig7, axes7 = plt.subplots(1, 3, figsize=(7.2, 2.8),
                            gridspec_kw={'width_ratios': [1, 1, 1], 'wspace': 0.35})

# ── 7A: PCA R² spectrum ──
ax = axes7[0]
ax.bar(np.arange(1, 16), r2_vjepa[:15],
       color=[C_PRED if i < 3 else C_UNPRED for i in range(15)],
       width=0.8, linewidth=0, zorder=2)
ax.set_xlabel('V-JEPA2 PC', labelpad=3)
ax.set_ylabel('R² (Brain → PC)', labelpad=3)
ax.set_title('PCA+Ridge\n"Which V-JEPA2 axes\ndoes the brain read?"', fontsize=6.5, pad=8)
ax.set_ylim(0, 0.44)
ax.set_xlim(0.3, 15.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# ── 7B: CCA correlation spectrum ──
ax = axes7[1]
ax.bar(np.arange(1, 16), cc_r[:15],
       color=C_CCA, width=0.8, linewidth=0, zorder=2)
null_95_15 = np.percentile(d_cca['cc_r_null'], 95, axis=1)[:15]
ax.plot(np.arange(1, 16), null_95_15, 'r--', linewidth=0.8, alpha=0.7, zorder=3)
ax.set_xlabel('Canonical component', labelpad=3)
ax.set_ylabel('Canonical correlation (r)', labelpad=3)
ax.set_title('CCA\n"What axes do brain\nand V-JEPA2 share?"', fontsize=6.5, pad=8)
ax.set_ylim(0, 0.85)
ax.set_xlim(0.3, 15.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.05, 'B', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# ── 7C: Cat/VA ratio comparison ──
ax = axes7[2]
labels_7c = ['PCA\n(3 PCs)', 'PCA\n(10 PCs)', 'PCA\n(100 PCs)', 'CCA\n(30 CCs)']
ratios_7c = [
    r2_pca3[:34].mean() / max(r2_pca3[34:].mean(), 1e-10),
    r2_pca10[:34].mean() / max(r2_pca10[34:].mean(), 1e-10),
    r2_pca100[:34].mean() / max(r2_pca100[34:].mean(), 1e-10),
    r2_cca_sig[:34].mean() / max(r2_cca_sig[34:].mean(), 1e-10),
]
colors_7c = [C_PRED, C_PRED, C_FULL, C_CCA]
bars = ax.bar(np.arange(4), ratios_7c, color=colors_7c, width=0.6, linewidth=0, zorder=2)
ax.axhline(y=1.0, color='black', linewidth=0.75, linestyle=':', zorder=3)
for i, r in enumerate(ratios_7c):
    ax.text(i, r + 0.03, f'{r:.2f}', ha='center', fontsize=5.5, fontweight='bold')
ax.set_xticks(np.arange(4))
ax.set_xticklabels(labels_7c, fontsize=5.5)
ax.set_ylabel('Cat / V-A ratio', labelpad=3)
ax.set_title('Category bias\nacross methods', fontsize=6.5, pad=8)
ax.set_ylim(0, 2.0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.18, 1.05, 'C', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

fig7.savefig(OUT / 'figure7_pca_vs_cca_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
fig7.savefig(OUT / 'figure7_pca_vs_cca_comparison.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig7)
print("Figure 7 saved.")

print(f"\nAll figures saved to: {OUT}")
print("Done.")
