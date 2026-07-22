"""
CCN Raw fMRI Analysis 08: Raw fMRI k-sweep

Priority 3: Raw fMRI RSM → k sweep (Procrustes + emotion decoding R²)

Motivation:
    Brain-JEPA k-sweep gave max R²_brain=0.06 with k_plateau=34.
    k=25/27 gave identical R²=0.056 (plateau begins at k~25).
    Raw fMRI (450 parcels) may show higher R² and clearer k=27 plateau.

Input:
    /pscratch/sd/s/sjmoon/EmoFM/raw_fmri_results/fmri_raw.npy     (5, 2196, 450)
    /pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy
    /pscratch/sd/s/sjmoon/EmoFM/video_embeddings/clip_embeddings.npy
    metadata CSV

Output:
    CCN/results/raw_k_sweep_results.npz
    CCN/figures/raw_k_sweep.png
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.spatial import procrustes
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

# ── Paths ─────────────────────────────────────────────────────────────────────
FMRI_PATH   = Path("/pscratch/sd/s/sjmoon/EmoFM/raw_fmri_results/fmri_raw.npy")
VJEPA2_PATH = Path("/pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy")
CLIP_PATH   = Path("/pscratch/sd/s/sjmoon/EmoFM/video_embeddings/clip_embeddings.npy")
META_PATH   = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
OUTPUT_DIR  = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results")
FIG_DIR     = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

K_VALUES = [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]

# Brain-JEPA k-sweep reference (from 05_k_sweep results)
BRAINJP_R2 = [0.015627, 0.022599, 0.034557, 0.042842, 0.048828, 0.053734,
              0.056145, 0.056147, 0.056797, 0.058299, 0.058972, 0.060644,
              0.057418, 0.054331]
BRAINJP_DV = [0.931579, 0.938259, 0.942706, 0.940375, 0.935514, 0.937199,
              0.937570, 0.938043, 0.938735, 0.938644, 0.938995, 0.939650,
              0.940351, 0.940627]

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
fmri_raw    = np.load(FMRI_PATH).astype(np.float64)  # (5, 2196, 450)
fmri_mean   = fmri_raw.mean(axis=0)                  # (2196, 450)
vjepa2_emb  = np.load(VJEPA2_PATH).astype(np.float64)
clip_emb    = np.load(CLIP_PATH).astype(np.float64)

meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)
emotion_scores = meta[[f"score_{i}" for i in range(34)]].values.astype(np.float64)  # (2196, 34)

print(f"  fmri_mean:  {fmri_mean.shape}")
print(f"  V-JEPA2:    {vjepa2_emb.shape}")
print(f"  CLIP:       {clip_emb.shape}")

# ── PCA explained variance ────────────────────────────────────────────────────
print("\nPCA explained variance (first 100 components):")
for name, X, maxk in [("Raw fMRI (450)", fmri_mean, 100),
                       ("V-JEPA2 (1408)", vjepa2_emb, 100),
                       ("CLIP (512)",     clip_emb,   100)]:
    pca = PCA(n_components=maxk).fit(X)
    cumvar = np.cumsum(pca.explained_variance_ratio_)
    k80 = int(np.argmax(cumvar >= 0.80)) + 1
    k90 = int(np.argmax(cumvar >= 0.90)) + 1
    k95 = int(np.argmax(cumvar >= 0.95)) + 1
    print(f"  {name}: k@80%={k80}  k@90%={k90}  k@95%={k95}")

# ── Emotion decoding helper ───────────────────────────────────────────────────
def emotion_decoding_r2(X_k):
    pipe = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])
    r2s = []
    for j in range(34):
        r2 = cross_val_score(pipe, X_k, emotion_scores[:, j],
                             cv=5, scoring='r2').mean()
        r2s.append(max(r2, 0.0))
    return float(np.mean(r2s))

# ── k sweep ───────────────────────────────────────────────────────────────────
print(f"\nRunning k sweep: {K_VALUES}")
print(f"{'k':>4}  {'disp_raw_v':>11}  {'disp_raw_c':>11}  "
      f"{'R2_raw':>8}  {'R2_vjepa':>9}  {'R2_clip':>8}  {'R2_raw[JP]':>11}")

disp_raw_vjepa = []
disp_raw_clip  = []
decoding_raw   = []
decoding_vjepa = []
decoding_clip  = []

for idx_k, k in enumerate(K_VALUES):
    t0 = time.time()

    fmri_k  = PCA(n_components=k).fit_transform(fmri_mean)
    vjepa_k = PCA(n_components=k).fit_transform(vjepa2_emb)
    clip_k  = PCA(n_components=k).fit_transform(clip_emb)

    _, _, d_v = procrustes(fmri_k, vjepa_k)
    _, _, d_c = procrustes(fmri_k, clip_k)
    disp_raw_vjepa.append(d_v)
    disp_raw_clip.append(d_c)

    r2_raw = emotion_decoding_r2(fmri_k)
    r2_v   = emotion_decoding_r2(vjepa_k)
    r2_c   = emotion_decoding_r2(clip_k)
    decoding_raw.append(r2_raw)
    decoding_vjepa.append(r2_v)
    decoding_clip.append(r2_c)

    jp_ref = BRAINJP_R2[idx_k]
    print(f"{k:>4}  {d_v:>11.6f}  {d_c:>11.6f}  "
          f"{r2_raw:>8.4f}  {r2_v:>9.4f}  {r2_c:>8.4f}  {jp_ref:>11.4f}  "
          f"[{time.time()-t0:.0f}s]")

disp_raw_vjepa = np.array(disp_raw_vjepa)
disp_raw_clip  = np.array(disp_raw_clip)
decoding_raw   = np.array(decoding_raw)
decoding_vjepa = np.array(decoding_vjepa)
decoding_clip  = np.array(decoding_clip)

# ── Find optimal k ────────────────────────────────────────────────────────────
disp_drops  = -np.diff(disp_raw_vjepa)
elbow_idx   = int(np.argmax(disp_drops))
k_elbow     = K_VALUES[elbow_idx + 1]

r2_max      = decoding_raw.max()
plateau_idx = int(np.argmax(decoding_raw >= 0.95 * r2_max))
k_plateau   = K_VALUES[plateau_idx]

k27_idx = K_VALUES.index(27)

print(f"\n{'='*60}")
print("RAW fMRI k-SWEEP RESULTS")
print(f"{'='*60}")
print(f"  Procrustes elbow:          k = {k_elbow}")
print(f"  Decoding R² plateau:       k = {k_plateau}")
print(f"  Reference (Cowen 2017):    k = 27")
print(f"\n  At k=27:")
print(f"    Procrustes disparity:  raw_v={disp_raw_vjepa[k27_idx]:.4f}  raw_c={disp_raw_clip[k27_idx]:.4f}")
print(f"    R2_raw={decoding_raw[k27_idx]:.4f}  R2_vjepa={decoding_vjepa[k27_idx]:.4f}  R2_clip={decoding_clip[k27_idx]:.4f}")
print(f"    [Brain-JEPA at k=27: R2=0.0561 (92.6% of max 0.0606)]")
print(f"\n  Max R²_raw: {r2_max:.4f} at k={K_VALUES[int(np.argmax(decoding_raw))]}")
print(f"  R²_raw at k=27: {decoding_raw[k27_idx]:.4f} = {decoding_raw[k27_idx]/r2_max*100:.1f}% of max")

print(f"\n  Comparison table (raw fMRI vs Brain-JEPA R²):")
print(f"  {'k':>4}  {'R2_raw':>8}  {'R2_BrainJP':>11}  {'Δ(raw-JP)':>11}")
for idx_k, k in enumerate(K_VALUES):
    delta = decoding_raw[idx_k] - BRAINJP_R2[idx_k]
    print(f"  {k:>4}  {decoding_raw[idx_k]:>8.4f}  {BRAINJP_R2[idx_k]:>11.4f}  {delta:>+11.4f}")

# ── Figure ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 5))
fig.patch.set_facecolor('white')

# Left: Procrustes disparity
ax = axes[0]
ax.plot(K_VALUES, disp_raw_vjepa,     'b-o',  linewidth=2, markersize=6, label='Raw fMRI vs V-JEPA2')
ax.plot(K_VALUES, disp_raw_clip,      'r-o',  linewidth=2, markersize=6, label='Raw fMRI vs CLIP')
ax.plot(K_VALUES, BRAINJP_DV,         'b--s', linewidth=1.5, markersize=5, alpha=0.6, label='Brain-JEPA vs V-JEPA2 (ref)')
ax.axvline(x=27,      color='gray',  linestyle='--', alpha=0.8, linewidth=1.5, label='k=27 (Cowen 2017)')
ax.axvline(x=k_elbow, color='blue',  linestyle=':',  alpha=0.8, linewidth=1.5, label=f'elbow k={k_elbow}')
ax.set_xlabel('Number of dimensions (k)', fontsize=12)
ax.set_ylabel('Procrustes disparity\n(lower = better alignment)', fontsize=12)
ax.set_title('Raw fMRI: Alignment quality vs dimensionality', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Right: Decoding R²
ax = axes[1]
ax.plot(K_VALUES, decoding_raw,    'g-o',  linewidth=2, markersize=6, label='Raw fMRI')
ax.plot(K_VALUES, BRAINJP_R2,      'g--s', linewidth=1.5, markersize=5, alpha=0.6, label='Brain-JEPA (ref)')
ax.plot(K_VALUES, decoding_vjepa,  'b-o',  linewidth=2, markersize=6, label='V-JEPA2')
ax.plot(K_VALUES, decoding_clip,   'r-o',  linewidth=2, markersize=6, label='CLIP')
ax.axvline(x=27,        color='gray',  linestyle='--', alpha=0.8, linewidth=1.5, label='k=27 (Cowen 2017)')
ax.axvline(x=k_plateau, color='green', linestyle=':',  alpha=0.8, linewidth=1.5, label=f'plateau k={k_plateau}')
ax.set_xlabel('Number of dimensions (k)', fontsize=12)
ax.set_ylabel('Emotion decoding R²\n(mean across 34 emotions)', fontsize=12)
ax.set_title('Raw fMRI: Emotion predictability vs dimensionality', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

plt.tight_layout()
fig_path = FIG_DIR / "raw_k_sweep.png"
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
print(f"\nSaved figure: {fig_path}")

# ── Save ──────────────────────────────────────────────────────────────────────
np.savez(OUTPUT_DIR / "raw_k_sweep_results.npz",
         k_values=np.array(K_VALUES),
         disp_raw_vjepa=disp_raw_vjepa,
         disp_raw_clip=disp_raw_clip,
         decoding_raw=decoding_raw,
         decoding_vjepa=decoding_vjepa,
         decoding_clip=decoding_clip,
         k_elbow=k_elbow,
         k_plateau=k_plateau,
         brainjp_r2_ref=np.array(BRAINJP_R2),
         brainjp_disp_ref=np.array(BRAINJP_DV))

print(f"Saved: {OUTPUT_DIR}/raw_k_sweep_results.npz")
