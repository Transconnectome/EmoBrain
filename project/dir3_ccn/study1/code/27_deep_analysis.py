"""
Exp 27: Deep analysis — every possible interpretation analysis.

1. 6 Basic Emotion 왜 안 나오는가
2. Rating 분포 통제 후 R² (partial correlation)
3. V-JEPA2 PC1, PC2, PC3 각각의 감정 프로필 상세
4. Raw fMRI로 전체 분석 재실행 (Forward, Reverse, 감정 디코딩)
5. Variance Partitioning (Stimulus × Brain × Behavior 삼각형)
6. Brain Residual — V-JEPA2가 설명 못하는 뇌의 고유 감정 정보
7. Emotion clustering — brain-pred space에서 감정이 어떻게 군집되는가
8. CCA CC들과 Cowen 27범주 1:1 대응 시도
9. Partial Mantel test — r(brain, behavior | stimulus)
10. V-JEPA2 vs CLIP 비교
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.decomposition import PCA
from scipy.stats import spearmanr, pearsonr, rankdata
from scipy.spatial.distance import pdist, squareform, correlation
from scipy.cluster.hierarchy import linkage, fcluster
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

BASIC_6 = ['Anger', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise']
BASIC_6_IDX = [EMOTION_LABELS.index(e) for e in BASIC_6]

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading all data...")
vjepa = np.load(BASE / "video_embeddings/vjepa2_embeddings.npy").astype(np.float64)
clip_emb = np.load(BASE / "video_embeddings/clip_embeddings.npy").astype(np.float64)
brain_raw = np.load(BASE / "brain_embeddings/brain_jepa_embeddings.npy").astype(np.float64)
brain_mean = brain_raw.mean(axis=0)
fmri_raw = np.load(BASE / "raw_fmri_results/fmri_raw.npy").astype(np.float64)
fmri_mean = fmri_raw.mean(axis=0)

meta = pd.read_csv(Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv"))
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)
score_cols = [f"score_{i}" for i in range(34)]
emotion_scores = meta[score_cols].values.astype(np.float64)
arousal = meta['arousal_score'].values.astype(np.float64)
valence = meta['valence_score'].values.astype(np.float64)

# PCA
pca_v = PCA(n_components=100, random_state=42)
vjepa_pcs = pca_v.fit_transform(vjepa)
pca_c = PCA(n_components=100, random_state=42)
clip_pcs = pca_c.fit_transform(clip_emb)

model = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

# Brain-pred subspace decoding R²
d_17 = np.load(RES / 'exp17_av2d_results.npz', allow_pickle=True)
r2_pred = d_17['r2_pred_vjepa'][:34]

print("Data loaded.")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("1. WHY DO 6 BASIC EMOTIONS FAIL?")
print("="*70)

# Rating stats for all 34
emo_std = emotion_scores.std(axis=0)
emo_mean_val = emotion_scores.mean(axis=0)
emo_nonzero = (emotion_scores > 0.01).mean(axis=0)  # proportion of videos with this emotion

# Specificity: how many videos strongly express this emotion?
emo_strong = (emotion_scores > 0.3).mean(axis=0)  # >0.3 threshold

# Inter-emotion redundancy: max correlation with any other emotion
emo_corr_mat = np.corrcoef(emotion_scores.T)
np.fill_diagonal(emo_corr_mat, 0)
emo_max_corr = np.max(np.abs(emo_corr_mat), axis=1)  # how redundant each emotion is

# Visual distinctiveness: how well does V-JEPA2 alone separate high vs low videos?
vjepa_separability = np.zeros(34)
for j in range(34):
    high_mask = emotion_scores[:, j] > np.percentile(emotion_scores[:, j], 75)
    low_mask = emotion_scores[:, j] < np.percentile(emotion_scores[:, j], 25)
    if high_mask.sum() > 10 and low_mask.sum() > 10:
        high_mean = vjepa[high_mask].mean(axis=0)
        low_mean = vjepa[low_mask].mean(axis=0)
        # Cohen's d analog: distance between means / pooled std
        diff = high_mean - low_mean
        pooled_std = np.sqrt((vjepa[high_mask].std(axis=0)**2 + vjepa[low_mask].std(axis=0)**2) / 2)
        vjepa_separability[j] = np.mean(np.abs(diff) / (pooled_std + 1e-10))

print(f"\n{'Emotion':<25s} {'R²':>6s} {'Std':>6s} {'NZ%':>5s} {'Str%':>5s} {'MaxCorr':>8s} {'VSep':>6s}")
print("-"*65)
sort_idx = np.argsort(r2_pred)[::-1]
for i in sort_idx:
    marker = " *** BASIC" if EMOTION_LABELS[i] in BASIC_6 else ""
    print(f"{EMOTION_LABELS[i]:<25s} {r2_pred[i]:6.3f} {emo_std[i]:6.3f} {emo_nonzero[i]*100:4.1f}% "
          f"{emo_strong[i]*100:4.1f}% {emo_max_corr[i]:8.3f} {vjepa_separability[i]:6.3f}{marker}")

# Summary: basic 6 vs rest
basic_mask = np.array([i in BASIC_6_IDX for i in range(34)])
print(f"\n  6 Basic emotions:  mean R²={r2_pred[basic_mask].mean():.4f}, mean Std={emo_std[basic_mask].mean():.3f}, "
      f"mean VSep={vjepa_separability[basic_mask].mean():.3f}")
print(f"  Other 28 emotions: mean R²={r2_pred[~basic_mask].mean():.4f}, mean Std={emo_std[~basic_mask].mean():.3f}, "
      f"mean VSep={vjepa_separability[~basic_mask].mean():.3f}")

# Correlation: R² with various factors
factors = {
    'Std': emo_std,
    'Mean': emo_mean_val,
    'NonZero%': emo_nonzero,
    'Strong%': emo_strong,
    'MaxCorr': emo_max_corr,
    'V-JEPA2 Separability': vjepa_separability,
}
print(f"\n  Correlation of R² with:")
for fname, fvals in factors.items():
    r, p = pearsonr(r2_pred, fvals)
    print(f"    {fname:<25s}: r={r:.3f}, p={p:.4f}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("2. RATING DISTRIBUTION CONTROLLED — RANK-NORMALIZED R²")
print("="*70)

# Rank-normalize emotion ratings to remove distribution effects
emo_ranked = np.zeros_like(emotion_scores)
for j in range(34):
    emo_ranked[:, j] = rankdata(emotion_scores[:, j])

# Re-decode with rank-normalized ratings
r2_ranked = np.zeros(34)
for j in range(34):
    scores = cross_val_score(model, vjepa_pcs[:, :3], emo_ranked[:, j], cv=5, scoring='r2')
    r2_ranked[j] = max(scores.mean(), 0.0)

print(f"\nOriginal vs Rank-normalized decoding (brain-pred PC1-3):")
print(f"{'Emotion':<25s} {'Original':>10s} {'Ranked':>10s} {'Change':>8s}")
print("-"*56)
for i in np.argsort(r2_pred)[::-1][:15]:
    change = r2_ranked[i] - r2_pred[i]
    print(f"{EMOTION_LABELS[i]:<25s} {r2_pred[i]:10.4f} {r2_ranked[i]:10.4f} {change:+8.4f}")

r_orig_rank, p_orig_rank = pearsonr(r2_pred, r2_ranked)
print(f"\n  Original vs Ranked R² correlation: r={r_orig_rank:.3f}")
print(f"  Mean original: {r2_pred.mean():.4f}, Mean ranked: {r2_ranked.mean():.4f}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("3. V-JEPA2 PC1, PC2, PC3 — DETAILED PROFILES")
print("="*70)

for pc_i in range(3):
    pc_vals = vjepa_pcs[:, pc_i]
    print(f"\n--- PC{pc_i+1} (var: {pca_v.explained_variance_ratio_[pc_i]*100:.1f}%) ---")

    # All 34 emotions
    corrs_all = []
    for j in range(34):
        r, p = spearmanr(pc_vals, emotion_scores[:, j])
        corrs_all.append((j, r, p))
    corrs_all.sort(key=lambda x: abs(x[1]), reverse=True)

    print(f"  All emotions (sorted by |r|):")
    for j, r, p in corrs_all[:10]:
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"    {EMOTION_LABELS[j]:<25s} r={r:+.4f} {sig}")

    r_a, _ = spearmanr(pc_vals, arousal)
    r_v, _ = spearmanr(pc_vals, valence)
    print(f"  Arousal: r={r_a:+.4f}, Valence: r={r_v:+.4f}")

    # Unique contribution of each PC
    print(f"  Unique decoding (this PC alone vs all 3):")
    for j_show in [corrs_all[0][0], corrs_all[1][0], corrs_all[2][0]]:
        r2_single = max(cross_val_score(model, pc_vals.reshape(-1, 1), emotion_scores[:, j_show],
                                         cv=5, scoring='r2').mean(), 0)
        r2_all3 = max(cross_val_score(model, vjepa_pcs[:, :3], emotion_scores[:, j_show],
                                       cv=5, scoring='r2').mean(), 0)
        print(f"    {EMOTION_LABELS[j_show]:<25s}: PC{pc_i+1} alone R²={r2_single:.4f}, "
              f"all 3 PCs R²={r2_all3:.4f}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("4. RAW fMRI — FULL FORWARD + REVERSE + DECODING")
print("="*70)

# Forward: Raw fMRI → V-JEPA2 PC (already in exp26, but redo for completeness)
print("\n4a. Forward: Raw fMRI → V-JEPA2 PC")
r2_raw_fwd = np.zeros(20)
for i in range(20):
    scores = cross_val_score(model, fmri_mean, vjepa_pcs[:, i], cv=5, scoring='r2')
    r2_raw_fwd[i] = max(scores.mean(), 0.0)
    if r2_raw_fwd[i] > 0.01:
        print(f"  PC{i+1}: R²={r2_raw_fwd[i]:.4f}")
print(f"  Raw fMRI brain-predictable PCs (R²>0.01): {np.where(r2_raw_fwd > 0.01)[0] + 1}")

# Forward emotion decoding from raw fMRI brain-pred subspace
raw_pred_mask = r2_raw_fwd > 0.01
if raw_pred_mask.sum() > 0:
    raw_pred_pcs = vjepa_pcs[:, :20][:, raw_pred_mask[:20]]
    print(f"\n4b. Emotion decoding from Raw-fMRI-brain-pred subspace ({raw_pred_mask.sum()} PCs):")
    targets = np.hstack([emotion_scores, arousal[:, None], valence[:, None]])
    r2_raw_pred_emo = np.zeros(36)
    for t in range(36):
        scores = cross_val_score(model, raw_pred_pcs, targets[:, t], cv=5, scoring='r2')
        r2_raw_pred_emo[t] = max(scores.mean(), 0.0)
    cat_r = r2_raw_pred_emo[:34].mean()
    av_r = r2_raw_pred_emo[34:].mean()
    print(f"  Cat R²={cat_r:.4f}, AV R²={av_r:.4f}, Cat/VA={cat_r/max(av_r,1e-10):.3f}")

    # Compare top emotions: Brain-JEPA vs Raw fMRI brain-pred
    print(f"\n  Top 10 emotions (Raw fMRI brain-pred):")
    for i in np.argsort(r2_raw_pred_emo[:34])[::-1][:10]:
        bj_r2 = r2_pred[i]
        print(f"    {EMOTION_LABELS[i]:<25s}: Raw-pred R²={r2_raw_pred_emo[i]:.4f}, BJ-pred R²={bj_r2:.4f}")

# Reverse: V-JEPA2 → Raw fMRI PC
print(f"\n4c. Reverse: V-JEPA2 → Raw fMRI PC")
pca_fmri = PCA(n_components=100, random_state=42)
fmri_pcs = pca_fmri.fit_transform(fmri_mean)
r2_raw_rev = np.zeros(20)
for i in range(20):
    scores = cross_val_score(model, vjepa, fmri_pcs[:, i], cv=5, scoring='r2')
    r2_raw_rev[i] = max(scores.mean(), 0.0)
print(f"  V-JEPA2 → Raw fMRI PC (top 10):")
for i in range(10):
    print(f"    fMRI-PC{i+1} (var={pca_fmri.explained_variance_ratio_[i]*100:.1f}%): R²={r2_raw_rev[i]:.4f}")
print(f"  Significant (R²>0.01): {np.where(r2_raw_rev > 0.01)[0] + 1}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("5. VARIANCE PARTITIONING: Stimulus × Brain × Behavior")
print("="*70)

# For each emotion, how much is explained by stimulus alone, brain alone, both, neither?
print("\nVariance partitioning for each emotion:")
print(f"{'Emotion':<25s} {'Stim':>6s} {'Brain':>6s} {'Shared':>7s} {'Unique_B':>8s} {'Total':>6s}")
print("-"*62)

vp_results = np.zeros((34, 4))  # stim_unique, brain_unique, shared, unexplained
for j in range(34):
    y = emotion_scores[:, j]

    # R² from stimulus alone (V-JEPA2)
    r2_stim = max(cross_val_score(model, vjepa_pcs[:, :3], y, cv=5, scoring='r2').mean(), 0)

    # R² from brain alone (Brain-JEPA)
    r2_brain = max(cross_val_score(model, brain_mean, y, cv=5, scoring='r2').mean(), 0)

    # R² from both combined
    combined = np.hstack([vjepa_pcs[:, :3], brain_mean])
    r2_both = max(cross_val_score(model, combined, y, cv=5, scoring='r2').mean(), 0)

    # Decompose
    shared = r2_stim + r2_brain - r2_both
    shared = max(shared, 0)
    stim_unique = r2_stim - shared
    brain_unique = r2_brain - shared
    stim_unique = max(stim_unique, 0)
    brain_unique = max(brain_unique, 0)

    vp_results[j] = [stim_unique, brain_unique, shared, r2_both]

    if r2_both > 0.02:
        print(f"{EMOTION_LABELS[j]:<25s} {stim_unique:6.3f} {brain_unique:6.3f} {shared:7.3f} "
              f"{brain_unique:8.3f} {r2_both:6.3f}")

print(f"\nMean across 34 emotions:")
print(f"  Stimulus unique:  {vp_results[:, 0].mean():.4f}")
print(f"  Brain unique:     {vp_results[:, 1].mean():.4f}")
print(f"  Shared:           {vp_results[:, 2].mean():.4f}")
print(f"  Total (combined): {vp_results[:, 3].mean():.4f}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("6. BRAIN RESIDUAL — UNIQUE BRAIN EMOTION INFO BEYOND V-JEPA2")
print("="*70)

# Regress out V-JEPA2 from Brain-JEPA → residual = brain's unique info
reg = LinearRegression()
reg.fit(vjepa_pcs[:, :3], brain_mean)
brain_predicted = reg.predict(vjepa_pcs[:, :3])
brain_residual = brain_mean - brain_predicted  # (2196, 768)

# Decode emotions from brain residual
print("Emotion decoding from brain residual (V-JEPA2 regressed out):")
r2_brain_resid = np.zeros(36)
targets = np.hstack([emotion_scores, arousal[:, None], valence[:, None]])
for t in range(36):
    scores = cross_val_score(model, brain_residual, targets[:, t], cv=5, scoring='r2')
    r2_brain_resid[t] = max(scores.mean(), 0.0)

cat_resid = r2_brain_resid[:34].mean()
av_resid = r2_brain_resid[34:].mean()
print(f"  Cat R²={cat_resid:.4f}, AV R²={av_resid:.4f}, Cat/VA={cat_resid/max(av_resid,1e-10):.3f}")

print(f"\n  Top 10 emotions from brain residual:")
for i in np.argsort(r2_brain_resid[:34])[::-1][:10]:
    print(f"    {EMOTION_LABELS[i]:<25s}: residual R²={r2_brain_resid[i]:.4f}, "
          f"brain-pred R²={r2_pred[i]:.4f}")

if cat_resid > 0.005:
    print(f"\n  → Brain has unique emotion info beyond V-JEPA2!")
    print(f"  → This justifies brain-tuning: brain provides signal that V-JEPA2 doesn't have")
else:
    print(f"\n  → Brain residual has little emotion info — V-JEPA2 captures most of it")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("7. EMOTION CLUSTERING IN BRAIN-PRED SPACE")
print("="*70)

# RSM of emotions in brain-pred subspace
# For each emotion, get its "profile" across videos in brain-pred space
# Then cluster emotions by similarity

emo_profiles_bp = np.zeros((34, 3))  # 34 emotions × 3 PCs
for j in range(34):
    # Weighted average of PC values, weighted by emotion rating
    weights = emotion_scores[:, j]
    if weights.sum() > 0:
        emo_profiles_bp[j] = np.average(vjepa_pcs[:, :3], axis=0, weights=weights)

# Distance matrix
emo_dist = squareform(pdist(emo_profiles_bp, 'cosine'))
emo_sim = 1 - emo_dist

# Hierarchical clustering
Z = linkage(pdist(emo_profiles_bp, 'cosine'), method='ward')
clusters_5 = fcluster(Z, t=5, criterion='maxclust')
clusters_3 = fcluster(Z, t=3, criterion='maxclust')

print("\n3-cluster solution:")
for c in range(1, 4):
    members = [EMOTION_LABELS[i] for i in range(34) if clusters_3[i] == c]
    mean_r2 = r2_pred[clusters_3 == c].mean()
    print(f"  Cluster {c} (n={len(members)}, mean R²={mean_r2:.3f}): {members}")

print("\n5-cluster solution:")
for c in range(1, 6):
    members = [EMOTION_LABELS[i] for i in range(34) if clusters_5[i] == c]
    mean_r2 = r2_pred[clusters_5 == c].mean()
    print(f"  Cluster {c} (n={len(members)}, mean R²={mean_r2:.3f}): {members}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("8. CCA CCs vs COWEN CATEGORIES — ASSIGNMENT")
print("="*70)

d_cca = np.load(RES / 'cca_brain_video_results.npz', allow_pickle=True)
corr_cc_emo = d_cca['corr_cc_emo']
cc_r = d_cca['cc_r']
n_cc = len(cc_r)

# For each CC, assign the emotion with highest |r|
assigned_emos = {}
for i in range(min(n_cc, 30)):
    if cc_r[i] < 0.1:
        break
    top_j = np.argmax(np.abs(corr_cc_emo[i]))
    emo_name = EMOTION_LABELS[top_j]
    r_val = corr_cc_emo[i, top_j]

    if emo_name not in assigned_emos:
        assigned_emos[emo_name] = (i, r_val)
    elif abs(r_val) > abs(assigned_emos[emo_name][1]):
        assigned_emos[emo_name] = (i, r_val)

print(f"\nUnique emotions mapped by top 30 CCs: {len(assigned_emos)}/34")
print(f"Mapped emotions:")
for emo, (cc_idx, r_val) in sorted(assigned_emos.items(), key=lambda x: abs(x[1][1]), reverse=True):
    print(f"  CC{cc_idx+1:2d} (r={cc_r[cc_idx]:.3f}) → {emo} ({r_val:+.3f})")

unmapped = [e for e in EMOTION_LABELS if e not in assigned_emos]
print(f"\nUnmapped emotions ({len(unmapped)}): {unmapped}")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("9. PARTIAL MANTEL: r(brain, behavior | stimulus)")
print("="*70)

# RSMs
stim_rsm = 1 - squareform(pdist(vjepa_pcs[:, :100], 'correlation'))
brain_rsm = 1 - squareform(pdist(brain_mean, 'correlation'))
behav_rsm = 1 - squareform(pdist(emotion_scores, 'correlation'))

# Use subset for speed (2196×2196 is big)
n_sub = 500
rng = np.random.default_rng(42)
sub_idx = rng.choice(2196, n_sub, replace=False)
stim_sub = 1 - squareform(pdist(vjepa_pcs[sub_idx, :100], 'correlation'))
brain_sub = 1 - squareform(pdist(brain_mean[sub_idx], 'correlation'))
behav_sub = 1 - squareform(pdist(emotion_scores[sub_idx], 'correlation'))

triu = np.triu_indices(n_sub, k=1)

# Simple Mantel tests
r_sb, _ = spearmanr(stim_sub[triu], brain_sub[triu])
r_sbeh, _ = spearmanr(stim_sub[triu], behav_sub[triu])
r_bbeh, _ = spearmanr(brain_sub[triu], behav_sub[triu])

print(f"  Mantel: Stimulus ↔ Brain:    r={r_sb:.4f}")
print(f"  Mantel: Stimulus ↔ Behavior: r={r_sbeh:.4f}")
print(f"  Mantel: Brain ↔ Behavior:    r={r_bbeh:.4f}")

# Partial Mantel: Brain ↔ Behavior | Stimulus
# Residualize brain-behavior from stimulus
from numpy.linalg import lstsq
s_flat = stim_sub[triu]
b_flat = brain_sub[triu]
beh_flat = behav_sub[triu]

# Regress stimulus out of brain
coef_b, _, _, _ = lstsq(s_flat.reshape(-1, 1), b_flat, rcond=None)
b_resid = b_flat - s_flat * coef_b[0]

# Regress stimulus out of behavior
coef_beh, _, _, _ = lstsq(s_flat.reshape(-1, 1), beh_flat, rcond=None)
beh_resid = beh_flat - s_flat * coef_beh[0]

r_partial, p_partial = spearmanr(b_resid, beh_resid)
print(f"\n  Partial Mantel: Brain ↔ Behavior | Stimulus: r={r_partial:.4f}, p={p_partial:.2e}")
if r_partial > 0 and p_partial < 0.05:
    print(f"  → Brain has emotion info BEYOND what stimulus provides!")
    print(f"  → This is the unique brain contribution that brain-tuning can capture")
else:
    print(f"  → Brain-behavior relationship is fully mediated by stimulus")

# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("10. V-JEPA2 vs CLIP COMPARISON")
print("="*70)

# Brain → CLIP PC prediction
r2_clip_fwd = np.zeros(10)
for i in range(10):
    scores = cross_val_score(model, brain_mean, clip_pcs[:, i], cv=5, scoring='r2')
    r2_clip_fwd[i] = max(scores.mean(), 0.0)

print(f"Brain → V-JEPA2 PC vs Brain → CLIP PC:")
print(f"{'PC':<6s} {'V-JEPA2':>10s} {'CLIP':>10s}")
print("-"*28)
r2_vjepa_fwd = np.zeros(10)
for i in range(10):
    scores = cross_val_score(model, brain_mean, vjepa_pcs[:, i], cv=5, scoring='r2')
    r2_vjepa_fwd[i] = max(scores.mean(), 0.0)
    print(f"PC{i+1:<4d} {r2_vjepa_fwd[i]:10.4f} {r2_clip_fwd[i]:10.4f}")

# CLIP emotion decoding from brain-pred subspace
clip_pred_mask = r2_clip_fwd > 0.01
print(f"\n  V-JEPA2 brain-pred PCs: {np.where(r2_vjepa_fwd[:10] > 0.01)[0] + 1}")
print(f"  CLIP brain-pred PCs:    {np.where(clip_pred_mask)[0] + 1}")

if clip_pred_mask.sum() > 0:
    clip_pred_pcs = clip_pcs[:, :10][:, clip_pred_mask[:10]]
    r2_clip_emo = np.zeros(36)
    targets = np.hstack([emotion_scores, arousal[:, None], valence[:, None]])
    for t in range(36):
        scores = cross_val_score(model, clip_pred_pcs, targets[:, t], cv=5, scoring='r2')
        r2_clip_emo[t] = max(scores.mean(), 0.0)
    cat_c = r2_clip_emo[:34].mean()
    av_c = r2_clip_emo[34:].mean()
    print(f"  CLIP brain-pred decoding: Cat R²={cat_c:.4f}, AV R²={av_c:.4f}, Cat/VA={cat_c/max(av_c,1e-10):.3f}")
    print(f"  V-JEPA2 brain-pred:       Cat R²={r2_pred.mean():.4f}")

# ═════════════════════════════════════════════════════════════════════════════
# SAVE
# ═════════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("SAVING ALL RESULTS")
print("="*70)

np.savez(OUT / 'deep_analysis.npz',
    # 1. Basic emotion analysis
    vjepa_separability=vjepa_separability,
    emo_max_corr=emo_max_corr,
    emo_strong=emo_strong,
    # 2. Rank-normalized
    r2_ranked=r2_ranked,
    # 4. Raw fMRI
    r2_raw_fwd=r2_raw_fwd,
    r2_raw_rev=r2_raw_rev,
    r2_raw_pred_emo=r2_raw_pred_emo if raw_pred_mask.sum() > 0 else np.zeros(36),
    raw_pred_mask=raw_pred_mask,
    # 5. Variance partitioning
    vp_results=vp_results,
    # 6. Brain residual
    r2_brain_resid=r2_brain_resid,
    # 7. Clustering
    clusters_3=clusters_3,
    clusters_5=clusters_5,
    emo_profiles_bp=emo_profiles_bp,
    # 9. Partial Mantel
    r_mantel_sb=r_sb,
    r_mantel_sbeh=r_sbeh,
    r_mantel_bbeh=r_bbeh,
    r_partial_mantel=r_partial,
    p_partial_mantel=p_partial,
    # 10. CLIP comparison
    r2_clip_fwd=r2_clip_fwd,
    # Labels
    emotion_labels=np.array(EMOTION_LABELS),
)
print(f"Saved → {OUT}/deep_analysis.npz")
print("\nDone.")
