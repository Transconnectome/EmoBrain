"""
Quick CCA 100 figure — hardcoded CC values from terminal output.
No .npz dependency. Just plots the canonical correlation spectrum.
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
        FONT = candidate
        break

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
C_CCA    = '#4DAF4A'
C_WEAK   = '#A6D96A'
C_DIM    = '#D6604D'
C_REV    = '#FF7F00'
C_EMO    = '#2166AC'

OUT = Path("/pscratch/sd/s/sjmoon/EmoFM/main/figures")
OUT.mkdir(parents=True, exist_ok=True)

# ── Hardcoded CCA 100 results (PCA100 → CCA100) ─────────────────────────────
cc_r = np.array([
    0.7737, 0.6792, 0.6492, 0.6082, 0.5715,
    0.5217, 0.4952, 0.4941, 0.4604, 0.4574,
    0.4385, 0.4280, 0.4151, 0.4008, 0.3895,
    0.3680, 0.3610, 0.3573, 0.3484, 0.3331,
    0.3360, 0.3283, 0.3247, 0.3178, 0.3135,
    0.3069, 0.3065, 0.2967, 0.2955, 0.2870,
    0.2775, 0.2746, 0.2730, 0.2679, 0.2613,
    0.2557, 0.2490, 0.2427, 0.2364, 0.2287,
    0.2312, 0.2235, 0.2189, 0.2164, 0.2144,
    0.2072, 0.2061, 0.2018, 0.1951, 0.1908,
    0.1869, 0.1867, 0.1790, 0.1762, 0.1681,
    0.1660, 0.1641, 0.1620, 0.1577, 0.1550,
    0.1539, 0.1463, 0.1403, 0.1352, 0.1295,
    0.1271, 0.1251, 0.1234, 0.1205, 0.1191,
    0.1152, 0.1099, 0.1045, 0.1038, 0.1015,
    0.0929, 0.0893, 0.0822, 0.0800, 0.0773,
    0.0722, 0.0706, 0.0628, 0.0606, 0.0575,
    0.0530, 0.0507, 0.0476, 0.0431, 0.0366,
    0.0339, 0.0325, 0.0259, 0.0235, 0.0182,
    0.0146, 0.0114, 0.0061, 0.0060, 0.0020,
])

# Also load forward/reverse PCA+Ridge for comparison figure
RES = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN2026/results")
d_pc = np.load(RES / 'brain_predictable_dims.npz', allow_pickle=True)
r2_fwd = d_pc['r2_vjepa_per_dim']  # (100,)
d_rev = np.load(RES / 'exp23_reverse_pca_ridge.npz', allow_pickle=True)
r2_rev = d_rev['r2_obs']  # (100,)

n_above_03 = (cc_r > 0.3).sum()
print(f"CCA 100: CC1={cc_r[0]:.4f}, CCs with r>0.3: {n_above_03}")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE A: CCA 100 canonical correlation spectrum
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(1, 1, figsize=(7.2, 2.8))

x = np.arange(1, 101)
colors = [C_CCA if cc_r[i] > 0.3 else (C_WEAK if cc_r[i] > 0.1 else C_UNPRED) for i in range(100)]
ax.bar(x, cc_r, color=colors, width=0.85, linewidth=0, zorder=2)

# Threshold lines
ax.axhline(y=0.3, color='black', linewidth=0.75, linestyle='--', alpha=0.5, zorder=3)
ax.text(102, 0.305, 'r = 0.3', fontsize=5, va='bottom', color='black')
ax.axhline(y=0.1, color='gray', linewidth=0.5, linestyle=':', alpha=0.5, zorder=3)
ax.text(102, 0.105, 'r = 0.1', fontsize=5, va='bottom', color='gray')

ax.set_xlabel('Canonical component index', labelpad=3)
ax.set_ylabel('Canonical correlation (r)', labelpad=3)
ax.set_xlim(0, 102)
ax.set_xticks([1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
ax.set_ylim(0, 0.85)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

legend_el = [
    mpatches.Patch(facecolor=C_CCA, label=f'Substantial (r > 0.3, n={n_above_03})'),
    mpatches.Patch(facecolor=C_WEAK, label=f'Weak (0.1 < r < 0.3, n={(cc_r > 0.1).sum() - n_above_03})'),
    mpatches.Patch(facecolor=C_UNPRED, label=f'Negligible (r < 0.1, n={(cc_r < 0.1).sum()})'),
]
ax.legend(handles=legend_el, loc='upper right', frameon=False, handlelength=1.2)

fig.savefig(OUT / 'figure_cca100_spectrum.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'figure_cca100_spectrum.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("CCA100 spectrum saved.")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE B: Three-way comparison — Forward / Reverse / CCA
# ═══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.8),
                          gridspec_kw={'width_ratios': [1, 1, 1], 'wspace': 0.35})

mask_fwd = np.zeros(100, dtype=bool)
mask_fwd[:3] = True

# ── A: Forward (Brain → V-JEPA2 PC) ──
ax = axes[0]
n_show = 20
colors_fwd = [C_PRED if mask_fwd[i] else C_UNPRED for i in range(n_show)]
ax.bar(np.arange(1, n_show+1), r2_fwd[:n_show], color=colors_fwd, width=0.8, linewidth=0, zorder=2)
ax.set_xlabel('V-JEPA2 PC', labelpad=3)
ax.set_ylabel('R²', labelpad=3)
ax.set_title('Brain \u2192 V-JEPA2 PC\n3 significant (R² up to 0.37)', fontsize=6.5, pad=6)
ax.set_ylim(0, 0.44)
ax.set_xlim(0.3, n_show + 0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.05, 'A', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

# ── B: Reverse (V-JEPA2 → Brain PC) ──
ax = axes[1]
ax.bar(np.arange(1, n_show+1), r2_rev[:n_show], color=C_REV, width=0.8, linewidth=0, zorder=2)
ax.set_xlabel('Brain-JEPA PC', labelpad=3)
ax.set_ylabel('R²', labelpad=3)
ax.set_title('V-JEPA2 \u2192 Brain PC\n0 significant (all R²=0)', fontsize=6.5, pad=6)
ax.set_ylim(0, 0.44)
ax.set_xlim(0.3, n_show + 0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.05, 'B', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')
ax.text(0.5, 0.5, 'All R² = 0', transform=ax.transAxes,
        fontsize=10, ha='center', va='center', color=C_REV, fontweight='bold', alpha=0.5)

# ── C: CCA (Brain ↔ V-JEPA2) ──
ax = axes[2]
colors_cca = [C_CCA if cc_r[i] > 0.3 else C_UNPRED for i in range(n_show)]
ax.bar(np.arange(1, n_show+1), cc_r[:n_show], color=colors_cca, width=0.8, linewidth=0, zorder=2)
ax.axhline(y=0.3, color='black', linewidth=0.5, linestyle='--', alpha=0.5)
ax.set_xlabel('Canonical component', labelpad=3)
ax.set_ylabel('Canonical r', labelpad=3)
ax.set_title(f'CCA: Brain \u2194 V-JEPA2\n{n_above_03} CCs with r > 0.3', fontsize=6.5, pad=6)
ax.set_ylim(0, 0.85)
ax.set_xlim(0.3, n_show + 0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.text(-0.15, 1.05, 'C', transform=ax.transAxes, fontsize=9, fontweight='bold', va='top')

fig.savefig(OUT / 'figure_three_methods_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'figure_three_methods_comparison.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Three-methods comparison saved.")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE C: Forward vs Reverse Cat/VA ratio
# ═══════════════════════════════════════════════════════════════════════════════
d_17 = np.load(RES / 'exp17_av2d_results.npz', allow_pickle=True)
r2_pred = d_17['r2_pred_vjepa']

fwd_ratio = r2_pred[:34].mean() / r2_pred[34:].mean()

rev_decode = d_rev['r2_decode_Brain_all_100']
rev_ratio = rev_decode[:34].mean() / max(rev_decode[34:].mean(), 1e-10)

fig, ax = plt.subplots(1, 1, figsize=(3.5, 2.8))

bars = ax.bar([0, 1], [fwd_ratio, rev_ratio], color=[C_PRED, C_REV], width=0.5, linewidth=0, zorder=2)
ax.axhline(y=1.0, color='black', linewidth=0.75, linestyle=':', zorder=3)
ax.text(1.3, 1.02, 'equal', fontsize=5, va='bottom')

ax.set_xticks([0, 1])
ax.set_xticklabels(['Forward\nBrain \u2192 V-JEPA2 PC\n(brain-pred subspace)',
                     'Reverse\nV-JEPA2 \u2192 Brain PC\n(all Brain PCs)'], fontsize=5.5)
ax.set_ylabel('Category / V-A ratio\n(mean R²$_{cat}$ / mean R²$_{V-A}$)', labelpad=3)
ax.set_ylim(0, 2.0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.text(0, fwd_ratio + 0.05, f'{fwd_ratio:.2f}', ha='center', fontsize=7, fontweight='bold', color=C_PRED)
ax.text(1, rev_ratio + 0.05, f'{rev_ratio:.2f}', ha='center', fontsize=7, fontweight='bold', color=C_REV)

# Annotations
ax.annotate('Category > V-A', xy=(0, fwd_ratio), xytext=(0.3, 1.7),
            fontsize=5.5, color=C_PRED, ha='center',
            arrowprops=dict(arrowstyle='->', color=C_PRED, lw=0.8))
ax.annotate('V-A > Category', xy=(1, rev_ratio), xytext=(0.7, 0.35),
            fontsize=5.5, color=C_REV, ha='center',
            arrowprops=dict(arrowstyle='->', color=C_REV, lw=0.8))

fig.savefig(OUT / 'figure_forward_vs_reverse_ratio.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(OUT / 'figure_forward_vs_reverse_ratio.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("Forward vs Reverse ratio saved.")

print(f"\nAll saved to {OUT}")
print("Done.")
