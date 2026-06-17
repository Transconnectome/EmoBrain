"""
Chapter 1-E: RSA (Representational Similarity Analysis)

Horikawa (2020) 재현:
  Brain RDM vs Emotion Category RDM → Spearman ρ
  Brain RDM vs VA RDM → Spearman ρ
  → ρ_cat > ρ_VA? (Horikawa 핵심 결과)

ROI별 RSA:
  각 network의 Brain RDM vs Emotion RDM

추가:
  34 cat + 14 dim 전체 비교
  Subject-level consistency
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')

BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
OUT  = BASE / "main/results"

CAT_LABELS = [
    'Admiration', 'Adoration', 'Aesthetic appreciation', 'Amusement', 'Anger',
    'Anxiety', 'Awe', 'Awkwardness', 'Boredom', 'Calmness', 'Confusion',
    'Contempt', 'Craving', 'Disgust', 'Empathic pain', 'Entrancement',
    'Excitement', 'Fear', 'Horror', 'Interest', 'Joy', 'Nostalgia', 'Relief',
    'Romance', 'Sadness', 'Satisfaction', 'Sexual desire', 'Surprise',
    'Sympathy', 'Triumph', 'Uncomfortable', 'Annoyance', 'Envy', 'Guilt'
]
DIM_LABELS = ['Arousal', 'Valence', 'Dominance', 'Approach', 'Attention', 'Certainty',
              'Commitment', 'Control', 'Effort', 'Fairness', 'Identity',
              'Obstruction', 'Safety', 'Upswing']
ALL_LABELS = CAT_LABELS + DIM_LABELS

NETWORK_PARCELS = {
    'Vis': list(range(0, 31)) + list(range(200, 230)),
    'SomMot': list(range(31, 68)) + list(range(230, 270)),
    'DorsAttn': list(range(68, 91)) + list(range(270, 293)),
    'SalVentAttn': list(range(91, 113)) + list(range(293, 318)),
    'Limbic': list(range(113, 126)) + list(range(318, 331)),
    'Cont': list(range(126, 148)) + list(range(331, 361)),
    'Default': list(range(148, 200)) + list(range(361, 400)),
    'Subcortical': list(range(400, 450)),
}

# ── Load ──────────────────────────────────────────────────────────────────
print("Loading data...")
fmri = np.load(BASE / "raw_fmri_results/fmri_raw.npy").astype(np.float64)[:, :2185, :]
fmri_mean = fmri.mean(axis=0)

meta = pd.read_csv(Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv"))
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True).iloc[:2185]
meta14 = pd.read_csv(Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv"))
meta14 = meta14.sort_values('stim_idx').reset_index(drop=True).iloc[:2185]

cat_scores = meta[[f"score_{i}" for i in range(34)]].values.astype(np.float64)
dim_cols = ['arousal_score', 'valence_score', 'dominance_score',
            'approach_score', 'attention_score', 'certainty_score', 'commitment_score',
            'control_score', 'effort_score', 'fairness_score', 'identity_score',
            'obstruction_score', 'safety_score', 'upswing_score']
dim_scores = meta14[dim_cols].values.astype(np.float64)

print(f"fMRI: {fmri_mean.shape}, Cat: {cat_scores.shape}, Dim: {dim_scores.shape}")

# ── RDM computation ───────────────────────────────────────────────────────
def compute_rdm(X):
    """Compute RDM (1 - correlation) from feature matrix (n_samples × n_features)."""
    return 1 - np.corrcoef(X)

def rdm_upper_tri(rdm):
    """Extract upper triangle of RDM (excluding diagonal)."""
    return rdm[np.triu_indices(rdm.shape[0], k=1)]

# N=2185 is too large for full RDM (2185×2185). Subsample.
N_SUB = 500
rng = np.random.default_rng(42)
sub_idx = rng.choice(2185, N_SUB, replace=False)
sub_idx.sort()

print(f"\nSubsampling {N_SUB} videos for RSA (full N={2185} too large for RDM)")

# ── Emotion model RDMs ────────────────────────────────────────────────────
print("\nComputing emotion model RDMs...")

# Category RDM: based on 34 cat scores
cat_rdm = compute_rdm(cat_scores[sub_idx])
cat_tri = rdm_upper_tri(cat_rdm)

# Dimension RDM: based on 14 dim scores
dim_rdm = compute_rdm(dim_scores[sub_idx])
dim_tri = rdm_upper_tri(dim_rdm)

# VA only RDM: arousal + valence only (euclidean, 2차원이라 correlation 불안정)
va_scores = dim_scores[sub_idx, :2]  # arousal, valence
va_rdm = squareform(pdist(va_scores, 'euclidean'))
va_rdm = va_rdm / va_rdm.max()  # normalize to 0-1
va_tri = rdm_upper_tri(va_rdm)

# All 48 RDM
all_scores = np.hstack([cat_scores[sub_idx], dim_scores[sub_idx]])
all_rdm = compute_rdm(all_scores)
all_tri = rdm_upper_tri(all_rdm)

# Per-emotion kernel RDMs (Horikawa 방식: 각 감정별 outer product)
print("Computing per-emotion kernel RDMs...")

# ── Group-level RSA ───────────────────────────────────────────────────────
print("\n" + "="*70)
print("GROUP-LEVEL RSA (whole brain)")
print("="*70)

brain_rdm = compute_rdm(fmri_mean[sub_idx])
brain_tri = rdm_upper_tri(brain_rdm)

rsa_cat, p_cat = spearmanr(brain_tri, cat_tri)
rsa_dim, p_dim = spearmanr(brain_tri, dim_tri)
rsa_va, p_va = spearmanr(brain_tri, va_tri)
rsa_all, p_all = spearmanr(brain_tri, all_tri)

print(f"\n  Brain RDM vs Category RDM:  ρ={rsa_cat:.4f}, p={p_cat:.2e}")
print(f"  Brain RDM vs Dimension RDM: ρ={rsa_dim:.4f}, p={p_dim:.2e}")
print(f"  Brain RDM vs VA RDM:        ρ={rsa_va:.4f}, p={p_va:.2e}")
print(f"  Brain RDM vs All 48 RDM:    ρ={rsa_all:.4f}, p={p_all:.2e}")
print(f"\n  Cat > Dim? {'YES' if rsa_cat > rsa_dim else 'NO'} ({rsa_cat:.4f} vs {rsa_dim:.4f})")
print(f"  Cat > VA?  {'YES' if rsa_cat > rsa_va else 'NO'} ({rsa_cat:.4f} vs {rsa_va:.4f})")

# ── Per-emotion RSA (Horikawa 방식) ───────────────────────────────────────
print("\n" + "="*70)
print("PER-EMOTION RSA")
print("="*70)

# For each emotion: compute kernel (outer product of scores)
# then correlate with brain RDM
rsa_per_emo = np.zeros(48)
p_per_emo = np.zeros(48)
all_emo_scores = np.hstack([cat_scores, dim_scores])

for t in range(48):
    scores = all_emo_scores[sub_idx, t]
    # Emotion kernel: outer product (score_i * score_j for all pairs)
    emo_kernel = np.outer(scores, scores)
    emo_tri = rdm_upper_tri(emo_kernel)
    r, p = spearmanr(brain_tri, emo_tri)
    rsa_per_emo[t] = r
    p_per_emo[t] = p

print(f"\n{'Emotion':<25s} {'RSA ρ':>8s} {'p':>10s} {'Type':>5s}")
print("-"*52)
for i in np.argsort(rsa_per_emo)[::-1]:
    t = "cat" if i < 34 else "dim"
    print(f"{ALL_LABELS[i]:<25s} {rsa_per_emo[i]:8.4f} {p_per_emo[i]:10.2e} {t:>5s}")

cat_rsa_mean = rsa_per_emo[:34].mean()
dim_rsa_mean = rsa_per_emo[34:].mean()
print(f"\n  Category mean RSA: {cat_rsa_mean:.4f}")
print(f"  Dimension mean RSA: {dim_rsa_mean:.4f}")
print(f"  Cat/Dim ratio: {cat_rsa_mean/max(dim_rsa_mean,1e-10):.3f}")

# ── ROI-level RSA ─────────────────────────────────────────────────────────
print("\n" + "="*70)
print("ROI-LEVEL RSA")
print("="*70)

roi_names = list(NETWORK_PARCELS.keys())
rsa_roi_cat = np.zeros(len(roi_names))
rsa_roi_dim = np.zeros(len(roi_names))
rsa_roi_va = np.zeros(len(roi_names))

for idx, (net, parcels) in enumerate(NETWORK_PARCELS.items()):
    valid = [p for p in parcels if p < fmri_mean.shape[1]]
    roi_fmri = fmri_mean[sub_idx][:, valid]
    roi_rdm = compute_rdm(roi_fmri)
    roi_tri = rdm_upper_tri(roi_rdm)

    r_cat, _ = spearmanr(roi_tri, cat_tri)
    r_dim, _ = spearmanr(roi_tri, dim_tri)
    r_va, _ = spearmanr(roi_tri, va_tri)

    rsa_roi_cat[idx] = r_cat
    rsa_roi_dim[idx] = r_dim
    rsa_roi_va[idx] = r_va

print(f"\n{'Network':<15s} {'Cat ρ':>7s} {'Dim ρ':>7s} {'VA ρ':>7s} {'Cat>Dim?':>9s}")
print("-"*50)
for idx, net in enumerate(roi_names):
    cd = "YES" if rsa_roi_cat[idx] > rsa_roi_dim[idx] else "no"
    print(f"{net:<15s} {rsa_roi_cat[idx]:7.4f} {rsa_roi_dim[idx]:7.4f} {rsa_roi_va[idx]:7.4f} {cd:>9s}")

# ── Subject-level consistency ─────────────────────────────────────────────
print("\n" + "="*70)
print("SUBJECT-LEVEL RSA CONSISTENCY")
print("="*70)

rsa_subj_cat = np.zeros(5)
rsa_subj_dim = np.zeros(5)
for s in range(5):
    brain_s = compute_rdm(fmri[s, sub_idx])
    brain_s_tri = rdm_upper_tri(brain_s)
    rsa_subj_cat[s], _ = spearmanr(brain_s_tri, cat_tri)
    rsa_subj_dim[s], _ = spearmanr(brain_s_tri, dim_tri)

print(f"\n  Subject-level RSA:")
for s in range(5):
    print(f"    S{s+1}: cat ρ={rsa_subj_cat[s]:.4f}, dim ρ={rsa_subj_dim[s]:.4f}")
print(f"  Mean: cat ρ={rsa_subj_cat.mean():.4f} ± {rsa_subj_cat.std():.4f}")
print(f"  Mean: dim ρ={rsa_subj_dim.mean():.4f} ± {rsa_subj_dim.std():.4f}")

# ── Save ──────────────────────────────────────────────────────────────────
np.savez(OUT / 'ch1e_rsa.npz',
    # Group RSA
    rsa_cat=rsa_cat, rsa_dim=rsa_dim, rsa_va=rsa_va, rsa_all=rsa_all,
    # Per-emotion RSA
    rsa_per_emo=rsa_per_emo,
    p_per_emo=p_per_emo,
    # ROI RSA
    rsa_roi_cat=rsa_roi_cat,
    rsa_roi_dim=rsa_roi_dim,
    rsa_roi_va=rsa_roi_va,
    roi_names=np.array(roi_names),
    # Subject
    rsa_subj_cat=rsa_subj_cat,
    rsa_subj_dim=rsa_subj_dim,
    # Meta
    all_labels=np.array(ALL_LABELS),
    n_subsample=N_SUB,
)
print(f"\nSaved → {OUT}/ch1e_rsa.npz")
print("Done.")
