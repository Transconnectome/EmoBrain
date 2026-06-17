"""
Exp 26: Comprehensive interpretation of all results.

1. Rating distribution analysis — R² artifact check
2. V-JEPA2 PC1-3 individual meaning
3. CCA CC structure vs Cowen's 27 categories
4. Raw fMRI vs Brain-JEPA comparison
5. Inter-emotion correlation structure
6. Confound checks (visual features, low-level)
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.decomposition import PCA
from scipy.stats import spearmanr, pearsonr, skew
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')

BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
RES  = BASE / "CCN2026/results"
OUT  = BASE / "main/results"
OUT.mkdir(parents=True, exist_ok=True)

EMOTION_LABELS = [
    'Admiration', 'Adoration', 'Aesthetic appreciation', 'Amusement', 'Anger',
    'Anxiety', 'Awe', 'Awkwardness', 'Boredom', 'Calmness', 'Confusion',
    'Contempt', 'Craving', 'Disgust', 'Empathic pain', 'Entrancement',
    'Excitement', 'Fear', 'Horror', 'Interest', 'Joy', 'Nostalgia', 'Relief',
    'Romance', 'Sadness', 'Satisfaction', 'Sexual desire', 'Surprise',
    'Sympathy', 'Triumph', 'Uncomfortable', 'Annoyance', 'Envy', 'Guilt'
]

# ── Load all data ─────────────────────────────────────────────────────────────
print("Loading data...")
vjepa = np.load(BASE / "video_embeddings/vjepa2_embeddings.npy").astype(np.float64)
brain_raw = np.load(BASE / "brain_embeddings/brain_jepa_embeddings.npy").astype(np.float64)
brain_mean = brain_raw.mean(axis=0)
fmri_raw = np.load(BASE / "raw_fmri_results/fmri_raw.npy").astype(np.float64)  # (5, 2196, 450)
fmri_mean = fmri_raw.mean(axis=0)  # (2196, 450)

meta = pd.read_csv(Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv"))
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

score_cols = [f"score_{i}" for i in range(34)]
emotion_scores = meta[score_cols].values.astype(np.float64)  # (2196, 34)
arousal = meta['arousal_score'].values.astype(np.float64)
valence = meta['valence_score'].values.astype(np.float64)

# PCA on V-JEPA2
pca_v = PCA(n_components=100, random_state=42)
vjepa_pcs = pca_v.fit_transform(vjepa)

# Load previous results
d_17 = np.load(RES / 'exp17_av2d_results.npz', allow_pickle=True)
r2_pred = d_17['r2_pred_vjepa']  # (36,) brain-pred subspace decoding

print(f"V-JEPA2: {vjepa.shape}, Brain-JEPA: {brain_mean.shape}, Raw fMRI: {fmri_mean.shape}")

model = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

# ═════════════════════════════════════════════════════════════════════════════
# 1. RATING DISTRIBUTION ANALYSIS — IS R² DRIVEN BY RATING VARIANCE?
# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("1. RATING DISTRIBUTION vs DECODING R²")
print("="*70)

emo_r2 = r2_pred[:34]
emo_mean = emotion_scores.mean(axis=0)
emo_std  = emotion_scores.std(axis=0)
emo_skewness = np.array([skew(emotion_scores[:, j]) for j in range(34)])
emo_range = emotion_scores.max(axis=0) - emotion_scores.min(axis=0)
# Proportion of non-zero ratings (sparsity)
emo_nonzero = (emotion_scores > 0).mean(axis=0)

# Correlation: R² vs distribution stats
r_std, p_std = pearsonr(emo_r2, emo_std)
r_mean, p_mean = pearsonr(emo_r2, emo_mean)
r_skew, p_skew = pearsonr(emo_r2, emo_skewness)
r_range, p_range = pearsonr(emo_r2, emo_range)
r_nonzero, p_nonzero = pearsonr(emo_r2, emo_nonzero)

print(f"\nCorrelation between decoding R² and rating statistics:")
print(f"  R² vs Std:       r={r_std:.3f},  p={p_std:.4f}  {'⚠️ CONFOUND' if p_std < 0.05 else '✓ OK'}")
print(f"  R² vs Mean:      r={r_mean:.3f}, p={p_mean:.4f} {'⚠️ CONFOUND' if p_mean < 0.05 else '✓ OK'}")
print(f"  R² vs Skewness:  r={r_skew:.3f}, p={p_skew:.4f} {'⚠️ CONFOUND' if p_skew < 0.05 else '✓ OK'}")
print(f"  R² vs Range:     r={r_range:.3f}, p={p_range:.4f} {'⚠️ CONFOUND' if p_range < 0.05 else '✓ OK'}")
print(f"  R² vs Non-zero%: r={r_nonzero:.3f}, p={p_nonzero:.4f} {'⚠️ CONFOUND' if p_nonzero < 0.05 else '✓ OK'}")

print(f"\nPer-emotion details (sorted by R²):")
sort_idx = np.argsort(emo_r2)[::-1]
print(f"{'Emotion':<25s} {'R²':>6s} {'Mean':>6s} {'Std':>6s} {'Skew':>6s} {'NZ%':>6s}")
print("-"*60)
for i in sort_idx:
    print(f"{EMOTION_LABELS[i]:<25s} {emo_r2[i]:6.3f} {emo_mean[i]:6.3f} {emo_std[i]:6.3f} "
          f"{emo_skewness[i]:6.2f} {emo_nonzero[i]*100:5.1f}%")

# ═════════════════════════════════════════════════════════════════════════════
# 2. V-JEPA2 PC1-3 INDIVIDUAL MEANING
# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("2. V-JEPA2 PC1, PC2, PC3 — WHAT DOES EACH ENCODE?")
print("="*70)

for pc_i in range(3):
    pc_vals = vjepa_pcs[:, pc_i]
    print(f"\n--- PC{pc_i+1} (var explained: {pca_v.explained_variance_ratio_[pc_i]*100:.1f}%) ---")

    # Correlation with each emotion
    corrs = []
    for j in range(34):
        r, p = spearmanr(pc_vals, emotion_scores[:, j])
        corrs.append((EMOTION_LABELS[j], r, p))
    corrs.sort(key=lambda x: abs(x[1]), reverse=True)

    print(f"  Top 5 positive emotions:")
    pos = [(n, r, p) for n, r, p in corrs if r > 0][:5]
    for n, r, p in pos:
        print(f"    {n:<25s} r={r:+.3f} (p={p:.1e})")

    print(f"  Top 5 negative emotions:")
    neg = [(n, r, p) for n, r, p in corrs if r < 0][:5]
    for n, r, p in neg:
        print(f"    {n:<25s} r={r:+.3f} (p={p:.1e})")

    # Correlation with Arousal, Valence
    r_a, p_a = spearmanr(pc_vals, arousal)
    r_v, p_v = spearmanr(pc_vals, valence)
    print(f"  Arousal: r={r_a:+.3f} (p={p_a:.1e})")
    print(f"  Valence: r={r_v:+.3f} (p={p_v:.1e})")

    # Top/bottom videos characterization
    top_idx = np.argsort(pc_vals)[-20:]  # top 20 videos on this PC
    bot_idx = np.argsort(pc_vals)[:20]   # bottom 20 videos

    top_emo_profile = emotion_scores[top_idx].mean(axis=0)
    bot_emo_profile = emotion_scores[bot_idx].mean(axis=0)
    diff = top_emo_profile - bot_emo_profile
    diff_sort = np.argsort(diff)[::-1]

    print(f"  Top 20 videos (high PC{pc_i+1}) vs Bottom 20 videos:")
    print(f"    Most increased:  {EMOTION_LABELS[diff_sort[0]]} (+{diff[diff_sort[0]]:.3f}), "
          f"{EMOTION_LABELS[diff_sort[1]]} (+{diff[diff_sort[1]]:.3f}), "
          f"{EMOTION_LABELS[diff_sort[2]]} (+{diff[diff_sort[2]]:.3f})")
    print(f"    Most decreased:  {EMOTION_LABELS[diff_sort[-1]]} ({diff[diff_sort[-1]]:.3f}), "
          f"{EMOTION_LABELS[diff_sort[-2]]} ({diff[diff_sort[-2]]:.3f}), "
          f"{EMOTION_LABELS[diff_sort[-3]]} ({diff[diff_sort[-3]]:.3f})")

    top_a = arousal[top_idx].mean()
    bot_a = arousal[bot_idx].mean()
    top_v = valence[top_idx].mean()
    bot_v = valence[bot_idx].mean()
    print(f"    Arousal: top={top_a:.3f} vs bot={bot_a:.3f} (Δ={top_a-bot_a:+.3f})")
    print(f"    Valence: top={top_v:.3f} vs bot={bot_v:.3f} (Δ={top_v-bot_v:+.3f})")

# ═════════════════════════════════════════════════════════════════════════════
# 3. INTER-EMOTION CORRELATION STRUCTURE
# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("3. INTER-EMOTION CORRELATION STRUCTURE")
print("="*70)

emo_corr = np.corrcoef(emotion_scores.T)  # (34, 34)

# Find highly correlated pairs
pairs = []
for i in range(34):
    for j in range(i+1, 34):
        pairs.append((EMOTION_LABELS[i], EMOTION_LABELS[j], emo_corr[i, j]))
pairs.sort(key=lambda x: abs(x[2]), reverse=True)

print("\nTop 10 most correlated emotion pairs:")
for n1, n2, r in pairs[:10]:
    print(f"  {n1} × {n2}: r={r:.3f}")

print("\nTop 10 most anti-correlated pairs:")
pairs_neg = sorted(pairs, key=lambda x: x[2])
for n1, n2, r in pairs_neg[:10]:
    print(f"  {n1} × {n2}: r={r:.3f}")

# Check if high-R² emotions are correlated with each other
high_r2_idx = np.argsort(emo_r2)[-5:]  # top 5 by R²
print(f"\nCorrelation among top-5 decoded emotions:")
for i in range(5):
    for j in range(i+1, 5):
        ii, jj = high_r2_idx[i], high_r2_idx[j]
        print(f"  {EMOTION_LABELS[ii]} × {EMOTION_LABELS[jj]}: r={emo_corr[ii,jj]:.3f}")

# ═════════════════════════════════════════════════════════════════════════════
# 4. RAW fMRI vs BRAIN-JEPA COMPARISON
# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("4. RAW fMRI vs BRAIN-JEPA — DOES BRAIN-JEPA ADD OR DISTORT?")
print("="*70)

# 4a: Raw fMRI → V-JEPA2 PC prediction
print("\n4a: Brain → V-JEPA2 PC prediction (Raw fMRI vs Brain-JEPA)")
r2_fmri_to_vpc = np.zeros(10)
r2_bj_to_vpc = np.zeros(10)

for i in range(10):
    scores_fmri = cross_val_score(model, fmri_mean, vjepa_pcs[:, i], cv=5, scoring='r2')
    scores_bj = cross_val_score(model, brain_mean, vjepa_pcs[:, i], cv=5, scoring='r2')
    r2_fmri_to_vpc[i] = max(scores_fmri.mean(), 0.0)
    r2_bj_to_vpc[i] = max(scores_bj.mean(), 0.0)

print(f"{'PC':<6s} {'Raw fMRI R²':>12s} {'Brain-JEPA R²':>14s} {'Δ':>8s}")
print("-"*42)
for i in range(10):
    delta = r2_bj_to_vpc[i] - r2_fmri_to_vpc[i]
    print(f"PC{i+1:<4d} {r2_fmri_to_vpc[i]:12.4f} {r2_bj_to_vpc[i]:14.4f} {delta:+8.4f}")

# 4b: Emotion decoding from raw fMRI vs Brain-JEPA
print("\n4b: Emotion decoding (Raw fMRI PCA vs Brain-JEPA)")
pca_fmri = PCA(n_components=100, random_state=42)
fmri_pcs = pca_fmri.fit_transform(fmri_mean)
print(f"  Raw fMRI PCA var explained: {pca_fmri.explained_variance_ratio_.sum():.3f}")

# Brain-pred subspace for raw fMRI: find which fMRI PCs predict V-JEPA2 PCs
r2_fmri_pred = np.zeros(100)
for i in range(100):
    scores = cross_val_score(model, fmri_pcs, vjepa_pcs[:, i], cv=5, scoring='r2')
    r2_fmri_pred[i] = max(scores.mean(), 0.0)

fmri_brain_pred = r2_fmri_pred > 0.01
print(f"  Raw fMRI → V-JEPA2 PC: {fmri_brain_pred.sum()} PCs with R²>0.01")
print(f"  R² values: {r2_fmri_pred[fmri_brain_pred].round(4)}")

# Emotion decoding from raw fMRI
targets = np.hstack([emotion_scores, arousal[:, None], valence[:, None]])

# Raw fMRI: full space
r2_fmri_emo = np.zeros(36)
for t in range(36):
    scores = cross_val_score(model, fmri_mean, targets[:, t], cv=5, scoring='r2')
    r2_fmri_emo[t] = max(scores.mean(), 0.0)

# Brain-JEPA: full space
r2_bj_emo = np.zeros(36)
for t in range(36):
    scores = cross_val_score(model, brain_mean, targets[:, t], cv=5, scoring='r2')
    r2_bj_emo[t] = max(scores.mean(), 0.0)

# V-JEPA2: full space (for reference)
r2_vjepa_emo = np.zeros(36)
for t in range(36):
    scores = cross_val_score(model, vjepa, targets[:, t], cv=5, scoring='r2')
    r2_vjepa_emo[t] = max(scores.mean(), 0.0)

print(f"\nEmotion decoding comparison:")
print(f"{'Source':<20s} {'Cat R²':>8s} {'AV R²':>8s} {'Cat/VA':>8s}")
print("-"*46)
for name, r2 in [('Raw fMRI (450)', r2_fmri_emo),
                  ('Brain-JEPA (768)', r2_bj_emo),
                  ('V-JEPA2 (1408)', r2_vjepa_emo)]:
    cat = r2[:34].mean()
    av = r2[34:].mean()
    ratio = cat / max(av, 1e-10)
    print(f"{name:<20s} {cat:8.4f} {av:8.4f} {ratio:8.3f}")

# Top emotions comparison
print(f"\nTop 5 emotions — Raw fMRI vs Brain-JEPA:")
print(f"{'Rank':<5s} {'Raw fMRI':<28s} {'Brain-JEPA':<28s}")
print("-"*60)
sort_fmri = np.argsort(r2_fmri_emo[:34])[::-1]
sort_bj = np.argsort(r2_bj_emo[:34])[::-1]
for k in range(5):
    i_f, i_b = sort_fmri[k], sort_bj[k]
    print(f"{k+1:<5d} {EMOTION_LABELS[i_f]:<20s} R²={r2_fmri_emo[i_f]:.3f}   "
          f"{EMOTION_LABELS[i_b]:<20s} R²={r2_bj_emo[i_b]:.3f}")

# ═════════════════════════════════════════════════════════════════════════════
# 5. CCA STRUCTURE vs COWEN'S 27 CATEGORIES
# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("5. CCA STRUCTURE vs COWEN'S FRAMEWORK")
print("="*70)

# Cowen & Keltner (2017): emotion categories form a ~27-dimensional space
# We can check: how many dimensions does the emotion rating matrix itself have?

# PCA on emotion ratings
pca_emo = PCA(n_components=34, random_state=42)
pca_emo.fit(emotion_scores)
cum_var = np.cumsum(pca_emo.explained_variance_ratio_)

print(f"\nDimensionality of emotion rating space (PCA on 34 ratings):")
for thresh in [0.80, 0.85, 0.90, 0.95, 0.99]:
    n_dims = np.searchsorted(cum_var, thresh) + 1
    print(f"  {thresh*100:.0f}% variance explained by {n_dims} dimensions")

print(f"\n  Explained variance top 10: {(pca_emo.explained_variance_ratio_[:10]*100).round(1)}%")

# Compare: RSM of CCA CCs vs RSM of emotion categories
# Load CCA results if available
cca_path = RES / 'cca_brain_video_results.npz'
if cca_path.exists():
    d_cca = np.load(cca_path, allow_pickle=True)
    corr_cc_emo = d_cca['corr_cc_emo']  # (30, 34)
    cc_r = d_cca['cc_r']
    n_cc = len(cc_r)

    # Each CC's emotion "loading" → RSM
    # Which CCs map to which emotions?
    print(f"\nCCA CC → emotion mapping (strongest emotion per CC):")
    cc_to_emo = {}
    for i in range(min(n_cc, 15)):
        top_idx = np.argmax(np.abs(corr_cc_emo[i]))
        top_emo = EMOTION_LABELS[top_idx]
        top_r = corr_cc_emo[i, top_idx]
        cc_to_emo[i] = (top_emo, top_r)
        print(f"  CC{i+1} (r={cc_r[i]:.3f}) → {top_emo} ({top_r:+.3f})")

    # How many unique emotions are represented in top CCs?
    unique_emos_10 = set(cc_to_emo[i][0] for i in range(min(10, n_cc)))
    unique_emos_all = set(cc_to_emo[i][0] for i in range(min(n_cc, 15)))
    print(f"\n  Unique emotions in top 10 CCs: {len(unique_emos_10)} — {unique_emos_10}")
    print(f"  Unique emotions in top 15 CCs: {len(unique_emos_all)} — {unique_emos_all}")

    # Mantel test: CCA emotion loading RSM vs behavior emotion RSM
    # RSM from CCA: how similar are emotions based on their CC loadings?
    cca_emo_rsm = 1 - squareform(pdist(corr_cc_emo.T, 'correlation'))  # (34, 34)
    # RSM from behavior: how similar are emotions based on rating co-occurrence?
    behav_emo_rsm = np.corrcoef(emotion_scores.T)  # (34, 34)

    # Mantel test (correlation of upper triangles)
    triu_idx = np.triu_indices(34, k=1)
    r_mantel, p_mantel = spearmanr(cca_emo_rsm[triu_idx], behav_emo_rsm[triu_idx])
    print(f"\n  Mantel test: CCA emotion RSM vs Behavior emotion RSM")
    print(f"    Spearman r = {r_mantel:.4f}, p = {p_mantel:.2e}")
    print(f"    → {'CCA structure matches behavioral emotion structure' if p_mantel < 0.05 else 'No match'}")

# ═════════════════════════════════════════════════════════════════════════════
# 6. CONFOUND CHECK: WHAT IF R² IS DRIVEN BY LOW-LEVEL VISUAL FEATURES?
# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("6. CONFOUND: V-JEPA2 PC1 = LOW-LEVEL VISUAL OR HIGH-LEVEL AFFECTIVE?")
print("="*70)

# V-JEPA2 PC1 explained variance
print(f"\nV-JEPA2 PCA explained variance:")
for i in range(5):
    print(f"  PC{i+1}: {pca_v.explained_variance_ratio_[i]*100:.2f}%")
print(f"  PC1-3 total: {pca_v.explained_variance_ratio_[:3].sum()*100:.2f}%")

# If PC1 is low-level visual, it should correlate with all subjects similarly
# and have specific visual statistics correlations
# Check: PC1-3 correlation with individual subjects
print(f"\nPC1-3 brain prediction: per-subject consistency")
for pc_i in range(3):
    subj_r2 = []
    for s in range(5):
        scores = cross_val_score(model, brain_raw[s], vjepa_pcs[:, pc_i], cv=5, scoring='r2')
        subj_r2.append(max(scores.mean(), 0.0))
    subj_r2 = np.array(subj_r2)
    print(f"  PC{pc_i+1}: per-subject R² = {subj_r2.round(4)}, mean={subj_r2.mean():.4f}, std={subj_r2.std():.4f}")

# Check: emotion prediction after regressing out Arousal/Valence
print(f"\nEmotion decoding AFTER regressing out Arousal/Valence:")
print("(If R² drops to 0, emotion decoding was just VA in disguise)")

from sklearn.linear_model import LinearRegression

av_features = np.stack([arousal, valence], axis=1)  # (2196, 2)

# Regress out AV from each emotion rating
emo_residual = np.zeros_like(emotion_scores)
for j in range(34):
    reg = LinearRegression().fit(av_features, emotion_scores[:, j])
    emo_residual[:, j] = emotion_scores[:, j] - reg.predict(av_features)

# Decode residual emotions from brain-pred subspace
r2_residual = np.zeros(34)
for j in range(34):
    scores = cross_val_score(model, vjepa_pcs[:, :3], emo_residual[:, j], cv=5, scoring='r2')
    r2_residual[j] = max(scores.mean(), 0.0)

print(f"\n{'Emotion':<25s} {'Original R²':>12s} {'Residual R²':>12s} {'Retained%':>10s}")
print("-"*62)
sort_idx = np.argsort(emo_r2)[::-1]
for i in sort_idx[:15]:
    retained = (r2_residual[i] / max(emo_r2[i], 1e-10)) * 100
    print(f"{EMOTION_LABELS[i]:<25s} {emo_r2[i]:12.4f} {r2_residual[i]:12.4f} {retained:9.1f}%")

print(f"\n  Mean original R²:  {emo_r2.mean():.4f}")
print(f"  Mean residual R²:  {r2_residual.mean():.4f}")
print(f"  Retained:          {(r2_residual.mean()/max(emo_r2.mean(),1e-10))*100:.1f}%")
if r2_residual.mean() > 0.01:
    print(f"  → Category decoding SURVIVES AV regression — not just VA in disguise")
else:
    print(f"  → ⚠️ Category decoding DISAPPEARS after AV regression — might be VA artifact")

# ═════════════════════════════════════════════════════════════════════════════
# SAVE ALL RESULTS
# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("SAVING RESULTS")
print("="*70)

np.savez(OUT / 'comprehensive_interpretation.npz',
    # Rating distributions
    emo_mean=emo_mean, emo_std=emo_std, emo_skewness=emo_skewness,
    emo_nonzero=emo_nonzero, emo_range=emo_range,
    r2_vs_std_r=r_std, r2_vs_std_p=p_std,
    r2_vs_mean_r=r_mean, r2_vs_mean_p=p_mean,
    # Raw fMRI vs Brain-JEPA
    r2_fmri_to_vpc=r2_fmri_to_vpc, r2_bj_to_vpc=r2_bj_to_vpc,
    r2_fmri_emo=r2_fmri_emo, r2_bj_emo=r2_bj_emo, r2_vjepa_emo=r2_vjepa_emo,
    # Emotion PCA
    emo_pca_var=pca_emo.explained_variance_ratio_,
    # Residual after AV regression
    r2_residual=r2_residual,
    # Labels
    emotion_labels=np.array(EMOTION_LABELS),
)

print(f"Saved → {OUT}/comprehensive_interpretation.npz")
print("\nDone.")
