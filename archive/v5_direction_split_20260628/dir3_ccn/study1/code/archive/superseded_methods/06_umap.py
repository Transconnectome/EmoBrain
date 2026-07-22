"""
CCN Analysis 06: Visualization — Brain-JEPA vs V-JEPA2 Emotion Space

Two types of visualization:

[Panel A/B/C] RSM-based 2D embedding (UMAP preferred, MDS fallback)
    Purpose: Show emotional geometry / cluster structure
    Method: UMAP or MDS on distance matrix (1 - RSM)
    Color: dominant emotion per video

[Panel D] Procrustes overlay
    Purpose: Show alignment ERROR between brain and model per video
    Method: PCA on Procrustes-aligned k-dim space → 2D
    Lines connect same video in brain vs V-JEPA2 space
    Line length ∝ alignment error (distance-preserving)

NOTE: t-SNE is NOT used because it distorts distances.
    - RSM panels: UMAP (preserves global+local structure) or MDS (preserves distances)
    - Procrustes overlay: PCA (linear, distance-preserving)

Input:
    cka_results/rsm_brain.npy
    cka_results/rsm_vjepa2.npy
    cka_results/rsm_clip.npy
    CCN/results/procrustes_results.npz
    metadata CSV

Output:
    CCN/figures/emotion_space_3panel.png
    CCN/figures/procrustes_overlay.png
    CCN/results/embedding_2d.npz
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import time

try:
    import umap as umap_lib
    USE_UMAP = True
    print("Using UMAP for RSM visualization")
except ImportError:
    USE_UMAP = False
    print("UMAP not available — using MDS (distance-preserving) for RSM visualization")

# ── Paths ─────────────────────────────────────────────────────────────────────
BRAIN_RSM_PATH  = Path("/pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_brain.npy")
VJEPA2_RSM_PATH = Path("/pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_vjepa2.npy")
CLIP_RSM_PATH   = Path("/pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_clip.npy")
PROC_PATH       = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results/procrustes_results.npz")
META_PATH       = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
OUTPUT_DIR      = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results")
FIG_DIR         = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

EMOTION_LABELS = [
    'Admiration','Adoration','Aesthetic appreciation','Amusement','Anger','Anxiety',
    'Awe','Awkwardness','Boredom','Calmness','Confusion','Contempt','Craving',
    'Disgust','Empathic pain','Entrancement','Excitement','Fear','Horror','Interest',
    'Joy','Nostalgia','Relief','Romance','Sadness','Satisfaction','Sexual desire',
    'Surprise','Sympathy','Triumph','Uncomfortable','Annoyance','Envy','Guilt'
]
N_EMO = 34

_c1 = plt.get_cmap('tab20')
_c2 = plt.get_cmap('tab20b')
COLORS = [_c1(i % 20) if i < 20 else _c2((i - 20) % 20) for i in range(N_EMO)]

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
rsm_brain  = np.load(BRAIN_RSM_PATH).astype(np.float64)
rsm_vjepa2 = np.load(VJEPA2_RSM_PATH).astype(np.float64)
rsm_clip   = np.load(CLIP_RSM_PATH).astype(np.float64)
proc       = np.load(PROC_PATH)

meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

score_mat    = meta[[f"score_{i}" for i in range(N_EMO)]].values
dominant_emo = np.argmax(score_mat, axis=1)   # (2196,)

# ── Distance matrices (for RSM visualization) ─────────────────────────────────
def to_dist(rsm):
    """1 - cosine_similarity → distance. Clip to [0, inf), symmetrize."""
    d = np.clip(1.0 - rsm, 0, None).astype(np.float64)
    np.fill_diagonal(d, 0)
    d = (d + d.T) / 2
    return d

dist_brain  = to_dist(rsm_brain)
dist_vjepa2 = to_dist(rsm_vjepa2)
dist_clip   = to_dist(rsm_clip)

# ── RSM → 2D embedding (UMAP or MDS) ─────────────────────────────────────────
def embed_rsm(dist, name, seed=42):
    """
    UMAP if available (preserves global + local structure).
    MDS fallback (preserves distances, classical metric MDS).
    """
    print(f"  Embedding {name}...")
    t0 = time.time()
    if USE_UMAP:
        emb = umap_lib.UMAP(metric='precomputed', random_state=seed,
                            n_neighbors=15, min_dist=0.1).fit_transform(dist)
    else:
        emb = MDS(n_components=2, dissimilarity='precomputed',
                  random_state=seed, normalized_stress='auto').fit_transform(dist)
    print(f"    done [{time.time()-t0:.0f}s]")
    return emb

print("\nComputing RSM-based 2D embeddings...")
emb_brain  = embed_rsm(dist_brain,  "Brain-JEPA")
emb_vjepa2 = embed_rsm(dist_vjepa2, "V-JEPA2")
emb_clip   = embed_rsm(dist_clip,   "CLIP")

# ── Procrustes overlay → PCA to 2D ────────────────────────────────────────────
# Procrustes already aligned brain_std and vjepa_aligned into the same k-dim space.
# PCA gives a linear 2D projection that preserves relative distances.
print("\nComputing Procrustes overlay (PCA on aligned k-dim space)...")
t0 = time.time()
brain_std     = proc['brain_std']       # (2196, k) — Procrustes-standardized brain
vjepa_aligned = proc['vjepa_aligned']   # (2196, k) — V-JEPA2 rotated to match brain
k_used        = int(proc['k_used'])

# Fit PCA on combined to find common 2D axes
joint = np.vstack([brain_std, vjepa_aligned])   # (4392, k)
pca_2d = PCA(n_components=2)
joint_2d = pca_2d.fit_transform(joint)
emb_overlay_brain = joint_2d[:2196]
emb_overlay_vjepa = joint_2d[2196:]

var_explained = pca_2d.explained_variance_ratio_.sum() * 100
print(f"  PCA 2D variance explained: {var_explained:.1f}%  [{time.time()-t0:.1f}s]")
print(f"  Per-video alignment error range: "
      f"{np.linalg.norm(emb_overlay_brain - emb_overlay_vjepa, axis=1).min():.4f} ~ "
      f"{np.linalg.norm(emb_overlay_brain - emb_overlay_vjepa, axis=1).max():.4f}")

# ── Figure 1: 3-panel RSM visualization ──────────────────────────────────────
method = "UMAP" if USE_UMAP else "MDS"
fig, axes = plt.subplots(1, 3, figsize=(24, 8))
fig.patch.set_facecolor('white')

for ax, emb, title in zip(axes,
    [emb_brain, emb_vjepa2, emb_clip],
    [f'Brain-JEPA\n({method})', f'V-JEPA2\n({method})', f'CLIP\n({method})']):

    for ei in range(N_EMO):
        mask = dominant_emo == ei
        if mask.sum() == 0:
            continue
        ax.scatter(emb[mask, 0], emb[mask, 1],
                   c=[COLORS[ei]], s=6, alpha=0.7, linewidths=0)

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_facecolor('#f5f5f5')
    for sp in ax.spines.values():
        sp.set_visible(False)

legend_handles = [mpatches.Patch(color=COLORS[i], label=EMOTION_LABELS[i])
                  for i in range(N_EMO)]
fig.legend(handles=legend_handles, loc='lower center', ncol=7,
           bbox_to_anchor=(0.5, -0.04), fontsize=7, frameon=False)
plt.suptitle('Emotional Geometry: Neural vs Computational Spaces',
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
fig1_path = FIG_DIR / "emotion_space_3panel.png"
plt.savefig(fig1_path, dpi=200, bbox_inches='tight')
print(f"\nSaved: {fig1_path}")
plt.close()

# ── Figure 2: Procrustes overlay (PCA, distance-preserving) ──────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.patch.set_facecolor('white')

# Left: all videos colored by dominant emotion
ax = axes[0]
for ei in range(N_EMO):
    mask = dominant_emo == ei
    if mask.sum() == 0:
        continue
    ax.scatter(emb_overlay_brain[mask, 0], emb_overlay_brain[mask, 1],
               c=[COLORS[ei]], s=8, alpha=0.5, linewidths=0, marker='o')
    ax.scatter(emb_overlay_vjepa[mask, 0], emb_overlay_vjepa[mask, 1],
               c=[COLORS[ei]], s=8, alpha=0.5, linewidths=0, marker='^')

# Lines connecting same video
np.random.seed(42)
sample = np.random.choice(2196, size=300, replace=False)
for i in sample:
    ax.plot([emb_overlay_brain[i, 0], emb_overlay_vjepa[i, 0]],
            [emb_overlay_brain[i, 1], emb_overlay_vjepa[i, 1]],
            color='gray', alpha=0.12, linewidth=0.5)

mod_handles = [Line2D([0],[0], marker='o', color='w', markerfacecolor='gray',
                      markersize=9, label='Brain-JEPA'),
               Line2D([0],[0], marker='^', color='w', markerfacecolor='gray',
                      markersize=9, label='V-JEPA2')]
ax.legend(handles=mod_handles, fontsize=11, loc='upper right')
ax.set_title(f'Procrustes Overlay (k={k_used}, PCA 2D: {var_explained:.0f}% var)\n'
             f'Line length ∝ alignment error', fontsize=12, fontweight='bold')
ax.set_xticks([]); ax.set_yticks([])
ax.set_facecolor('#f5f5f5')
for sp in ax.spines.values():
    sp.set_visible(False)

# Right: color by alignment error magnitude
ax = axes[1]
errors = np.linalg.norm(emb_overlay_brain - emb_overlay_vjepa, axis=1)  # (2196,)
sc = ax.scatter(emb_overlay_brain[:, 0], emb_overlay_brain[:, 1],
                c=errors, cmap='RdYlGn_r', s=8, alpha=0.7, linewidths=0)
plt.colorbar(sc, ax=ax, label='Alignment error (line length)', shrink=0.8)
ax.set_title(f'Brain-JEPA colored by alignment error\n'
             f'Red = high divergence (Brain Tuning target)', fontsize=12, fontweight='bold')
ax.set_xticks([]); ax.set_yticks([])
ax.set_facecolor('#f5f5f5')
for sp in ax.spines.values():
    sp.set_visible(False)

plt.tight_layout()
fig2_path = FIG_DIR / "procrustes_overlay.png"
plt.savefig(fig2_path, dpi=200, bbox_inches='tight')
print(f"Saved: {fig2_path}")
plt.close()

# ── Save ──────────────────────────────────────────────────────────────────────
np.savez(OUTPUT_DIR / "embedding_2d.npz",
         emb_brain=emb_brain,
         emb_vjepa2=emb_vjepa2,
         emb_clip=emb_clip,
         emb_overlay_brain=emb_overlay_brain,
         emb_overlay_vjepa=emb_overlay_vjepa,
         dominant_emo=dominant_emo,
         emotion_labels=np.array(EMOTION_LABELS),
         pca_var_explained=var_explained)
print(f"Saved: {OUTPUT_DIR}/embedding_2d.npz")
