"""
Chapter 2 Figures — 발표용

Fig 1: Variance Partitioning 개요 (Total vs Shared vs Unique, V-JEPA2)
Fig 2: 감정별 Unique r (top 20, ???가 큰 감정)
Fig 3: V-JEPA2 vs CLIP 렌즈 비교
Fig 4: Confound control (AI vs AI+Vis+Sem)
Fig 5: Forward/Reverse/CCA summary (Ch2-0)
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

C_TOTAL = '#2166AC'
C_SHARED = '#92C5DE'
C_UNIQUE = '#B2182B'
C_CAT = '#2166AC'
C_DIM = '#D6604D'
C_VJEPA = '#4DAF4A'
C_CLIP = '#FF7F00'

BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
OUT = BASE / "main/figures"

# Load Ch2-1 results
d = np.load(BASE / "main/results/ch2_1_variance_partitioning.npz", allow_pickle=True)
labels = list(d['all_labels'])

# V-JEPA2
vj_total = d['V-JEPA2_r_total']
vj_shared = d['V-JEPA2_r_shared']
vj_unique = d['V-JEPA2_r_unique']
vj_var = float(d['V-JEPA2_var_explained'])

# CLIP
cl_total = d['CLIP_r_total']
cl_shared = d['CLIP_r_shared']
cl_unique = d['CLIP_r_unique']
cl_var = float(d['CLIP_var_explained'])

# Confound (V-JEPA2+Vis+Sem) — if available
try:
    vj_vs_unique = d['V-JEPA2_plus_Vis_plus_Sem_r_unique']
    vj_vs_var = float(d['V-JEPA2_plus_Vis_plus_Sem_var_explained'])
    cl_vs_unique = d['CLIP_plus_Vis_plus_Sem_r_unique']
    cl_vs_var = float(d['CLIP_plus_Vis_plus_Sem_var_explained'])
    has_confound = True
except:
    has_confound = False

# Ch2-0
d0 = np.load(BASE / "main/results/ch2_0_alignment.npz", allow_pickle=True)

# ═══════════════════════════════════════════════════════════════════════════
# Fig 1: Variance Partitioning Overview (V-JEPA2)
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={'width_ratios': [1, 1.5]})

# 1A: Cat/Dim summary bars
ax = axes[0]
x = np.arange(3)
w = 0.35
cat_vals = [vj_total[:34].mean(), vj_shared[:34].mean(), vj_unique[:34].mean()]
dim_vals = [vj_total[34:].mean(), vj_shared[34:].mean(), vj_unique[34:].mean()]
ax.bar(x - w/2, cat_vals, w, color=C_CAT, label='Category (34)')
ax.bar(x + w/2, dim_vals, w, color=C_DIM, label='Dimension (14)')
ax.set_xticks(x)
ax.set_xticklabels(['Total\n(fMRI)', 'AI-shared\n(V-JEPA2)', 'AI-unique\n(???)'], fontsize=6)
ax.set_ylabel('Mean Pearson r', labelpad=3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(frameon=False, fontsize=5)
# Annotate variance
ax.text(0.5, 0.95, f'V-JEPA2 explains {vj_var*100:.0f}% of fMRI',
        transform=ax.transAxes, fontsize=5, ha='center', va='top', style='italic')
ax.text(-0.12, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# 1B: Per-emotion Total vs Unique (scatter)
ax = axes[1]
for i in range(48):
    c = C_CAT if i < 34 else C_DIM
    ax.scatter(vj_total[i], vj_unique[i], s=12, c=c, alpha=0.7, edgecolors='none')
# Label top unique emotions
top_unique = np.argsort(vj_unique)[::-1][:5]
for i in top_unique:
    ax.annotate(labels[i], (vj_total[i], vj_unique[i]), fontsize=4, ha='left',
               xytext=(3, 2), textcoords='offset points')
# Diagonal
lim = max(vj_total.max(), vj_unique.max()) + 0.05
ax.plot([0, lim], [0, lim], 'k:', linewidth=0.5, alpha=0.3)
ax.set_xlabel('Total r (full fMRI)', labelpad=3)
ax.set_ylabel('AI-unique r (??? residual)', labelpad=3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(handles=[mpatches.Patch(facecolor=C_CAT, label='Cat'),
                    mpatches.Patch(facecolor=C_DIM, label='Dim')],
          frameon=False, fontsize=5, loc='upper left')
ax.text(-0.10, 1.05, 'B', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

plt.tight_layout()
fig.savefig(OUT / 'ch2_fig1_variance_partitioning.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'ch2_fig1_variance_partitioning.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Fig 1 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# Fig 2: Top ??? emotions (unique r, sorted)
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(1, 1, figsize=(7.2, 3.5))
sort_u = np.argsort(vj_unique)[::-1]
colors = [C_CAT if i < 34 else C_DIM for i in sort_u]
x = np.arange(48)
ax.bar(x, vj_unique[sort_u], color=colors, width=0.8, linewidth=0)
ax.axhline(y=vj_unique[:34].mean(), color=C_CAT, linestyle='--', linewidth=0.7, alpha=0.7,
           label=f'Cat unique mean={vj_unique[:34].mean():.3f}')
ax.axhline(y=vj_unique[34:].mean(), color=C_DIM, linestyle='--', linewidth=0.7, alpha=0.7,
           label=f'Dim unique mean={vj_unique[34:].mean():.3f}')
ax.set_xticks(x)
ax.set_xticklabels([labels[i] for i in sort_u], rotation=90, fontsize=4.5)
ax.set_ylabel('AI-unique r (V-JEPA2 residual → emotion)', labelpad=3)
ax.set_xlim(-0.8, 48.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(frameon=False, fontsize=5, loc='upper right')
fig.savefig(OUT / 'ch2_fig2_unique_emotions.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'ch2_fig2_unique_emotions.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Fig 2 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# Fig 3: V-JEPA2 vs CLIP lens comparison
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))

# 3A: Unique r comparison per emotion
ax = axes[0]
for i in range(48):
    c = C_CAT if i < 34 else C_DIM
    ax.scatter(vj_unique[i], cl_unique[i], s=12, c=c, alpha=0.7, edgecolors='none')
lim = max(vj_unique.max(), cl_unique.max()) + 0.05
ax.plot([0, lim], [0, lim], 'k:', linewidth=0.5, alpha=0.3)
ax.set_xlabel('V-JEPA2 unique r', labelpad=3)
ax.set_ylabel('CLIP unique r', labelpad=3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.12, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# 3B: Summary bars
ax = axes[1]
x = np.arange(2)
w = 0.3
# V-JEPA2
ax.bar(x - w/2, [vj_unique[:34].mean(), vj_unique[34:].mean()], w,
       color=C_VJEPA, label=f'V-JEPA2 ({vj_var*100:.0f}% expl.)')
# CLIP
ax.bar(x + w/2, [cl_unique[:34].mean(), cl_unique[34:].mean()], w,
       color=C_CLIP, label=f'CLIP ({cl_var*100:.0f}% expl.)')
ax.set_xticks(x)
ax.set_xticklabels(['Category', 'Dimension'], fontsize=6)
ax.set_ylabel('Mean unique r (???)', labelpad=3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(frameon=False, fontsize=5)
ax.text(-0.12, 1.05, 'B', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

plt.tight_layout()
fig.savefig(OUT / 'ch2_fig3_lens_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'ch2_fig3_lens_comparison.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Fig 3 saved.")

# ═══════════════════════════════════════════════════════════════════════════
# Fig 4: Confound control (if available)
# ═══════════════════════════════════════════════════════════════════════════
if has_confound:
    fig, ax = plt.subplots(1, 1, figsize=(5.0, 3.0))
    x = np.arange(2)
    w = 0.18
    ax.bar(x - 1.5*w, [vj_unique[:34].mean(), vj_unique[34:].mean()], w,
           color=C_VJEPA, label='V-JEPA2 only')
    ax.bar(x - 0.5*w, [vj_vs_unique[:34].mean(), vj_vs_unique[34:].mean()], w,
           color='#2CA02C', label='V-JEPA2+Vis+Sem')
    ax.bar(x + 0.5*w, [cl_unique[:34].mean(), cl_unique[34:].mean()], w,
           color=C_CLIP, label='CLIP only')
    ax.bar(x + 1.5*w, [cl_vs_unique[:34].mean(), cl_vs_unique[34:].mean()], w,
           color='#D62728', label='CLIP+Vis+Sem')
    ax.set_xticks(x)
    ax.set_xticklabels(['Category', 'Dimension'], fontsize=6)
    ax.set_ylabel('Unique r (???)', labelpad=3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(frameon=False, fontsize=5)
    ax.set_title('Confound control: ??? survives after removing all features', fontsize=7)
    fig.savefig(OUT / 'ch2_fig4_confound.png', dpi=300, bbox_inches='tight', facecolor='white')
    fig.savefig(OUT / 'ch2_fig4_confound.pdf', bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Fig 4 saved.")
else:
    print("Fig 4 skipped (confound control not yet complete).")

# ═══════════════════════════════════════════════════════════════════════════
# Fig 5: Forward/Reverse/CCA — Raw fMRI vs Brain-JEPA (Ch2-0)
# ═══════════════════════════════════════════════════════════════════════════
C_RAW = '#2166AC'
C_BJ = '#FF7F00'

fig, axes = plt.subplots(2, 3, figsize=(7.2, 5.0))

# Row 1: Raw fMRI
fwd_raw = d0['fwd_raw_vj']
rev_raw = d0['rev_vj_raw']
cca_raw = d0['cca_raw_vj']

ax = axes[0, 0]
ax.bar(np.arange(20), fwd_raw, color=C_RAW, width=0.8)
ax.set_ylabel('R²', labelpad=3)
ax.set_title(f'Forward: Raw fMRI → V-JEPA2\n{(fwd_raw>0.01).sum()}/20 sig', fontsize=6)
ax.set_ylim(0, 0.55)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.08, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

ax = axes[0, 1]
ax.bar(np.arange(20), rev_raw, color=C_RAW, width=0.8)
ax.set_title(f'Reverse: V-JEPA2 → Raw fMRI\n{(rev_raw>0.01).sum()}/20 sig', fontsize=6)
ax.set_ylim(0, 0.55)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.08, 'B', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

ax = axes[0, 2]
ax.bar(np.arange(30), cca_raw, color=C_RAW, width=0.85)
ax.axhline(y=0.3, color='red', linestyle='--', linewidth=0.7, alpha=0.5)
ax.set_title(f'CCA: Raw ↔ V-JEPA2\n{(cca_raw>0.3).sum()}/30 r>0.3', fontsize=6)
ax.set_ylim(0, 0.85)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.08, 'C', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# Row 2: Brain-JEPA
fwd_bj = d0['fwd_bj_vj']
rev_bj = d0['rev_vj_bj']
cca_bj = d0['cca_bj_vj']

ax = axes[1, 0]
ax.bar(np.arange(20), fwd_bj, color=C_BJ, width=0.8)
ax.set_xlabel('V-JEPA2 PC', labelpad=3)
ax.set_ylabel('R²', labelpad=3)
ax.set_title(f'Forward: Brain-JEPA → V-JEPA2\n{(fwd_bj>0.01).sum()}/20 sig', fontsize=6)
ax.set_ylim(0, 0.55)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.08, 'D', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

ax = axes[1, 1]
ax.bar(np.arange(20), rev_bj, color=C_BJ, width=0.8)
ax.set_xlabel('Brain-JEPA PC', labelpad=3)
ax.set_title(f'Reverse: V-JEPA2 → Brain-JEPA\n{(rev_bj>0.01).sum()}/20 sig', fontsize=6)
ax.set_ylim(0, 0.55)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.08, 'E', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

ax = axes[1, 2]
ax.bar(np.arange(30), cca_bj, color=C_BJ, width=0.85)
ax.axhline(y=0.3, color='red', linestyle='--', linewidth=0.7, alpha=0.5)
ax.set_xlabel('Canonical component', labelpad=3)
ax.set_title(f'CCA: BJ ↔ V-JEPA2\n{(cca_bj>0.3).sum()}/30 r>0.3', fontsize=6)
ax.set_ylim(0, 0.85)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.08, 'F', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# Row labels
axes[0, 0].text(-0.35, 0.5, 'Raw fMRI', transform=axes[0, 0].transAxes,
                fontsize=8, fontweight='bold', va='center', rotation=90, color=C_RAW)
axes[1, 0].text(-0.35, 0.5, 'Brain-JEPA', transform=axes[1, 0].transAxes,
                fontsize=8, fontweight='bold', va='center', rotation=90, color=C_BJ)

plt.tight_layout()
fig.savefig(OUT / 'ch2_fig5_alignment.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'ch2_fig5_alignment.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Fig 5 saved.")

print(f"\nAll Ch2 figures saved to {OUT}")
print("Done.")
