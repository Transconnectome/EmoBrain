"""
Exp 21: CCA between Brain-JEPA and V-JEPA2
Find shared representational axes, then test emotion correlation.

Pipeline:
  1. PCA dimensionality reduction (both sides)
  2. CCA: Brain-JEPA ↔ V-JEPA2
  3. Permutation test for significant CCs
  4. Emotion correlation of canonical variates
  5. Category vs V-A analysis on CCA subspace
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.cross_decomposition import CCA
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from scipy.stats import spearmanr
import warnings
warnings.filterwarnings('ignore')

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
VJEPA_PATH = BASE / "video_embeddings/vjepa2_embeddings.npy"
BRAIN_PATH = BASE / "brain_embeddings/brain_jepa_embeddings.npy"
META_PATH  = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
OUTPUT_DIR = BASE / "CCN2026/results"
FIG_DIR    = BASE / "CCN2026/figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

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

print(f"  V-JEPA2: {vjepa.shape}, Brain-JEPA mean: {brain_mean.shape}")
print(f"  Emotion scores: {emotion_scores.shape}")

# ── Step 1: PCA reduction ────────────────────────────────────────────────────
# Reduce dimensionality to stabilize CCA
N_PCA = 100  # both sides → 100 dims (consistent with PCA+Ridge analysis)
print(f"\nPCA reduction to {N_PCA} dims (both sides)...")

scaler_v = StandardScaler()
scaler_b = StandardScaler()

vjepa_s = scaler_v.fit_transform(vjepa)
brain_s = scaler_b.fit_transform(brain_mean)

pca_v = PCA(n_components=N_PCA, random_state=42)
pca_b = PCA(n_components=N_PCA, random_state=42)

vjepa_pca = pca_v.fit_transform(vjepa_s)    # (2196, 50)
brain_pca = pca_b.fit_transform(brain_s)    # (2196, 50)

print(f"  V-JEPA2 PCA var explained: {pca_v.explained_variance_ratio_.sum():.3f}")
print(f"  Brain-JEPA PCA var explained: {pca_b.explained_variance_ratio_.sum():.3f}")

# ── Step 2: CCA ──────────────────────────────────────────────────────────────
N_CC = 100  # number of canonical components (= N_PCA)
print(f"\nFitting CCA with {N_CC} components...")

cca = CCA(n_components=N_CC, max_iter=1000)
brain_cc, video_cc = cca.fit_transform(brain_pca, vjepa_pca)
# brain_cc: (2196, N_CC), video_cc: (2196, N_CC)

# Canonical correlations
print("\nCanonical correlations:")
cc_r = np.array([np.corrcoef(brain_cc[:, i], video_cc[:, i])[0, 1] for i in range(N_CC)])
for i in range(N_CC):
    print(f"  CC{i+1}: r = {cc_r[i]:.4f}")

# ── Step 3: Permutation test for significant CCs ─────────────────────────────
N_PERM = 1000
print(f"\nPermutation test ({N_PERM} permutations)...")
rng = np.random.default_rng(42)

cc_r_null = np.zeros((N_CC, N_PERM))
for p in range(N_PERM):
    perm_idx = rng.permutation(brain_pca.shape[0])
    brain_perm = brain_pca[perm_idx]
    try:
        cca_perm = CCA(n_components=N_CC, max_iter=500)
        b_perm, v_perm = cca_perm.fit_transform(brain_perm, vjepa_pca)
        for i in range(N_CC):
            cc_r_null[i, p] = np.corrcoef(b_perm[:, i], v_perm[:, i])[0, 1]
    except:
        cc_r_null[:, p] = 0.0
    if (p + 1) % 100 == 0:
        print(f"  Permutation {p+1}/{N_PERM} done")

# p-values
p_values = np.array([np.mean(cc_r_null[i] >= cc_r[i]) for i in range(N_CC)])

# FDR correction (BH)
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
print(f"SIGNIFICANT CANONICAL COMPONENTS (FDR q < 0.05): {n_sig}")
print(f"{'='*60}")
for i in range(N_CC):
    status = "✓ SIG" if sig_mask[i] else "  ---"
    print(f"  CC{i+1}: r={cc_r[i]:.4f}, p={p_values[i]:.4f}, q={p_corrected[i]:.4f} {status}")

# ── Step 4: Emotion correlation of canonical variates ─────────────────────────
print(f"\nComputing emotion correlations for all {N_CC} CCs...")

# Use video-side canonical variates (aligned to V-JEPA2 space)
corr_cc_emo = np.zeros((N_CC, 34))
pval_cc_emo = np.zeros((N_CC, 34))
for i in range(N_CC):
    for j in range(34):
        r, p = spearmanr(video_cc[:, i], emotion_scores[:, j])
        corr_cc_emo[i, j] = r
        pval_cc_emo[i, j] = p

# Also brain-side
corr_cc_emo_brain = np.zeros((N_CC, 34))
for i in range(N_CC):
    for j in range(34):
        r, _ = spearmanr(brain_cc[:, i], emotion_scores[:, j])
        corr_cc_emo_brain[i, j] = r

# Arousal / Valence
corr_cc_av = np.zeros((N_CC, 2))
for i in range(N_CC):
    corr_cc_av[i, 0], _ = spearmanr(video_cc[:, i], arousal)
    corr_cc_av[i, 1], _ = spearmanr(video_cc[:, i], valence)

# Summary: max |r| per CC
max_r_per_cc = np.max(np.abs(corr_cc_emo), axis=1)

print("\nEmotion correlation summary (video-side CC):")
for i in range(min(N_CC, 15)):
    top3_idx = np.argsort(np.abs(corr_cc_emo[i]))[-3:][::-1]
    top3 = [(EMOTION_LABELS[j], f"{corr_cc_emo[i,j]:+.3f}") for j in top3_idx]
    sig_str = "✓" if sig_mask[i] else " "
    print(f"  {sig_str} CC{i+1} (r={cc_r[i]:.3f}): max|r|={max_r_per_cc[i]:.3f}, "
          f"A={corr_cc_av[i,0]:+.3f}, V={corr_cc_av[i,1]:+.3f}, top3={top3}")

# ── Step 5: Decoding from CCA subspace ────────────────────────────────────────
print("\n" + "="*60)
print("EMOTION DECODING FROM CCA SUBSPACE")
print("="*60)

# Compare: significant CCs only vs all CCs vs PCA baseline (PC1-3)
sig_indices = np.where(sig_mask)[0]
print(f"Using {n_sig} significant CCs: {sig_indices + 1}")

# Targets: 34 emotions + Arousal + Valence
targets_all = np.hstack([emotion_scores, arousal[:, None], valence[:, None]])  # (2196, 36)
target_names = EMOTION_LABELS + ['Arousal', 'Valence']

# Feature sets to compare
vjepa_pca_full = PCA(n_components=100, random_state=42).fit_transform(scaler_v.fit_transform(vjepa))

feature_sets = {
    'CCA-sig': video_cc[:, sig_mask] if n_sig > 0 else video_cc[:, :1],
    f'CCA-all{N_CC}': video_cc,
    'PCA-PC1to3': vjepa_pca_full[:, :3],
    'PCA-PC1to10': vjepa_pca_full[:, :10],
    'PCA-all100': vjepa_pca_full,
}

model = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

r2_results = {}
for feat_name, X in feature_sets.items():
    print(f"\n  [{feat_name}] shape={X.shape}")
    r2_vals = np.zeros(36)
    for t in range(36):
        scores = cross_val_score(model, X, targets_all[:, t], cv=5, scoring='r2')
        r2_vals[t] = max(scores.mean(), 0.0)
    r2_results[feat_name] = r2_vals

    cat_mean = r2_vals[:34].mean()
    av_mean = r2_vals[34:].mean()
    ratio = cat_mean / max(av_mean, 1e-10)
    print(f"    Mean R² (34 cat): {cat_mean:.4f}")
    print(f"    Mean R² (A/V):    {av_mean:.4f}")
    print(f"    Cat/VA ratio:     {ratio:.3f}")

# ── Step 6: Compare brain-predictable PCs vs CCA ────────────────────────────
print("\n" + "="*60)
print("COMPARISON: PCA brain-pred (PC1-3) vs CCA-sig")
print("="*60)

for feat_name in ['PCA-PC1to3', 'CCA-sig']:
    r2 = r2_results[feat_name]
    print(f"\n  {feat_name}:")
    print(f"    Dims: {feature_sets[feat_name].shape[1]}")
    print(f"    Mean R² (cat): {r2[:34].mean():.4f}")
    print(f"    Mean R² (A/V): {r2[34:].mean():.4f}")
    print(f"    Cat/VA ratio:  {r2[:34].mean() / max(r2[34:].mean(), 1e-10):.3f}")
    # Top 5 emotions
    top5 = np.argsort(r2[:34])[-5:][::-1]
    for idx in top5:
        print(f"      {EMOTION_LABELS[idx]}: R²={r2[idx]:.4f}")

# ── Step 7: Subject-level CCA ────────────────────────────────────────────────
print("\n" + "="*60)
print("SUBJECT-LEVEL CCA")
print("="*60)

cc_r_per_subj = np.zeros((5, N_CC))
for s in range(5):
    brain_s_subj = scaler_b.fit_transform(brain_raw[s])
    brain_pca_subj = pca_b.fit_transform(brain_s_subj)
    cca_subj = CCA(n_components=N_CC, max_iter=1000)
    b_subj, v_subj = cca_subj.fit_transform(brain_pca_subj, vjepa_pca)
    for i in range(N_CC):
        cc_r_per_subj[s, i] = np.corrcoef(b_subj[:, i], v_subj[:, i])[0, 1]
    print(f"  Subject {s+1}: CC1={cc_r_per_subj[s,0]:.4f}, CC2={cc_r_per_subj[s,1]:.4f}, "
          f"CC3={cc_r_per_subj[s,2]:.4f}")

print(f"\n  Mean CC1 across subjects: {cc_r_per_subj[:,0].mean():.4f} ± {cc_r_per_subj[:,0].std():.4f}")

# ── Save ──────────────────────────────────────────────────────────────────────
print("\nSaving results...")
np.savez(
    OUTPUT_DIR / "cca_brain_video_results.npz",
    # CCA results
    cc_r=cc_r,
    brain_cc=brain_cc,
    video_cc=video_cc,
    sig_mask=sig_mask,
    p_values=p_values,
    p_corrected=p_corrected,
    cc_r_null=cc_r_null,
    # Emotion correlations
    corr_cc_emo=corr_cc_emo,
    pval_cc_emo=pval_cc_emo,
    corr_cc_emo_brain=corr_cc_emo_brain,
    corr_cc_av=corr_cc_av,
    max_r_per_cc=max_r_per_cc,
    # Decoding results
    r2_cca_sig=r2_results.get('CCA-sig', np.zeros(36)),
    r2_cca_all=r2_results.get(f'CCA-all{N_CC}', np.zeros(36)),
    r2_pca_3=r2_results.get('PCA-PC1to3', np.zeros(36)),
    r2_pca_10=r2_results.get('PCA-PC1to10', np.zeros(36)),
    r2_pca_100=r2_results.get('PCA-all100', np.zeros(36)),
    # Subject-level
    cc_r_per_subj=cc_r_per_subj,
    # Metadata
    emotion_labels=np.array(EMOTION_LABELS),
    n_pca=N_PCA,
    n_cc=N_CC,
    n_perm=N_PERM,
)
print(f"Saved → {OUTPUT_DIR}/cca_brain_video_results.npz")
print("\nDone.")
