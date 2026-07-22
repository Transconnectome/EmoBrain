"""
Exp 28: Factor Rotation + UMAP/t-SNE + Cowen Comparison

1. V-JEPA2 PCA + varimax rotation → interpretable factors
2. Brain prediction of rotated factors
3. Emotion rating PCA + varimax (Cowen replication)
4. UMAP/t-SNE visualizations:
   a. 2196 videos in brain-pred subspace, colored by emotion
   b. 34 emotions in brain-pred space (emotion map)
   c. 2196 videos in CCA space
5. Cowen factor structure comparison
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from scipy.stats import spearmanr
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')

BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
RES  = BASE / "CCN2026/results"
OUT  = BASE / "main/results"
FIG  = BASE / "main/figures"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

EMOTION_LABELS = [
    'Admiration', 'Adoration', 'Aesthetic appreciation', 'Amusement', 'Anger',
    'Anxiety', 'Awe', 'Awkwardness', 'Boredom', 'Calmness', 'Confusion',
    'Contempt', 'Craving', 'Disgust', 'Empathic pain', 'Entrancement',
    'Excitement', 'Fear', 'Horror', 'Interest', 'Joy', 'Nostalgia', 'Relief',
    'Romance', 'Sadness', 'Satisfaction', 'Sexual desire', 'Surprise',
    'Sympathy', 'Triumph', 'Uncomfortable', 'Annoyance', 'Envy', 'Guilt'
]
BASIC_6 = ['Anger', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise']

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
vjepa = np.load(BASE / "video_embeddings/vjepa2_embeddings.npy").astype(np.float64)
brain_raw = np.load(BASE / "brain_embeddings/brain_jepa_embeddings.npy").astype(np.float64)
brain_mean = brain_raw.mean(axis=0)
fmri_mean = np.load(BASE / "raw_fmri_results/fmri_raw.npy").astype(np.float64).mean(axis=0)

meta = pd.read_csv(Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv"))
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)
score_cols = [f"score_{i}" for i in range(34)]
emotion_scores = meta[score_cols].values.astype(np.float64)
arousal = meta['arousal_score'].values.astype(np.float64)
valence = meta['valence_score'].values.astype(np.float64)

model = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

# ── Varimax rotation function ────────────────────────────────────────────────
def varimax(Phi, gamma=1.0, q=50, tol=1e-6):
    """Varimax rotation of loading matrix Phi (n_vars x n_factors)."""
    p, k = Phi.shape
    R = np.eye(k)
    d = 0
    for _ in range(q):
        Lambda = Phi @ R
        u, s, vt = np.linalg.svd(
            Phi.T @ (Lambda**3 - (gamma / p) * Lambda @ np.diag(np.diag(Lambda.T @ Lambda)))
        )
        R = u @ vt
        d_new = np.sum(s)
        if d_new - d < tol:
            break
        d = d_new
    return Phi @ R, R

print("Data loaded.")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("1. V-JEPA2 PCA + VARIMAX ROTATION")
print("="*70)

# PCA on V-JEPA2
pca_v = PCA(n_components=100, random_state=42)
vjepa_pcs = pca_v.fit_transform(vjepa)

# Varimax rotation on top K components
for K in [3, 10, 27, 34]:
    print(f"\n--- Varimax on top {K} PCs ---")
    loading_matrix = pca_v.components_[:K].T  # (1408, K)
    rotated_loading, R_mat = varimax(loading_matrix)
    # Rotated scores
    rotated_scores = vjepa_pcs[:, :K] @ R_mat  # (2196, K)

    # Each rotated factor's emotion correlation
    print(f"{'Factor':<10s} {'Top emotion':<25s} {'r':>7s} {'2nd':>20s} {'r':>7s} {'A':>7s} {'V':>7s}")
    print("-"*80)
    for f in range(K):
        corrs = []
        for j in range(34):
            r, _ = spearmanr(rotated_scores[:, f], emotion_scores[:, j])
            corrs.append((j, r))
        corrs.sort(key=lambda x: abs(x[1]), reverse=True)
        top1 = corrs[0]
        top2 = corrs[1]
        r_a, _ = spearmanr(rotated_scores[:, f], arousal)
        r_v, _ = spearmanr(rotated_scores[:, f], valence)
        print(f"F{f+1:<9d} {EMOTION_LABELS[top1[0]]:<25s} {top1[1]:+7.3f} {EMOTION_LABELS[top2[0]]:>20s} {top2[1]:+7.3f} {r_a:+7.3f} {r_v:+7.3f}")

# Brain prediction of rotated factors (K=27, Cowen과 맞추기)
K = 27
loading_matrix = pca_v.components_[:K].T
rotated_loading, R_mat = varimax(loading_matrix)
rotated_scores_27 = vjepa_pcs[:, :K] @ R_mat

print(f"\n--- Brain prediction of 27 rotated factors ---")
r2_rotated_bj = np.zeros(K)
r2_rotated_raw = np.zeros(K)
for f in range(K):
    scores_bj = cross_val_score(model, brain_mean, rotated_scores_27[:, f], cv=5, scoring='r2')
    scores_raw = cross_val_score(model, fmri_mean, rotated_scores_27[:, f], cv=5, scoring='r2')
    r2_rotated_bj[f] = max(scores_bj.mean(), 0.0)
    r2_rotated_raw[f] = max(scores_raw.mean(), 0.0)

# Sort by Brain-JEPA R²
sort_idx = np.argsort(r2_rotated_bj)[::-1]
print(f"\n{'Factor':<8s} {'BJ R²':>8s} {'Raw R²':>8s} {'Top emotion':<25s} {'r':>7s}")
print("-"*60)
for f in sort_idx:
    corrs = [(j, spearmanr(rotated_scores_27[:, f], emotion_scores[:, j])[0]) for j in range(34)]
    corrs.sort(key=lambda x: abs(x[1]), reverse=True)
    print(f"F{f+1:<7d} {r2_rotated_bj[f]:8.4f} {r2_rotated_raw[f]:8.4f} {EMOTION_LABELS[corrs[0][0]]:<25s} {corrs[0][1]:+7.3f}")

print(f"\nBrain-pred rotated factors (BJ R²>0.01): {np.where(r2_rotated_bj > 0.01)[0] + 1}")
print(f"Brain-pred rotated factors (Raw R²>0.01): {np.where(r2_rotated_raw > 0.01)[0] + 1}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("2. EMOTION RATING PCA + VARIMAX (COWEN REPLICATION)")
print("="*70)

# PCA on emotion ratings (Cowen's method)
pca_emo = PCA(n_components=34, random_state=42)
emo_pcs = pca_emo.fit_transform(emotion_scores)
cum_var = np.cumsum(pca_emo.explained_variance_ratio_)

print(f"Emotion PCA variance:")
for i in range(34):
    print(f"  PC{i+1:2d}: {pca_emo.explained_variance_ratio_[i]*100:6.2f}% (cum: {cum_var[i]*100:6.2f}%)")

# Varimax on top 27 emotion PCs (Cowen's number)
emo_loading = pca_emo.components_[:27].T  # (34, 27)
rotated_emo_loading, R_emo = varimax(emo_loading)
rotated_emo_scores = emo_pcs[:, :27] @ R_emo  # (2196, 27)

print(f"\n--- 27 rotated emotion factors (Cowen replication) ---")
print(f"{'Factor':<8s} {'Top loading emotion':<25s} {'Loading':>8s} {'2nd':>20s} {'Loading':>8s}")
print("-"*75)
for f in range(27):
    loadings = rotated_emo_loading[:, f]
    sort_l = np.argsort(np.abs(loadings))[::-1]
    print(f"F{f+1:<7d} {EMOTION_LABELS[sort_l[0]]:<25s} {loadings[sort_l[0]]:+8.3f} "
          f"{EMOTION_LABELS[sort_l[1]]:>20s} {loadings[sort_l[1]]:+8.3f}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("3. COWEN vs OUR CCA: STRUCTURE COMPARISON")
print("="*70)

# Our CCA CC emotion profiles
d_cca = np.load(RES / 'cca_brain_video_results.npz', allow_pickle=True)
corr_cc = d_cca['corr_cc_emo']  # (100, 34)
cc_r = d_cca['cc_r']

# Cowen's rotated emotion factor loading matrix: (34, 27)
# Our CCA CC emotion profile matrix: (27, 34) for top 27 CCs
cca_emo_profile = corr_cc[:27, :]  # (27, 34)
cowen_factor_profile = rotated_emo_loading.T  # (27, 34) from rotation

# RSA between the two: how similar is the emotion structure?
cca_rsm = 1 - squareform(pdist(cca_emo_profile, 'correlation'))
cowen_rsm = 1 - squareform(pdist(cowen_factor_profile, 'correlation'))

triu = np.triu_indices(27, k=1)
r_struct, p_struct = spearmanr(cca_rsm[triu], cowen_rsm[triu])
print(f"\nStructure comparison (RSM of factor profiles):")
print(f"  Spearman r = {r_struct:.4f}, p = {p_struct:.2e}")

# Factor-to-factor matching: for each CCA CC, find closest Cowen factor
print(f"\nCCA CC → Cowen factor matching:")
print(f"{'CC':>4s} {'CC r':>6s} {'CC top emo':>23s} → {'Cowen F':>8s} {'Cowen top emo':>23s} {'Match r':>8s}")
print("-"*80)
for i in range(27):
    # Correlation between CC_i's emotion profile and each Cowen factor's loading
    match_corrs = [np.corrcoef(cca_emo_profile[i], cowen_factor_profile[j])[0,1] for j in range(27)]
    best_j = np.argmax(np.abs(match_corrs))
    cc_top = EMOTION_LABELS[np.argmax(np.abs(cca_emo_profile[i]))]
    cow_top = EMOTION_LABELS[np.argmax(np.abs(cowen_factor_profile[best_j]))]
    print(f"CC{i+1:2d} {cc_r[i]:6.3f} {cc_top:>23s} → F{best_j+1:2d}      {cow_top:>23s} {match_corrs[best_j]:+8.3f}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("4. UMAP / t-SNE VISUALIZATIONS")
print("="*70)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

available = [f.name for f in fm.fontManager.ttflist]
for candidate in ['Helvetica', 'Arial', 'Liberation Sans', 'DejaVu Sans']:
    if candidate in available:
        FONT = candidate; break
plt.rcParams.update({'font.family': FONT, 'font.size': 7, 'pdf.fonttype': 42})

# Try UMAP, fall back to t-SNE
try:
    from umap import UMAP
    has_umap = True
    print("Using UMAP")
except ImportError:
    has_umap = False
    print("UMAP not available, using t-SNE only")

from sklearn.manifold import TSNE

# 4a. Videos in brain-pred subspace (PC1-3), colored by top emotion
print("\n4a. Videos in brain-pred subspace...")
bp_3d = vjepa_pcs[:, :3]  # (2196, 3)

# Assign each video its dominant emotion
dominant_emo = np.argmax(emotion_scores, axis=1)  # (2196,)

# t-SNE on brain-pred subspace
tsne = TSNE(n_components=2, random_state=42, perplexity=30)
bp_2d = tsne.fit_transform(bp_3d)

# Top 8 most frequent dominant emotions for coloring
from collections import Counter
emo_counts = Counter(dominant_emo)
top8_emos = [e for e, _ in emo_counts.most_common(8)]
colors_map = plt.cm.Set2(np.linspace(0, 1, 8))

fig, ax = plt.subplots(1, 1, figsize=(6, 5))
# Plot "other" first in gray
other_mask = ~np.isin(dominant_emo, top8_emos)
ax.scatter(bp_2d[other_mask, 0], bp_2d[other_mask, 1], s=2, c='lightgray', alpha=0.3, label='Other')
for idx, emo_i in enumerate(top8_emos):
    mask = dominant_emo == emo_i
    ax.scatter(bp_2d[mask, 0], bp_2d[mask, 1], s=5, c=[colors_map[idx]], alpha=0.6,
              label=EMOTION_LABELS[emo_i])
ax.legend(fontsize=5, markerscale=2, loc='upper right')
ax.set_title('Videos in brain-pred subspace (t-SNE)\nColored by dominant emotion', fontsize=8)
ax.set_xlabel('t-SNE 1', fontsize=7)
ax.set_ylabel('t-SNE 2', fontsize=7)
fig.savefig(FIG / 'tsne_videos_brainpred.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(FIG / 'tsne_videos_brainpred.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("  Saved tsne_videos_brainpred")

# 4b. 34 emotions as points in brain-pred space
print("\n4b. Emotion map in brain-pred space...")
emo_centroids = np.zeros((34, 3))
for j in range(34):
    weights = emotion_scores[:, j]
    if weights.sum() > 0:
        emo_centroids[j] = np.average(bp_3d, axis=0, weights=weights)

fig, axes = plt.subplots(1, 3, figsize=(12, 4))
pairs = [(0,1,'PC1','PC2'), (0,2,'PC1','PC3'), (1,2,'PC2','PC3')]
for ax, (xi, yi, xn, yn) in zip(axes, pairs):
    ax.scatter(emo_centroids[:, xi], emo_centroids[:, yi], s=30, c='steelblue', zorder=3)
    for j in range(34):
        ax.annotate(EMOTION_LABELS[j], (emo_centroids[j, xi], emo_centroids[j, yi]),
                   fontsize=4, ha='center', va='bottom')
    # Highlight basic 6
    for j in range(34):
        if EMOTION_LABELS[j] in BASIC_6:
            ax.scatter(emo_centroids[j, xi], emo_centroids[j, yi], s=50, c='red', zorder=4, marker='^')
    ax.set_xlabel(xn, fontsize=7)
    ax.set_ylabel(yn, fontsize=7)
    ax.set_title(f'{xn} vs {yn}', fontsize=8)
plt.suptitle('34 emotions in brain-pred subspace (weighted centroids)\nRed triangles = 6 basic emotions', fontsize=9)
plt.tight_layout()
fig.savefig(FIG / 'emotion_map_brainpred.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(FIG / 'emotion_map_brainpred.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("  Saved emotion_map_brainpred")

# 4c. Videos in CCA space (CC1-CC3)
print("\n4c. Videos in CCA space...")
d_cca = np.load(RES / 'cca_brain_video_results.npz', allow_pickle=True)
video_cc = d_cca['video_cc']  # (2196, 100)
cca_3d = video_cc[:, :3]

tsne_cca = TSNE(n_components=2, random_state=42, perplexity=30)
cca_2d = tsne_cca.fit_transform(cca_3d)

fig, ax = plt.subplots(1, 1, figsize=(6, 5))
other_mask = ~np.isin(dominant_emo, top8_emos)
ax.scatter(cca_2d[other_mask, 0], cca_2d[other_mask, 1], s=2, c='lightgray', alpha=0.3, label='Other')
for idx, emo_i in enumerate(top8_emos):
    mask = dominant_emo == emo_i
    ax.scatter(cca_2d[mask, 0], cca_2d[mask, 1], s=5, c=[colors_map[idx]], alpha=0.6,
              label=EMOTION_LABELS[emo_i])
ax.legend(fontsize=5, markerscale=2, loc='upper right')
ax.set_title('Videos in CCA shared space (t-SNE of CC1-3)\nColored by dominant emotion', fontsize=8)
ax.set_xlabel('t-SNE 1', fontsize=7)
ax.set_ylabel('t-SNE 2', fontsize=7)
fig.savefig(FIG / 'tsne_videos_cca.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(FIG / 'tsne_videos_cca.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("  Saved tsne_videos_cca")

# 4d. Full V-JEPA2 space vs brain-pred subspace (t-SNE comparison)
print("\n4d. Full V-JEPA2 vs brain-pred t-SNE comparison...")
tsne_full = TSNE(n_components=2, random_state=42, perplexity=30)
full_2d = tsne_full.fit_transform(vjepa_pcs[:, :100])

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, emb_2d, title in [(axes[0], bp_2d, 'Brain-pred subspace (PC1-3)'),
                            (axes[1], full_2d, 'Full V-JEPA2 (100 PCs)')]:
    # Color by valence
    sc = ax.scatter(emb_2d[:, 0], emb_2d[:, 1], s=2, c=valence, cmap='RdBu_r',
                   alpha=0.5, vmin=valence.min(), vmax=valence.max())
    plt.colorbar(sc, ax=ax, label='Valence', shrink=0.7)
    ax.set_title(title + '\nColored by Valence', fontsize=8)
    ax.set_xlabel('t-SNE 1', fontsize=7)
    ax.set_ylabel('t-SNE 2', fontsize=7)
plt.tight_layout()
fig.savefig(FIG / 'tsne_brainpred_vs_full_valence.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(FIG / 'tsne_brainpred_vs_full_valence.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("  Saved tsne_brainpred_vs_full_valence")

# 4e. Emotion similarity heatmap (brain-pred vs behavior)
print("\n4e. Emotion RSM comparison...")
# Brain-pred space RSM
bp_emo_rsm = 1 - squareform(pdist(emo_centroids, 'cosine'))
# Behavior RSM
behav_rsm = np.corrcoef(emotion_scores.T)

fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
for ax, rsm, title in [(axes[0], bp_emo_rsm, 'Brain-pred subspace'),
                        (axes[1], behav_rsm, 'Behavioral ratings')]:
    im = ax.imshow(rsm, cmap='RdBu_r', vmin=-1, vmax=1, interpolation='nearest')
    ax.set_xticks(range(34))
    ax.set_xticklabels(EMOTION_LABELS, rotation=90, fontsize=4)
    ax.set_yticks(range(34))
    ax.set_yticklabels(EMOTION_LABELS, fontsize=4)
    ax.set_title(title, fontsize=8)
    plt.colorbar(im, ax=ax, shrink=0.7)

triu_idx = np.triu_indices(34, k=1)
r_rsm, p_rsm = spearmanr(bp_emo_rsm[triu_idx], behav_rsm[triu_idx])
plt.suptitle(f'Emotion RSM: brain-pred vs behavioral (Mantel r={r_rsm:.3f}, p={p_rsm:.2e})', fontsize=9)
plt.tight_layout()
fig.savefig(FIG / 'emotion_rsm_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(FIG / 'emotion_rsm_comparison.pdf', bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f"  Mantel (brain-pred RSM vs behavior RSM): r={r_rsm:.4f}, p={p_rsm:.2e}")

# ═════════════════════════════════════════════════════════════════════════════
# SAVE
# ═════════════════════════════════════════════════════════════════════════════
print("\nSaving results...")
np.savez(OUT / 'rotation_umap_cowen.npz',
    # Rotated factors (K=27)
    rotated_scores_27=rotated_scores_27,
    r2_rotated_bj=r2_rotated_bj,
    r2_rotated_raw=r2_rotated_raw,
    # Cowen replication
    rotated_emo_loading=rotated_emo_loading,
    rotated_emo_scores=rotated_emo_scores,
    emo_pca_var=pca_emo.explained_variance_ratio_,
    # CCA-Cowen comparison
    r_structure_match=r_struct,
    p_structure_match=p_struct,
    # Emotion RSM comparison
    bp_emo_rsm=bp_emo_rsm,
    behav_rsm=behav_rsm,
    r_rsm_mantel=r_rsm,
    p_rsm_mantel=p_rsm,
    # Emotion centroids
    emo_centroids=emo_centroids,
    # t-SNE embeddings
    tsne_brainpred_2d=bp_2d,
    tsne_cca_2d=cca_2d,
    tsne_full_2d=full_2d,
)
print(f"Saved results + 5 figures")
print("Done.")
