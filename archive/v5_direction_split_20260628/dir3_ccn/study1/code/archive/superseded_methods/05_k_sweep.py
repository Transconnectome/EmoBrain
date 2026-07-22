"""
CCN Analysis 05: Optimal Dimensionality — k Sweep

Purpose:
    Find optimal k where Brain-JEPA and V-JEPA2 spaces best converge.

    Two criteria:
        1. Procrustes disparity elbow (biggest drop)
        2. Emotion decoding R² plateau

    If optimal k ≈ 27:
        Behavioral (Cowen 2017) + Neural (Horikawa 2020) + Computational (ours)
        → emotion space is universally ~27-dimensional

Input:
    brain_embeddings/brain_jepa_embeddings.npy  (5, 2196, 768)
    video_embeddings/vjepa2_embeddings.npy
    video_embeddings/clip_embeddings.npy
    metadata CSV

Output:
    CCN/results/k_sweep_results.npz
    CCN/figures/k_sweep.png
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.spatial import procrustes
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

# ── Paths ─────────────────────────────────────────────────────────────────────
BRAIN_EMB_PATH = Path("/pscratch/sd/s/sjmoon/EmoFM/brain_embeddings/brain_jepa_embeddings.npy")
VJEPA2_PATH    = Path("/pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy")
CLIP_PATH      = Path("/pscratch/sd/s/sjmoon/EmoFM/video_embeddings/clip_embeddings.npy")
META_PATH      = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
OUTPUT_DIR     = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results")
FIG_DIR        = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

K_VALUES = [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading data...")
brain_emb  = np.load(BRAIN_EMB_PATH).astype(np.float64)
brain_mean = brain_emb.mean(axis=0)   # (2196, 768)
vjepa2_emb = np.load(VJEPA2_PATH).astype(np.float64)
clip_emb   = np.load(CLIP_PATH).astype(np.float64)

meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)
emotion_scores = meta[[f"score_{i}" for i in range(34)]].values.astype(np.float64)  # (2196, 34)

print(f"  Brain-JEPA mean: {brain_mean.shape}")
print(f"  V-JEPA2:         {vjepa2_emb.shape}")
print(f"  CLIP:            {clip_emb.shape}")

# ── PCA explained variance (reference) ────────────────────────────────────────
print("\nPCA explained variance:")
for name, X, maxk in [("Brain-JEPA(768)", brain_mean, 100),
                       ("V-JEPA2(1408)",  vjepa2_emb, 100),
                       ("CLIP(512)",      clip_emb,   100)]:
    pca = PCA(n_components=maxk)
    pca.fit(X)
    cumvar = np.cumsum(pca.explained_variance_ratio_)
    k80 = int(np.argmax(cumvar >= 0.80)) + 1
    k90 = int(np.argmax(cumvar >= 0.90)) + 1
    k95 = int(np.argmax(cumvar >= 0.95)) + 1
    print(f"  {name}: k@80%={k80}  k@90%={k90}  k@95%={k95}")

# ── k sweep ───────────────────────────────────────────────────────────────────
print(f"\nRunning k sweep: {K_VALUES}")

disparity_vjepa    = []
disparity_clip     = []
decoding_brain     = []
decoding_vjepa     = []
decoding_clip      = []

def emotion_decoding_r2(X_k):
    # Use Pipeline to prevent data leakage (scaler fit only on train fold)
    from sklearn.pipeline import Pipeline
    pipe = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])
    r2s = []
    for j in range(34):
        r2 = cross_val_score(pipe, X_k, emotion_scores[:, j],
                             cv=5, scoring='r2').mean()
        r2s.append(max(r2, 0.0))
    return float(np.mean(r2s))

for k in K_VALUES:
    t0 = time.time()

    brain_k = PCA(n_components=k).fit_transform(brain_mean)
    vjepa_k = PCA(n_components=k).fit_transform(vjepa2_emb)
    clip_k  = PCA(n_components=k).fit_transform(clip_emb)

    _, _, d_v = procrustes(brain_k, vjepa_k)
    _, _, d_c = procrustes(brain_k, clip_k)
    disparity_vjepa.append(d_v)
    disparity_clip.append(d_c)

    r2_b = emotion_decoding_r2(brain_k)
    r2_v = emotion_decoding_r2(vjepa_k)
    r2_c = emotion_decoding_r2(clip_k)
    decoding_brain.append(r2_b)
    decoding_vjepa.append(r2_v)
    decoding_clip.append(r2_c)

    print(f"  k={k:3d}  disp_v={d_v:.4f}  disp_c={d_c:.4f}  "
          f"R²_brain={r2_b:.4f}  R²_vjepa={r2_v:.4f}  R²_clip={r2_c:.4f}  "
          f"[{time.time()-t0:.0f}s]")

disparity_vjepa = np.array(disparity_vjepa)
disparity_clip  = np.array(disparity_clip)
decoding_brain  = np.array(decoding_brain)
decoding_vjepa  = np.array(decoding_vjepa)
decoding_clip   = np.array(decoding_clip)

# ── Find optimal k ────────────────────────────────────────────────────────────
# Elbow: largest drop in disparity
disp_drops = -np.diff(disparity_vjepa)
elbow_idx  = int(np.argmax(disp_drops))
k_elbow    = K_VALUES[elbow_idx + 1]

# Plateau: first k where R² >= 95% of max
r2_max      = decoding_brain.max()
plateau_idx = int(np.argmax(decoding_brain >= 0.95 * r2_max))
k_plateau   = K_VALUES[plateau_idx]

k27_idx = K_VALUES.index(27)

print(f"\n{'='*60}")
print(f"OPTIMAL k RESULTS")
print(f"{'='*60}")
print(f"  Procrustes elbow:          k = {k_elbow}")
print(f"  Decoding plateau (Brain):  k = {k_plateau}")
print(f"  Reference (Cowen 2017):    k = 27")
print(f"\n  At k=27:")
print(f"    Procrustes disparity: V-JEPA2={disparity_vjepa[k27_idx]:.4f}  CLIP={disparity_clip[k27_idx]:.4f}")
print(f"    Decoding R²:  Brain={decoding_brain[k27_idx]:.4f}  "
      f"V-JEPA2={decoding_vjepa[k27_idx]:.4f}  CLIP={decoding_clip[k27_idx]:.4f}")

if abs(k_elbow - 27) <= 5 or abs(k_plateau - 27) <= 5:
    print(f"\n  *** Scenario A/B: optimal k ≈ 27 — converges with Cowen (2017)! ***")
else:
    print(f"\n  Scenario C: optimal k ({k_elbow}) differs from 27 — interesting finding!")

# ── Figure ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor('white')

ax = axes[0]
ax.plot(K_VALUES, disparity_vjepa, 'b-o', linewidth=2, markersize=6, label='Brain vs V-JEPA2')
ax.plot(K_VALUES, disparity_clip,  'r-o', linewidth=2, markersize=6, label='Brain vs CLIP')
ax.axvline(x=27,       color='gray',  linestyle='--', alpha=0.8, linewidth=1.5, label='k=27 (Cowen 2017)')
ax.axvline(x=k_elbow,  color='blue',  linestyle=':',  alpha=0.8, linewidth=1.5, label=f'elbow k={k_elbow}')
ax.set_xlabel('Number of dimensions (k)', fontsize=12)
ax.set_ylabel('Procrustes disparity\n(lower = better alignment)', fontsize=12)
ax.set_title('Alignment quality vs dimensionality', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(alpha=0.3)

ax = axes[1]
ax.plot(K_VALUES, decoding_brain, 'g-o', linewidth=2, markersize=6, label='Brain-JEPA')
ax.plot(K_VALUES, decoding_vjepa, 'b-o', linewidth=2, markersize=6, label='V-JEPA2')
ax.plot(K_VALUES, decoding_clip,  'r-o', linewidth=2, markersize=6, label='CLIP')
ax.axvline(x=27,        color='gray', linestyle='--', alpha=0.8, linewidth=1.5, label='k=27 (Cowen 2017)')
ax.axvline(x=k_plateau, color='green', linestyle=':', alpha=0.8, linewidth=1.5, label=f'plateau k={k_plateau}')
ax.set_xlabel('Number of dimensions (k)', fontsize=12)
ax.set_ylabel('Emotion decoding R²\n(mean across 34 emotions)', fontsize=12)
ax.set_title('Emotion predictability vs dimensionality', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(alpha=0.3)

plt.tight_layout()
fig_path = FIG_DIR / "k_sweep.png"
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
print(f"\nSaved figure: {fig_path}")

# ── Save ──────────────────────────────────────────────────────────────────────
np.savez(OUTPUT_DIR / "k_sweep_results.npz",
         k_values=np.array(K_VALUES),
         disparity_vjepa=disparity_vjepa,
         disparity_clip=disparity_clip,
         decoding_brain=decoding_brain,
         decoding_vjepa=decoding_vjepa,
         decoding_clip=decoding_clip,
         k_elbow=k_elbow,
         k_plateau=k_plateau)

print(f"Saved: {OUTPUT_DIR}/k_sweep_results.npz")
print(f"\nNOTE: If k_elbow or k_plateau differs from k=27 used in 03_procrustes.py,")
print(f"      re-run 03_procrustes.py (it will auto-load optimal k).")
