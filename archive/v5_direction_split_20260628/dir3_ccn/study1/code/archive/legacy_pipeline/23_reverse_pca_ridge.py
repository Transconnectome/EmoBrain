"""
Exp 23: Reverse PCA + Ridge — V-JEPA2 → Brain-JEPA PC prediction

Original (Exp 10): Brain(768) → Ridge → V-JEPA2 PC_i
  "뇌가 V-JEPA2의 어떤 축을 읽을 수 있는가?"

Reverse (this):    V-JEPA2(1408) → Ridge → Brain-JEPA PC_j
  "V-JEPA2가 뇌의 어떤 축을 설명할 수 있는가?"

Also includes permutation test (n=1000) + FDR correction.
"""

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.decomposition import PCA
from scipy.stats import spearmanr
import pandas as pd
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
VJEPA_PATH = BASE / "video_embeddings/vjepa2_embeddings.npy"
BRAIN_PATH = BASE / "brain_embeddings/brain_jepa_embeddings.npy"
META_PATH  = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
OUTPUT_DIR = BASE / "CCN2026/results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EMOTION_LABELS = [
    'Admiration', 'Adoration', 'Aesthetic appreciation', 'Amusement', 'Anger',
    'Anxiety', 'Awe', 'Awkwardness', 'Boredom', 'Calmness', 'Confusion',
    'Contempt', 'Craving', 'Disgust', 'Empathic pain', 'Entrancement',
    'Excitement', 'Fear', 'Horror', 'Interest', 'Joy', 'Nostalgia', 'Relief',
    'Romance', 'Sadness', 'Satisfaction', 'Sexual desire', 'Surprise',
    'Sympathy', 'Triumph', 'Uncomfortable', 'Annoyance', 'Envy', 'Guilt'
]

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading data...")
vjepa = np.load(VJEPA_PATH).astype(np.float64)           # (2196, 1408)
brain_raw = np.load(BRAIN_PATH).astype(np.float64)        # (5, 2196, 768)
brain_mean = brain_raw.mean(axis=0)                        # (2196, 768)

meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

score_cols = [f"score_{i}" for i in range(34)]
emotion_scores = meta[score_cols].values.astype(np.float64)  # (2196, 34)
arousal = meta['arousal_score'].values.astype(np.float64)
valence = meta['valence_score'].values.astype(np.float64)

print(f"  V-JEPA2: {vjepa.shape}, Brain mean: {brain_mean.shape}")

# ── Step 1: PCA on Brain-JEPA ────────────────────────────────────────────────
N_PC = 100
print(f"\nFitting PCA on Brain-JEPA ({N_PC} components)...")
pca_brain = PCA(n_components=N_PC, random_state=42)
brain_pcs = pca_brain.fit_transform(brain_mean)  # (2196, 100)
print(f"  Explained variance (sum): {pca_brain.explained_variance_ratio_.sum():.4f}")
print(f"  Top 10: {pca_brain.explained_variance_ratio_[:10].round(4)}")

# ── Step 2: V-JEPA2 → Brain PC_j prediction (Ridge, 5-fold CV) ───────────────
print(f"\nPredicting each Brain PC from V-JEPA2 (Ridge, 5-fold CV)...")
model = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

r2_obs = np.zeros(N_PC)
mse_obs = np.zeros(N_PC)

for i in range(N_PC):
    scores_r2 = cross_val_score(model, vjepa, brain_pcs[:, i], cv=5, scoring='r2')
    scores_mse = cross_val_score(model, vjepa, brain_pcs[:, i], cv=5, scoring='neg_mean_squared_error')
    r2_obs[i] = max(scores_r2.mean(), 0.0)
    mse_obs[i] = -scores_mse.mean()
    if (i + 1) % 10 == 0 or i < 5:
        print(f"  Brain PC{i+1}: R²={r2_obs[i]:.4f}, MSE={mse_obs[i]:.4f}")

print(f"\nNon-zero R² PCs: {np.where(r2_obs > 0)[0] + 1}")
print(f"R² > 0.01 PCs: {np.where(r2_obs > 0.01)[0] + 1}")

# ── Step 3: Permutation test ─────────────────────────────────────────────────
N_PERM = 1000
rng = np.random.default_rng(42)

nonzero_pcs = np.where(r2_obs > 0)[0]
n_test = len(nonzero_pcs)
print(f"\nRunning {N_PERM} permutations for {n_test} PCs with R² > 0...")

r2_null = np.zeros((N_PC, N_PERM))
p_values = np.ones(N_PC)

for idx, i in enumerate(nonzero_pcs):
    target = brain_pcs[:, i]
    for p in range(N_PERM):
        target_perm = rng.permutation(target)
        null_score = cross_val_score(model, vjepa, target_perm, cv=5, scoring='r2')
        r2_null[i, p] = max(null_score.mean(), 0.0)
    p_values[i] = np.mean(r2_null[i] >= r2_obs[i])
    print(f"  [{idx+1}/{n_test}] Brain PC{i+1}: obs R²={r2_obs[i]:.4f}, "
          f"p={p_values[i]:.4f} (null mean={r2_null[i].mean():.4f}, max={r2_null[i].max():.4f})")

# ── FDR correction ────────────────────────────────────────────────────────────
def fdr_bh(pvals):
    n = len(pvals)
    order = np.argsort(pvals)
    adj = pvals[order] * n / (np.arange(1, n + 1))
    for j in range(n - 2, -1, -1):
        adj[j] = min(adj[j], adj[j + 1])
    adj = np.clip(adj, 0, 1)
    result = np.empty(n)
    result[order] = adj
    return result

p_corrected = fdr_bh(p_values)
sig_mask = p_corrected < 0.05
n_sig = sig_mask.sum()

print(f"\n{'='*60}")
print(f"REVERSE DIRECTION: V-JEPA2 → Brain-JEPA PC")
print(f"Brain-predictable PCs (FDR q < 0.05): {n_sig}")
print(f"{'='*60}")
sig_pcs = np.where(sig_mask)[0]
for i in sig_pcs:
    var_exp = pca_brain.explained_variance_ratio_[i] * 100
    print(f"  Brain PC{i+1}: R²={r2_obs[i]:.4f}, p={p_values[i]:.4f}, "
          f"q={p_corrected[i]:.4f}, var={var_exp:.2f}%")

# ── Step 4: Emotion correlation of Brain PCs ─────────────────────────────────
print(f"\nComputing emotion correlations for Brain PCs...")
corr_brain_emo = np.zeros((N_PC, 34))
for i in range(N_PC):
    for j in range(34):
        r, _ = spearmanr(brain_pcs[:, i], emotion_scores[:, j])
        corr_brain_emo[i, j] = r

corr_brain_av = np.zeros((N_PC, 2))
for i in range(N_PC):
    corr_brain_av[i, 0], _ = spearmanr(brain_pcs[:, i], arousal)
    corr_brain_av[i, 1], _ = spearmanr(brain_pcs[:, i], valence)

max_r_per_pc = np.max(np.abs(corr_brain_emo), axis=1)

print("\nBrain PCs predicted by V-JEPA2 — emotion profiles:")
for i in sig_pcs[:15]:
    top3_idx = np.argsort(np.abs(corr_brain_emo[i]))[-3:][::-1]
    top3 = [(EMOTION_LABELS[j], f"{corr_brain_emo[i,j]:+.3f}") for j in top3_idx]
    print(f"  Brain PC{i+1}: R²={r2_obs[i]:.4f}, max|r|={max_r_per_pc[i]:.3f}, "
          f"A={corr_brain_av[i,0]:+.3f}, V={corr_brain_av[i,1]:+.3f}, top3={top3}")

# ── Step 5: Emotion decoding from V-JEPA2-predictable Brain subspace ──────────
print(f"\n{'='*60}")
print("EMOTION DECODING FROM V-JEPA2-PREDICTABLE BRAIN SUBSPACE")
print(f"{'='*60}")

targets = np.hstack([emotion_scores, arousal[:, None], valence[:, None]])
target_names = EMOTION_LABELS + ['Arousal', 'Valence']

feature_sets = {}
if n_sig > 0:
    feature_sets['Brain-pred-by-Video (sig)'] = brain_pcs[:, sig_mask]
feature_sets['Brain PC1-3'] = brain_pcs[:, :3]
feature_sets['Brain PC1-10'] = brain_pcs[:, :10]
feature_sets['Brain all 100'] = brain_pcs[:, :100]

r2_results = {}
for feat_name, X in feature_sets.items():
    r2_vals = np.zeros(36)
    for t in range(36):
        scores = cross_val_score(model, X, targets[:, t], cv=5, scoring='r2')
        r2_vals[t] = max(scores.mean(), 0.0)
    r2_results[feat_name] = r2_vals
    cat_mean = r2_vals[:34].mean()
    av_mean = r2_vals[34:].mean()
    ratio = cat_mean / max(av_mean, 1e-10)
    print(f"  {feat_name} ({X.shape[1]} dims): cat R²={cat_mean:.4f}, AV R²={av_mean:.4f}, ratio={ratio:.3f}")

# ── Step 6: Compare with forward direction ────────────────────────────────────
print(f"\n{'='*60}")
print("COMPARISON: FORWARD vs REVERSE")
print(f"{'='*60}")

# Load forward results
d_fwd = np.load(OUTPUT_DIR / 'brain_predictable_dims.npz', allow_pickle=True)
r2_fwd = d_fwd['r2_vjepa_per_dim']  # Brain → V-JEPA2 PC

print(f"\n  Forward (Brain → V-JEPA2 PC):")
print(f"    Significant PCs: {np.where(r2_fwd > 0.01)[0] + 1}")
print(f"    R² values: {r2_fwd[r2_fwd > 0.01].round(4)}")

print(f"\n  Reverse (V-JEPA2 → Brain PC):")
print(f"    Significant PCs: {sig_pcs + 1}")
print(f"    R² values: {r2_obs[sig_mask].round(4)}")

# ── Save ──────────────────────────────────────────────────────────────────────
print("\nSaving results...")
save_dict = {
    'r2_obs': r2_obs,
    'mse_obs': mse_obs,
    'r2_null': r2_null,
    'p_values': p_values,
    'p_corrected': p_corrected,
    'sig_mask': sig_mask,
    'brain_pca_var_ratio': pca_brain.explained_variance_ratio_,
    'corr_brain_emo': corr_brain_emo,
    'corr_brain_av': corr_brain_av,
    'max_r_per_pc': max_r_per_pc,
    'emotion_labels': np.array(EMOTION_LABELS),
    'n_perm': N_PERM,
}
for k, v in r2_results.items():
    safe_key = k.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
    save_dict[f'r2_decode_{safe_key}'] = v

np.savez(OUTPUT_DIR / 'exp23_reverse_pca_ridge.npz', **save_dict)
print(f"Saved → {OUTPUT_DIR}/exp23_reverse_pca_ridge.npz")
print("\nDone.")
