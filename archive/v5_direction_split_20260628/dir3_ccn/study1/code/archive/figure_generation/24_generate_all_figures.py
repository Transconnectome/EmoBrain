"""
Generate all main figures including CCA and reverse PCA+Ridge.
Saves to /pscratch/sd/s/sjmoon/EmoFM/main/figures/

Figure 1: Brain-predictable subspace (PCA+Ridge)
Figure 2: Categorical organization
Figure 3: CCA shared space
Figure 4: Method comparison (decoding)
Figure 5: Subject-level CCA stability
Figure 6: CCA full heatmap
Figure 7: PCA vs CCA side-by-side
Figure 8: Forward vs Reverse asymmetry (NEW)
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
for candidate in ['Helvetica', 'Arial', 'Liberation Sans', 'DejaVu Sans']:
    if candidate in available:
        FONT = candidate
        break
print(f"Using font: {FONT}")

rcParams.update({
    'font.family': FONT, 'font.size': 7,
    'axes.titlesize': 8, 'axes.labelsize': 7,
    'xtick.labelsize': 6, 'ytick.labelsize': 6, 'legend.fontsize': 6,
    'axes.linewidth': 0.75,
    'xtick.major.width': 0.75, 'ytick.major.width': 0.75,
    'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
    'pdf.fonttype': 42, 'ps.fonttype': 42,
})

C_PRED   = '#2166AC'
C_UNPRED = '#B2B2B2'
C_EMO    = '#2166AC'
C_DIM    = '#D6604D'
C_FULL   = '#92C5DE'
C_CCA    = '#4DAF4A'
C_REV    = '#FF7F00'

BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
RES  = BASE / "CCN2026/results"
OUT  = BASE / "main/figures"
OUT.mkdir(parents=True, exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────
d_pc   = np.load(RES / 'brain_predictable_dims.npz', allow_pickle=True)
d_cor  = np.load(RES / 'pc_emotion_correlation.npz', allow_pickle=True)
d_17   = np.load(RES / 'exp17_av2d_results.npz', allow_pickle=True)
# Use CCA 100 results if available, else fall back to old CCA 30
cca100_path = RES / 'cca100_results.npz'
cca30_path = RES / 'cca_brain_video_results.npz'
if cca100_path.exists():
    d_cca = np.load(cca100_path, allow_pickle=True)
    print("Using CCA 100 results.")
else:
    d_cca = np.load(cca30_path, allow_pickle=True)
    print("Using CCA 30 results (CCA 100 not yet available).")
d_rev  = np.load(RES / 'exp23_reverse_pca_ridge.npz', allow_pickle=True)

r2_vjepa   = d_pc['r2_vjepa_per_dim']
mask_vjepa = np.zeros(100, dtype=bool)
mask_vjepa[:3] = True
corr_emo   = d_cor['corr_vjepa_emo']
emo_labels = list(d_cor['emotion_labels'])
r2_pred    = d_17['r2_pred_vjepa']
r2_all     = d_17['r2_all_vjepa']

cc_r       = d_cca['cc_r']
corr_cc    = d_cca['corr_cc_emo']
corr_cc_av = d_cca['corr_cc_av']
max_r_cc   = d_cca['max_r_per_cc']
r2_pca3    = d_cca['r2_pca_3']
r2_pca10   = d_cca['r2_pca_10']
r2_pca100  = d_cca['r2_pca_100']
cc_subj    = d_cca['cc_r_per_subj']

# Handle different key names between CCA30 and CCA100
if 'r2_cca_meaningful' in d_cca:
    r2_cca_sig = d_cca['r2_cca_meaningful']
    sig_mask = d_cca.get('meaningful_mask', cc_r > 0.3)
elif 'r2_cca_sig' in d_cca:
    r2_cca_sig = d_cca['r2_cca_sig']
    sig_mask = d_cca.get('sig_mask', cc_r > 0.3)
else:
    r2_cca_sig = d_cca.get('r2_cca_all', np.zeros(36))
    sig_mask = cc_r > 0.3

n_meaningful = int(sig_mask.sum()) if hasattr(sig_mask, 'sum') else (cc_r > 0.3).sum()
print(f"CCA: {len(cc_r)} CCs, {n_meaningful} meaningful (r>0.3)")

r2_rev     = d_rev['r2_obs']
mse_rev    = d_rev['mse_obs']
var_brain  = d_rev['brain_pca_var_ratio']

max_r_per_pc = np.max(np.abs(corr_emo), axis=1)
print("Data loaded.")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Brain-Predictable Subspace (PCA+Ridge)
# ═══════════════════════════════════════════════════════════════════════════════
fig1, axes1 = plt.subplots(1, 2, figsize=(7.2, 2.5),
                            gridspec_kw={'width_ratios': [3, 1.2], 'wspace': 0.38})
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

ax = axes1[1]
pred_vals = max_r_per_pc[mask_vjepa]
unpred_vals = max_r_per_pc[~mask_vjepa]
ax.bar([0, 1], [pred_vals.mean(), unpred_vals.mean()],
       color=[C_PRED, C_UNPRED], width=0.5, linewidth=0, zorder=2)
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

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2: Categorical Organization
# ═══════════════════════════════════════════════════════════════════════════════
fig2, axes2 = plt.subplots(1, 2, figsize=(7.2, 2.8),
                            gridspec_kw={'width_ratios': [3.2, 1.0], 'wspace': 0.40})
ax = axes2[0]
emo_r2 = r2_pred[:34]
av_r2 = r2_pred[34:]
sort_idx = np.argsort(emo_r2)[::-1]
emo_sorted = [emo_labels[i] for i in sort_idx]
r2_sorted = emo_r2[sort_idx]
x_emo = np.arange(34)
x_av = np.array([35.5, 36.5])
ax.bar(x_emo, r2_sorted, color=C_EMO, width=0.82, linewidth=0, zorder=2)
ax.bar(x_av, av_r2, color=C_DIM, width=0.82, linewidth=0, zorder=2)
ax.axhline(y=emo_r2.mean(), color=C_EMO, linewidth=0.8, linestyle='--', alpha=0.7, zorder=3)
ax.axhline(y=av_r2.mean(), color=C_DIM, linewidth=0.8, linestyle='--', alpha=0.7, zorder=3)
tick_x = list(x_emo) + list(x_av)
tick_lab = emo_sorted + ['Arousal', 'Valence']
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

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 3: CCA Brain-Video Shared Space
# ═══════════════════════════════════════════════════════════════════════════════
n_cc = len(cc_r)
fig3, axes3 = plt.subplots(1, 2, figsize=(7.2, 2.8),
                            gridspec_kw={'width_ratios': [1.5, 2.0], 'wspace': 0.35})
ax = axes3[0]
x_cc = np.arange(1, n_cc + 1)
colors_cc = [C_CCA if sig_mask[i] else C_UNPRED for i in range(n_cc)]
ax.bar(x_cc, cc_r, color=colors_cc, width=0.85, linewidth=0, zorder=2)
null_95 = np.percentile(d_cca['cc_r_null'], 95, axis=1)
ax.plot(x_cc, null_95, 'r--', linewidth=0.8, alpha=0.7, label='Null 95th %ile', zorder=3)
ax.set_xlabel('Canonical component index', labelpad=3)
ax.set_ylabel('Canonical correlation (r)', labelpad=3)
ax.set_xlim(0.3, n_cc + 0.7)
ax.set_ylim(0, 0.85)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
legend_cc = [
    mpatches.Patch(facecolor=C_CCA, label=f'Significant (n={int(sig_mask.sum())})'),
    plt.Line2D([0], [0], color='r', linestyle='--', linewidth=0.8, label='Null 95th %ile'),
]
ax.legend(handles=legend_cc, loc='upper right', frameon=False)
ax.text(-0.12, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

ax = axes3[1]
n_top = 5
top_emo_names = set()
for i in range(n_top):
    top5_idx = np.argsort(np.abs(corr_cc[i]))[-5:][::-1]
    for j in top5_idx:
        top_emo_names.add(emo_labels[j])
sel_emo = sorted(top_emo_names)
sel_idx = [emo_labels.index(e) for e in sel_emo]
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

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 4: Method Comparison
# ═══════════════════════════════════════════════════════════════════════════════
fig4, axes4 = plt.subplots(1, 2, figsize=(7.2, 2.5),
                            gridspec_kw={'width_ratios': [1.5, 1.0], 'wspace': 0.35})
ax = axes4[0]
methods = ['PCA\n(PC1-3)', 'PCA\n(PC1-10)', 'PCA\n(all 100)', f'CCA\n({n_meaningful} r>0.3)']
cat_r2 = [r2_pca3[:34].mean(), r2_pca10[:34].mean(), r2_pca100[:34].mean(), r2_cca_sig[:34].mean()]
av_r2_vals = [r2_pca3[34:].mean(), r2_pca10[34:].mean(), r2_pca100[34:].mean(), r2_cca_sig[34:].mean()]
x_m = np.arange(len(methods))
w = 0.35
ax.bar(x_m - w/2, cat_r2, w, color=C_EMO, label='Category (34)', zorder=2)
ax.bar(x_m + w/2, av_r2_vals, w, color=C_DIM, label='Valence/Arousal', zorder=2)
ax.set_xticks(x_m)
ax.set_xticklabels(methods, fontsize=6)
ax.set_ylabel('Mean decoding R²', labelpad=3)
ax.set_ylim(0, 0.22)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(frameon=False, loc='upper left')
ax.text(-0.10, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

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

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 5: Subject-level CCA stability
# ═══════════════════════════════════════════════════════════════════════════════
fig5, ax5 = plt.subplots(1, 1, figsize=(3.5, 2.5))
n_show_s = 10
x_s = np.arange(1, n_show_s + 1)
for s in range(5):
    ax5.plot(x_s, cc_subj[s, :n_show_s], 'o-', markersize=3, linewidth=0.8,
             alpha=0.5, color=C_UNPRED)
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

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 6: CCA Full Heatmap
# ═══════════════════════════════════════════════════════════════════════════════
fig6, ax6 = plt.subplots(1, 1, figsize=(7.2, 6.5))
sort_by_cc1 = np.argsort(corr_cc[0])[::-1]
data_sorted = corr_cc[:, sort_by_cc1]
emo_sorted_cc = [emo_labels[i] for i in sort_by_cc1]
im = ax6.imshow(data_sorted, aspect='auto', cmap='RdBu_r', vmin=-0.5, vmax=0.5, interpolation='nearest')
plt.colorbar(im, ax=ax6, label='Spearman r', shrink=0.7, pad=0.02)
for i in range(n_cc):
    for j in range(34):
        val = data_sorted[i, j]
        if abs(val) > 0.15:
            color = 'white' if abs(val) > 0.3 else 'black'
            ax6.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=4, color=color)
ax6.set_xticks(np.arange(34))
ax6.set_xticklabels(emo_sorted_cc, rotation=90, fontsize=5)
ax6.set_yticks(np.arange(n_cc))
ax6.set_yticklabels([f'CC{i+1} (r={cc_r[i]:.2f})' for i in range(n_cc)], fontsize=5)
ax6.set_xlabel('Emotion category', labelpad=3)
ax6.set_ylabel('Canonical component', labelpad=3)

fig6.savefig(OUT / 'figure6_cca_full_heatmap.png', dpi=300, bbox_inches='tight', facecolor='white')
fig6.savefig(OUT / 'figure6_cca_full_heatmap.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig6)
print("Figure 6 saved.")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 7: PCA vs CCA side-by-side
# ═══════════════════════════════════════════════════════════════════════════════
fig7, axes7 = plt.subplots(1, 3, figsize=(7.2, 2.8),
                            gridspec_kw={'width_ratios': [1, 1, 1], 'wspace': 0.35})
ax = axes7[0]
ax.bar(np.arange(1, 16), r2_vjepa[:15],
       color=[C_PRED if i < 3 else C_UNPRED for i in range(15)],
       width=0.8, linewidth=0, zorder=2)
ax.set_xlabel('V-JEPA2 PC', labelpad=3)
ax.set_ylabel('R² (Brain \u2192 PC)', labelpad=3)
ax.set_title('PCA+Ridge\n"Which V-JEPA2 axes\ndoes the brain read?"', fontsize=6.5, pad=8)
ax.set_ylim(0, 0.44)
ax.set_xlim(0.3, 15.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

ax = axes7[1]
ax.bar(np.arange(1, 16), cc_r[:15], color=C_CCA, width=0.8, linewidth=0, zorder=2)
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

ax = axes7[2]
labels_7c = ['PCA\n(3 PCs)', 'PCA\n(10 PCs)', 'PCA\n(100)', f'CCA\n({n_meaningful})']
ratios_7c = [
    r2_pca3[:34].mean() / max(r2_pca3[34:].mean(), 1e-10),
    r2_pca10[:34].mean() / max(r2_pca10[34:].mean(), 1e-10),
    r2_pca100[:34].mean() / max(r2_pca100[34:].mean(), 1e-10),
    r2_cca_sig[:34].mean() / max(r2_cca_sig[34:].mean(), 1e-10),
]
colors_7c = [C_PRED, C_PRED, C_FULL, C_CCA]
ax.bar(np.arange(4), ratios_7c, color=colors_7c, width=0.6, linewidth=0, zorder=2)
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

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 8: Forward vs Reverse Asymmetry (NEW)
# ═══════════════════════════════════════════════════════════════════════════════
fig8, axes8 = plt.subplots(1, 3, figsize=(7.2, 2.8),
                            gridspec_kw={'width_ratios': [1.2, 1.2, 1.0], 'wspace': 0.38})

# ── 8A: Forward R² (Brain → V-JEPA2 PC) ──
ax = axes8[0]
n_show_8 = 20
x8 = np.arange(1, n_show_8 + 1)
colors_fwd = [C_PRED if mask_vjepa[i] else C_UNPRED for i in range(n_show_8)]
ax.bar(x8, r2_vjepa[:n_show_8], color=colors_fwd, width=0.8, linewidth=0, zorder=2)
ax.set_xlabel('V-JEPA2 PC index', labelpad=3)
ax.set_ylabel('R²', labelpad=3)
ax.set_title('Forward: Brain \u2192 V-JEPA2 PC\n"Can brain predict video axes?"', fontsize=6.5, pad=8)
ax.set_ylim(0, 0.44)
ax.set_xlim(0.3, n_show_8 + 0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.12, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')
# Annotate
ax.text(0.95, 0.85, f'3 PCs\nsignificant', transform=ax.transAxes,
        fontsize=6, ha='right', va='top', color=C_PRED, fontweight='bold')

# ── 8B: Reverse R² (V-JEPA2 → Brain PC) ──
ax = axes8[1]
ax.bar(x8, r2_rev[:n_show_8], color=C_REV, width=0.8, linewidth=0, zorder=2)
ax.set_xlabel('Brain-JEPA PC index', labelpad=3)
ax.set_ylabel('R²', labelpad=3)
ax.set_title('Reverse: V-JEPA2 \u2192 Brain PC\n"Can video predict brain axes?"', fontsize=6.5, pad=8)
ax.set_ylim(0, 0.44)
ax.set_xlim(0.3, n_show_8 + 0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.12, 1.05, 'B', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')
# Annotate
ax.text(0.95, 0.85, f'0 PCs\nsignificant\n(all R²=0)', transform=ax.transAxes,
        fontsize=6, ha='right', va='top', color=C_REV, fontweight='bold')

# ── 8C: Cat/VA ratio comparison ──
ax = axes8[2]
# Forward brain-pred decoding
fwd_cat = r2_pred[:34].mean()
fwd_av = r2_pred[34:].mean()
fwd_ratio = fwd_cat / max(fwd_av, 1e-10)

# Reverse: brain PC decoding
rev_data = d_rev['r2_decode_Brain_all_100']
rev_cat = rev_data[:34].mean()
rev_av = rev_data[34:].mean()
rev_ratio = rev_cat / max(rev_av, 1e-10)

ax.bar([0, 1], [fwd_ratio, rev_ratio], color=[C_PRED, C_REV], width=0.5, linewidth=0, zorder=2)
ax.axhline(y=1.0, color='black', linewidth=0.75, linestyle=':', zorder=3)
ax.set_xticks([0, 1])
ax.set_xticklabels(['Forward\n(Brain\u2192Video)', 'Reverse\n(Video\u2192Brain)'], fontsize=6)
ax.set_ylabel('Cat / V-A ratio', labelpad=3)
ax.set_title('Emotion structure\nof predictable axes', fontsize=6.5, pad=8)
ax.set_ylim(0, 2.0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(0, fwd_ratio + 0.05, f'{fwd_ratio:.2f}', ha='center', fontsize=6, fontweight='bold', color=C_PRED)
ax.text(1, rev_ratio + 0.05, f'{rev_ratio:.2f}', ha='center', fontsize=6, fontweight='bold', color=C_REV)
ax.text(-0.22, 1.05, 'C', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

fig8.savefig(OUT / 'figure8_forward_vs_reverse.png', dpi=300, bbox_inches='tight', facecolor='white')
fig8.savefig(OUT / 'figure8_forward_vs_reverse.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig8)
print("Figure 8 saved.")

print(f"\nAll figures saved to: {OUT}")
print("Done.")
