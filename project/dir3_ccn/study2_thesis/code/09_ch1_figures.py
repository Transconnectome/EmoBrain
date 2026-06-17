"""
Chapter 1 Figures — 발표용

Fig 1: 48 targets 디코딩 bar chart (Pearson r, sorted, cat/dim 색 구분)
Fig 2: Video identification (cat vs dim vs all)
Fig 3: ROI × emotion heatmap (8 networks × top emotions)
Fig 4: ROI 디코딩 summary bar chart (cat/dim per network)
Fig 5: Principal Gradient scatter (PG1 vs decoding r)
Fig 6: RSA comparison (Cat vs Dim vs VA, group + ROI)
Fig 7: Noise ceiling (group vs subject vs LOO)
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
from pathlib import Path

import matplotlib.font_manager as fm
available = [f.name for f in fm.fontManager.ttflist]
for candidate in ['Helvetica', 'Arial', 'Liberation Sans', 'DejaVu Sans']:
    if candidate in available:
        FONT = candidate; break
rcParams.update({
    'font.family': FONT, 'font.size': 7,
    'axes.titlesize': 8, 'axes.labelsize': 7,
    'xtick.labelsize': 5, 'ytick.labelsize': 6, 'legend.fontsize': 6,
    'axes.linewidth': 0.75, 'pdf.fonttype': 42, 'ps.fonttype': 42,
})

C_CAT = '#2166AC'
C_DIM = '#D6604D'
C_GRAY = '#B2B2B2'

BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
OUT = BASE / "main/figures"
OUT.mkdir(parents=True, exist_ok=True)

# Load
d1 = np.load(BASE / "main/results/ch1_brain_to_behavior.npz", allow_pickle=True)
d3 = np.load(BASE / "main/results/ch1c_roi_decoding.npz", allow_pickle=True)
d4 = np.load(BASE / "main/results/ch1_noise_ceiling.npz", allow_pickle=True)
d5 = np.load(BASE / "main/results/ch1d_principal_gradient.npz", allow_pickle=True)
d6 = np.load(BASE / "main/results/ch1e_rsa.npz", allow_pickle=True)

r = d1['r_group']
r2 = d1['r2_group']
labels = list(d1['all_labels'])
r_roi = d3['r_roi']
vid_roi = d3['vid_id_roi']
rn = list(d3['roi_names'])
r_subj_mean = d4['r_subject_mean']
lower_nc = d4['lower_nc']

# ═══════════════════════════════════════════════════════════════════════════
# Fig 1: 48 targets decoding (sorted bar chart)
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(1, 1, figsize=(7.2, 3.5))
sort_idx = np.argsort(r)[::-1]
colors = [C_CAT if i < 34 else C_DIM for i in sort_idx]
x = np.arange(48)
ax.bar(x, r[sort_idx], color=colors, width=0.8, linewidth=0)
ax.axhline(y=r[:34].mean(), color=C_CAT, linestyle='--', linewidth=0.7, alpha=0.7, label=f'Cat mean r={r[:34].mean():.3f}')
ax.axhline(y=r[34:].mean(), color=C_DIM, linestyle='--', linewidth=0.7, alpha=0.7, label=f'Dim mean r={r[34:].mean():.3f}')
ax.set_xticks(x)
ax.set_xticklabels([labels[i] for i in sort_idx], rotation=90, fontsize=4.5, ha='center')
ax.set_ylabel('Decoding accuracy (Pearson r)', labelpad=3)
ax.set_xlim(-0.8, 48.5)
ax.set_ylim(0, 0.72)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(frameon=False, loc='upper right')
legend_el = [mpatches.Patch(facecolor=C_CAT, label='Category (34)'),
             mpatches.Patch(facecolor=C_DIM, label='Dimension (14)')]
ax.legend(handles=legend_el + ax.get_legend_handles_labels()[0], frameon=False, loc='upper right', fontsize=5)
fig.savefig(OUT / 'ch1_fig1_decoding_48targets.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'ch1_fig1_decoding_48targets.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Fig 1 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# Fig 2: Video identification
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(1, 1, figsize=(3.5, 2.8))
vid_vals = [float(d1['vid_id_cat'])*100, float(d1['vid_id_dim'])*100, float(d1['vid_id_all'])*100]
bars = ax.bar([0, 1, 2], vid_vals, color=[C_CAT, C_DIM, C_GRAY], width=0.5, linewidth=0)
ax.axhline(y=50, color='black', linestyle=':', linewidth=0.75)
ax.text(2.3, 50.5, 'chance', fontsize=5)
for i, v in enumerate(vid_vals):
    ax.text(i, v + 0.8, f'{v:.1f}%', ha='center', fontsize=6, fontweight='bold')
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(['Category\n(34)', 'Dimension\n(14)', 'All\n(48)'], fontsize=6)
ax.set_ylabel('Video identification accuracy (%)', labelpad=3)
ax.set_ylim(0, 95)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# Horikawa reference
ax.text(0, vid_vals[0]-3, f'Horikawa: 81.9%', ha='center', fontsize=4, color='gray')
fig.savefig(OUT / 'ch1_fig2_video_identification.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'ch1_fig2_video_identification.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Fig 2 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# Fig 3: ROI × emotion heatmap (8 networks × 48 targets)
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(1, 1, figsize=(7.2, 3.0))
# Sort targets by overall r
sort_t = np.argsort(r)[::-1]
data = r_roi[:, sort_t]
im = ax.imshow(data, aspect='auto', cmap='YlOrRd', vmin=0, vmax=0.55, interpolation='nearest')
plt.colorbar(im, ax=ax, label='Pearson r', shrink=0.8, pad=0.02)
ax.set_xticks(np.arange(48))
ax.set_xticklabels([labels[i] for i in sort_t], rotation=90, fontsize=3.5)
ax.set_yticks(np.arange(8))
ax.set_yticklabels(rn, fontsize=6)
ax.set_xlabel('Emotion target', labelpad=3)
ax.set_ylabel('Network', labelpad=3)
fig.savefig(OUT / 'ch1_fig3_roi_heatmap.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'ch1_fig3_roi_heatmap.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Fig 3 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# Fig 4: ROI summary (cat/dim per network + video identification)
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={'width_ratios': [1.5, 1]})

# 4A: Cat/Dim r per network
ax = axes[0]
x_n = np.arange(8)
w = 0.35
cat_r_roi = r_roi[:, :34].mean(axis=1)
dim_r_roi = r_roi[:, 34:].mean(axis=1)
# Sort by overall r
sort_n = np.argsort(r_roi.mean(axis=1))[::-1]
ax.barh(x_n, cat_r_roi[sort_n], w, color=C_CAT, label='Category')
ax.barh(x_n + w, dim_r_roi[sort_n], w, color=C_DIM, label='Dimension')
ax.set_yticks(x_n + w/2)
ax.set_yticklabels([rn[i] for i in sort_n], fontsize=6)
ax.set_xlabel('Mean Pearson r', labelpad=3)
ax.invert_yaxis()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(frameon=False, fontsize=5, loc='lower right')
ax.text(-0.15, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# 4B: Video ID per network
ax = axes[1]
vid_cat = vid_roi[:, 0] * 100
vid_dim = vid_roi[:, 1] * 100
ax.barh(x_n, vid_cat[sort_n], w, color=C_CAT)
ax.barh(x_n + w, vid_dim[sort_n], w, color=C_DIM)
ax.axvline(x=50, color='black', linestyle=':', linewidth=0.75)
ax.set_yticks(x_n + w/2)
ax.set_yticklabels([rn[i] for i in sort_n], fontsize=6)
ax.set_xlabel('Video ID accuracy (%)', labelpad=3)
ax.invert_yaxis()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.05, 'B', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

plt.tight_layout()
fig.savefig(OUT / 'ch1_fig4_roi_summary.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'ch1_fig4_roi_summary.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Fig 4 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# Fig 5: Principal Gradient scatter
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(1, 1, figsize=(3.5, 3.0))
net_pg1 = d5['network_pg1']
net_names = list(d5['network_names'])
all_r_mean = [r_roi[rn.index(n)].mean() for n in net_names]

colors_net = ['#7570b3', '#1b9e77', '#d95f02', '#e7298a', '#66a61e', '#e6ab02', '#a6761d']
for i, net in enumerate(net_names):
    ax.scatter(net_pg1[i], all_r_mean[i], s=60, c=colors_net[i], zorder=3, edgecolors='black', linewidth=0.5)
    ax.annotate(net, (net_pg1[i], all_r_mean[i]), fontsize=5, ha='center', va='bottom',
               xytext=(0, 5), textcoords='offset points')

# Trend line
z = np.polyfit(net_pg1, all_r_mean, 1)
x_line = np.linspace(net_pg1.min()-0.002, net_pg1.max()+0.002, 100)
ax.plot(x_line, np.polyval(z, x_line), 'k--', linewidth=0.7, alpha=0.5)

rho = float(d5['r_pg_all'])
p = float(d5['p_pg_all'])
ax.text(0.05, 0.95, f'ρ={rho:.3f}, p={p:.3f}', transform=ax.transAxes, fontsize=6, va='top')

ax.set_xlabel('Principal Gradient 1 (unimodal → transmodal)', labelpad=3)
ax.set_ylabel('Mean decoding r (all 48 targets)', labelpad=3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.savefig(OUT / 'ch1_fig5_pg_scatter.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'ch1_fig5_pg_scatter.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Fig 5 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# Fig 6: RSA comparison (group + ROI)
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), gridspec_kw={'width_ratios': [1, 2]})

# 6A: Group RSA
ax = axes[0]
rsa_vals = [float(d6['rsa_cat']), float(d6['rsa_dim']), float(d6['rsa_va'])]
bars = ax.bar([0, 1, 2], rsa_vals, color=[C_CAT, C_DIM, C_GRAY], width=0.5)
for i, v in enumerate(rsa_vals):
    ax.text(i, v + 0.002, f'{v:.4f}', ha='center', fontsize=5)
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(['Category', 'Dimension', 'VA only'], fontsize=6)
ax.set_ylabel('RSA (Spearman ρ)', labelpad=3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# 6B: ROI RSA
ax = axes[1]
rsa_rc = d6['rsa_roi_cat']
rsa_rd = d6['rsa_roi_dim']
roi_rsa = list(d6['roi_names'])
sort_rsa = np.argsort(rsa_rc)[::-1]
x_r = np.arange(len(roi_rsa))
w = 0.35
ax.barh(x_r, rsa_rc[sort_rsa], w, color=C_CAT, label='Category')
ax.barh(x_r + w, rsa_rd[sort_rsa], w, color=C_DIM, label='Dimension')
ax.set_yticks(x_r + w/2)
ax.set_yticklabels([roi_rsa[i] for i in sort_rsa], fontsize=6)
ax.set_xlabel('RSA (Spearman ρ)', labelpad=3)
ax.invert_yaxis()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(frameon=False, fontsize=5, loc='lower right')
ax.text(-0.10, 1.05, 'B', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

plt.tight_layout()
fig.savefig(OUT / 'ch1_fig6_rsa.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'ch1_fig6_rsa.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Fig 6 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# Fig 7: Noise ceiling (group vs subject vs LOO)
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(1, 1, figsize=(7.2, 3.0))
sort_r = np.argsort(r)[::-1]
x = np.arange(48)
ax.bar(x, r[sort_r], width=0.8, color=[C_CAT if sort_r[i] < 34 else C_DIM for i in range(48)],
       alpha=0.8, label='Group r')
ax.scatter(x, r_subj_mean[sort_r], s=8, color='black', zorder=3, label='Subject mean r', marker='v')
ax.scatter(x, lower_nc[sort_r], s=8, color='green', zorder=3, label='LOO NC', marker='^')
ax.set_xticks(x)
ax.set_xticklabels([labels[i] for i in sort_r], rotation=90, fontsize=3.5)
ax.set_ylabel('Pearson r', labelpad=3)
ax.set_xlim(-0.8, 48.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(frameon=False, fontsize=5, loc='upper right')
fig.savefig(OUT / 'ch1_fig7_noise_ceiling.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'ch1_fig7_noise_ceiling.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Fig 7 saved.")

print(f"\nAll figures saved to {OUT}")
print("Done.")
