"""
CCN Raw fMRI Analysis 09: Raw fMRI visualization
    — MDS of raw fMRI RSM + Procrustes overlay (raw fMRI vs V-JEPA2)

Priority 4: Update UMAP/MDS visualization using raw fMRI RSM

Requires: 07_raw_rsm_rsa_cka.py to have been run first (raw_rsm_mean.npy)

Input:
    CCN/results/raw_rsm_mean.npy           (2196, 2196)
    /pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_vjepa2.npy
    /pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_clip.npy
    /pscratch/sd/s/sjmoon/EmoFM/raw_fmri_results/fmri_raw.npy    (5, 2196, 450)
    /pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy
    metadata CSV

Output:
    CCN/figures/raw_emotion_space_3panel.png   — MDS of raw/vjepa/clip RSMs
    CCN/figures/raw_procrustes_overlay.png     — Procrustes overlay (PCA 2D)
    CCN/results/raw_embedding_2d.npz
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.spatial import procrustes
from sklearn.decomposition import PCA
from sklearn.manifold import MDS
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import time

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW_RSM_PATH   = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results/raw_rsm_mean.npy")
VJEPA2_RSM_PATH = Path("/pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_vjepa2.npy")
CLIP_RSM_PATH   = Path("/pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_clip.npy")
FMRI_PATH      = Path("/pscratch/sd/s/sjmoon/EmoFM/raw_fmri_results/fmri_raw.npy")
VJEPA2_EMB_PATH = Path("/pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy")
META_PATH      = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
OUTPUT_DIR     = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results")
FIG_DIR        = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

EMOTION_LABELS = [
    'Admiration','Adoration','Aesthetic appreciation','Amusement','Anger','Anxiety',
    'Awe','Awkwardness','Boredom','Calmness','Confusion','Contempt','Craving',
    'Disgust','Empathic pain','Entrancement','Excitement','Fear','Horror','Interest',
    'Joy','Nostalgia','Relief','Romance','Sadness','Satisfaction','Sexual desire',
    'Surprise','Sympathy','Triumph','Uncomfortable','Annoyance','Envy','Guilt'
]
N       = 2196
K_PROC  = 27    # Procrustes overlay dimension (consistent with main analyses)
SEED    = 42

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
rsm_raw    = np.load(RAW_RSM_PATH).astype(np.float64)
rsm_vjepa2 = np.load(VJEPA2_RSM_PATH).astype(np.float64)
rsm_clip   = np.load(CLIP_RSM_PATH).astype(np.float64)
fmri_raw   = np.load(FMRI_PATH).astype(np.float64)
fmri_mean  = fmri_raw.mean(axis=0)      # (2196, 450)
vjepa2_emb = np.load(VJEPA2_EMB_PATH).astype(np.float64)

meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

# Dominant emotion per video (highest score)
emotion_scores = meta[[f"score_{i}" for i in range(34)]].values
dominant_emo   = emotion_scores.argmax(axis=1)   # (2196,)

print(f"  rsm_raw:   {rsm_raw.shape}  std={rsm_raw.std():.4f}")
print(f"  rsm_vjepa2: {rsm_vjepa2.shape}")
print(f"  fmri_mean: {fmri_mean.shape}")
print(f"  vjepa2_emb: {vjepa2_emb.shape}")

# ── RSM → distance matrix → MDS 2D ───────────────────────────────────────────
def rsm_to_mds(rsm, label, seed=SEED):
    t0 = time.time()
    # clip to [0,1] and convert to distance
    rsm_clipped = np.clip(rsm, 0, 1)
    dist = 1.0 - rsm_clipped
    np.fill_diagonal(dist, 0.0)
    mds = MDS(n_components=2, metric=True, dissimilarity='precomputed',
              n_init=4, random_state=seed, normalized_stress='auto', max_iter=500)
    emb = mds.fit_transform(dist).astype(np.float32)
    print(f"  MDS {label}: stress={mds.stress_:.4f}  [{time.time()-t0:.0f}s]")
    return emb

print("\nComputing MDS embeddings (may take a few minutes each)...")
emb_raw    = rsm_to_mds(rsm_raw,    "Raw fMRI")
emb_vjepa2 = rsm_to_mds(rsm_vjepa2, "V-JEPA2")
emb_clip   = rsm_to_mds(rsm_clip,   "CLIP")

# ── Procrustes overlay (raw fMRI vs V-JEPA2, k-dim PCA) ───────────────────────
print(f"\nComputing Procrustes overlay (k={K_PROC})...")
t0 = time.time()
fmri_k  = PCA(n_components=K_PROC).fit_transform(fmri_mean)
vjepa_k = PCA(n_components=K_PROC).fit_transform(vjepa2_emb)
_, vjepa_aligned, disparity = procrustes(fmri_k, vjepa_k)
print(f"  Procrustes disparity (raw fMRI vs V-JEPA2): {disparity:.6f}")

# PCA on joint for distance-preserving 2D overlay
joint    = np.vstack([fmri_k, vjepa_aligned])   # (4392, K_PROC)
pca_2d   = PCA(n_components=2)
joint_2d = pca_2d.fit_transform(joint)
emb_overlay_raw   = joint_2d[:N]
emb_overlay_vjepa = joint_2d[N:]
var_explained = pca_2d.explained_variance_ratio_.sum() * 100
print(f"  Procrustes overlay PCA 2D: {var_explained:.1f}% var explained  [{time.time()-t0:.1f}s]")

# Per-video alignment error in 2D projection
overlay_errors = np.linalg.norm(emb_overlay_raw - emb_overlay_vjepa, axis=1)
print(f"  Overlay error: min={overlay_errors.min():.4f}  max={overlay_errors.max():.4f}  "
      f"mean={overlay_errors.mean():.4f}  std={overlay_errors.std():.4f}")

# ── Figure 1: 3-panel MDS (Raw fMRI / V-JEPA2 / CLIP) ─────────────────────────
print("\nGenerating 3-panel MDS figure...")
fig, axes = plt.subplots(1, 3, figsize=(24, 8))
fig.patch.set_facecolor('white')
colors = cm.tab20(np.linspace(0, 1, 34))

for ax, emb, title in zip(axes,
                           [emb_raw, emb_vjepa2, emb_clip],
                           ['Raw fMRI (MDS)', 'V-JEPA2 (MDS)', 'CLIP (MDS)']):
    for emo_idx in range(34):
        mask = dominant_emo == emo_idx
        if mask.sum() == 0:
            continue
        ax.scatter(emb[mask, 0], emb[mask, 1],
                   c=[colors[emo_idx]], s=6, alpha=0.6, label=EMOTION_LABELS[emo_idx])
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_xlabel('MDS dim 1', fontsize=11)
    ax.set_ylabel('MDS dim 2', fontsize=11)
    ax.grid(alpha=0.2)

# Shared legend (right panel only)
axes[2].legend(loc='upper right', fontsize=6, markerscale=2,
               ncol=2, framealpha=0.8)
plt.suptitle('Neural & Computational Emotion Spaces (Raw fMRI)', fontsize=15, fontweight='bold', y=1.01)
plt.tight_layout()
fig1_path = FIG_DIR / "raw_emotion_space_3panel.png"
plt.savefig(fig1_path, dpi=200, bbox_inches='tight')
print(f"  Saved: {fig1_path}")
plt.close()

# ── Figure 2: Procrustes overlay (colored by emotion / by error) ───────────────
print("Generating Procrustes overlay figure...")
fig, axes = plt.subplots(1, 2, figsize=(20, 8))
fig.patch.set_facecolor('white')

# Panel 1: colored by dominant emotion + connection lines
ax = axes[0]
for emo_idx in range(34):
    mask = (dominant_emo == emo_idx)
    if mask.sum() == 0:
        continue
    ax.scatter(emb_overlay_raw[mask, 0],   emb_overlay_raw[mask, 1],
               c=[colors[emo_idx]], s=10, alpha=0.7, marker='o')
    ax.scatter(emb_overlay_vjepa[mask, 0], emb_overlay_vjepa[mask, 1],
               c=[colors[emo_idx]], s=10, alpha=0.4, marker='^')

# Draw connection lines (subsample for clarity)
step = max(1, N // 300)
for i in range(0, N, step):
    ax.plot([emb_overlay_raw[i, 0], emb_overlay_vjepa[i, 0]],
            [emb_overlay_raw[i, 1], emb_overlay_vjepa[i, 1]],
            'k-', alpha=0.08, linewidth=0.5)
ax.set_title(f'Procrustes Overlay — Raw fMRI (●) vs V-JEPA2 (▲)\n'
             f'k={K_PROC}, PCA 2D ({var_explained:.0f}% var), disparity={disparity:.4f}',
             fontsize=12, fontweight='bold')
ax.set_xlabel('PCA dim 1', fontsize=11)
ax.set_ylabel('PCA dim 2', fontsize=11)
ax.grid(alpha=0.2)

# Panel 2: colored by alignment error magnitude
ax = axes[1]
vmin, vmax = np.percentile(overlay_errors, [5, 95])
sc = ax.scatter(emb_overlay_raw[:, 0], emb_overlay_raw[:, 1],
                c=overlay_errors, cmap='RdYlGn_r', s=8, alpha=0.8,
                vmin=vmin, vmax=vmax)
plt.colorbar(sc, ax=ax, label='Alignment error (L2 in 2D)')
ax.set_title('Alignment Error: High=red (brain-model divergence), Low=green',
             fontsize=12, fontweight='bold')
ax.set_xlabel('PCA dim 1', fontsize=11)
ax.set_ylabel('PCA dim 2', fontsize=11)
ax.grid(alpha=0.2)

plt.tight_layout()
fig2_path = FIG_DIR / "raw_procrustes_overlay.png"
plt.savefig(fig2_path, dpi=200, bbox_inches='tight')
print(f"  Saved: {fig2_path}")
plt.close()

# ── Save ──────────────────────────────────────────────────────────────────────
np.savez(OUTPUT_DIR / "raw_embedding_2d.npz",
         emb_raw=emb_raw,
         emb_vjepa2=emb_vjepa2,
         emb_clip=emb_clip,
         emb_overlay_raw=emb_overlay_raw,
         emb_overlay_vjepa=emb_overlay_vjepa,
         overlay_errors=overlay_errors,
         dominant_emo=dominant_emo,
         emotion_labels=np.array(EMOTION_LABELS),
         procrustes_disparity=disparity,
         pca_var_explained=var_explained)

print(f"Saved: {OUTPUT_DIR}/raw_embedding_2d.npz")
print("\nDone.")
