"""
Chapter 1: Brain → Behavior (48 targets)

Horikawa (2020) 방식 디코딩 + 14 dim 확장.
"뇌에서 감정이 얼마나 디코딩되는가?" — baseline 확립.

Input:  Raw fMRI (5명, 2185 unique videos, 450 Schaefer parcels)
Output: 48 targets (34 emotion categories + 14 affective dimensions)

Metrics:
  - Pearson r (Horikawa 방식)
  - R² (추가)
  - Video identification accuracy (pairwise, Horikawa 방식)

11개 반복 비디오(stimulus_2186~2196) 제거.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
OUT  = BASE / "main/results"
OUT.mkdir(parents=True, exist_ok=True)

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
N_TARGETS = 48

# ── Load ──────────────────────────────────────────────────────────────────
print("Loading data...")
fmri_all = np.load(BASE / "raw_fmri_results/fmri_raw.npy").astype(np.float64)  # (5, 2196, 450)

meta = pd.read_csv(Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv"))
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

meta14 = pd.read_csv(Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv"))
meta14 = meta14.sort_values('stim_idx').reset_index(drop=True)

# Remove 11 repeat videos
UNIQUE = np.arange(2185)
fmri_all = fmri_all[:, UNIQUE, :]
meta = meta.iloc[UNIQUE].reset_index(drop=True)
meta14 = meta14.iloc[UNIQUE].reset_index(drop=True)

cat_scores = meta[[f"score_{i}" for i in range(34)]].values.astype(np.float64)  # (2185, 34)
dim_cols = ['arousal_score', 'valence_score', 'dominance_score',
            'approach_score', 'attention_score', 'certainty_score', 'commitment_score',
            'control_score', 'effort_score', 'fairness_score', 'identity_score',
            'obstruction_score', 'safety_score', 'upswing_score']
dim_scores = meta14[dim_cols].values.astype(np.float64)  # (2185, 14)
all_targets = np.hstack([cat_scores, dim_scores])  # (2185, 48)

N_VIDEOS = len(UNIQUE)
N_SUBJECTS = 5
print(f"fMRI: ({N_SUBJECTS}, {N_VIDEOS}, {fmri_all.shape[2]})")
print(f"Targets: {all_targets.shape} (34 cat + 14 dim)")

# ── Decode function (Horikawa 방식: RidgeCV + Pearson r) ─────────────────
def decode_cv(X, y, n_splits=5):
    """
    Ridge regression with CV alpha selection.
    Returns predicted y for all samples (out-of-fold predictions).
    """
    alphas = np.logspace(-2, 10, 20)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    y_pred = np.zeros_like(y)

    for train_idx, test_idx in kf.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train = y[train_idx]

        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        ridge = RidgeCV(alphas=alphas)
        ridge.fit(X_train_s, y_train)
        y_pred[test_idx] = ridge.predict(X_test_s)

    return y_pred

def compute_metrics(y_true, y_pred):
    """Pearson r + R²."""
    r, p = pearsonr(y_true, y_pred)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - y_true.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return r, p, max(r2, 0.0)

def video_identification(y_true_all, y_pred_all):
    """
    Horikawa 방식 pairwise video identification.
    모든 감정의 predicted score 벡터로 비디오 identification.
    각 비디오에 대해 true vs 모든 other → pairwise accuracy.
    """
    n = y_true_all.shape[0]
    correct = 0
    total = 0
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            # true video i의 predicted vs true i, true j
            r_true = np.corrcoef(y_pred_all[i], y_true_all[i])[0, 1]
            r_false = np.corrcoef(y_pred_all[i], y_true_all[j])[0, 1]
            if r_true > r_false:
                correct += 1
            total += 1
    return correct / total if total > 0 else 0.0

def video_identification_fast(y_true_all, y_pred_all):
    """
    Fast version: for each video, compute correlation with all true vectors.
    Accuracy = proportion where self-correlation is highest.
    """
    n = y_true_all.shape[0]
    # Correlation matrix: pred × true
    # Normalize
    pred_n = (y_pred_all - y_pred_all.mean(1, keepdims=True)) / (y_pred_all.std(1, keepdims=True) + 1e-10)
    true_n = (y_true_all - y_true_all.mean(1, keepdims=True)) / (y_true_all.std(1, keepdims=True) + 1e-10)
    corr_mat = pred_n @ true_n.T / y_pred_all.shape[1]  # (n, n)

    # Pairwise accuracy: for each video, is diagonal > each off-diagonal?
    diag = np.diag(corr_mat)  # (n,)
    # For each i, count how many j where corr[i,i] > corr[i,j]
    pairwise_correct = (corr_mat < diag[:, None]).sum(axis=1)  # exclude self
    pairwise_acc = pairwise_correct / (n - 1)
    return pairwise_acc.mean()

# ── Subject-averaged decoding ─────────────────────────────────────────────
print("\n" + "="*65)
print("GROUP DECODING (5-subject averaged fMRI)")
print("="*65)

fmri_mean = fmri_all.mean(axis=0)  # (2185, 450)

r_all = np.zeros(N_TARGETS)
p_all = np.zeros(N_TARGETS)
r2_all = np.zeros(N_TARGETS)
y_pred_all = np.zeros_like(all_targets)  # (2185, 48) for video identification

print("\nDecoding 48 targets (RidgeCV, 5-fold)...")
for t in range(N_TARGETS):
    y_pred = decode_cv(fmri_mean, all_targets[:, t])
    r, p, r2 = compute_metrics(all_targets[:, t], y_pred)
    r_all[t] = r
    p_all[t] = p
    r2_all[t] = r2
    y_pred_all[:, t] = y_pred

# Results table
print(f"\n{'Target':<25s} {'Pearson r':>10s} {'R²':>8s} {'p':>10s} {'Type':>5s}")
print("-"*62)
for i in np.argsort(r_all)[::-1]:
    ttype = "cat" if i < 34 else "dim"
    print(f"{ALL_LABELS[i]:<25s} {r_all[i]:10.4f} {r2_all[i]:8.4f} {p_all[i]:10.2e} {ttype:>5s}")

cat_r = r_all[:34].mean()
dim_r = r_all[34:].mean()
cat_r2 = r2_all[:34].mean()
dim_r2 = r2_all[34:].mean()
print(f"\nCategory mean:  r={cat_r:.4f}, R²={cat_r2:.4f}")
print(f"Dimension mean: r={dim_r:.4f}, R²={dim_r2:.4f}")
print(f"Cat/Dim ratio:  r={cat_r/max(dim_r,1e-10):.3f}, R²={cat_r2/max(dim_r2,1e-10):.3f}")
print(f"Targets with r>0.095 (Horikawa threshold): {(r_all>0.095).sum()}/48")
print(f"Targets with R²>0.01: {(r2_all>0.01).sum()}/48")

# ── Video identification ──────────────────────────────────────────────────
print("\nVideo identification (pairwise)...")

# Category-based
cat_acc = video_identification_fast(all_targets[:, :34], y_pred_all[:, :34])
# Dimension-based
dim_acc = video_identification_fast(all_targets[:, 34:], y_pred_all[:, 34:])
# All 48
all_acc = video_identification_fast(all_targets, y_pred_all)

print(f"  Category (34):   {cat_acc*100:.1f}% (chance 50%)")
print(f"  Dimension (14):  {dim_acc*100:.1f}% (chance 50%)")
print(f"  All (48):        {all_acc*100:.1f}% (chance 50%)")

if cat_acc > dim_acc:
    print(f"  → Category > Dimension (Horikawa와 일관)")
else:
    print(f"  → Dimension ≥ Category")

# ── Subject-level ──────────────────────────────────────────────────────────
print("\n" + "="*65)
print("SUBJECT-LEVEL DECODING")
print("="*65)

r_subj = np.zeros((N_SUBJECTS, N_TARGETS))
r2_subj = np.zeros((N_SUBJECTS, N_TARGETS))

for s in range(N_SUBJECTS):
    print(f"\n  Subject {s+1}...")
    for t in range(N_TARGETS):
        y_pred = decode_cv(fmri_all[s], all_targets[:, t])
        r, p, r2 = compute_metrics(all_targets[:, t], y_pred)
        r_subj[s, t] = r
        r2_subj[s, t] = r2

    cat_r_s = r_subj[s, :34].mean()
    dim_r_s = r_subj[s, 34:].mean()
    n_sig = (r_subj[s] > 0.095).sum()
    print(f"    cat r={cat_r_s:.4f}, dim r={dim_r_s:.4f}, sig(r>0.095)={n_sig}/48")

print(f"\n  Mean across subjects:")
print(f"    cat r={r_subj[:,:34].mean():.4f} ± {r_subj[:,:34].mean(1).std():.4f}")
print(f"    dim r={r_subj[:,34:].mean():.4f} ± {r_subj[:,34:].mean(1).std():.4f}")

# ── Save ──────────────────────────────────────────────────────────────────
np.savez(OUT / 'ch1_brain_to_behavior.npz',
    # Group
    r_group=r_all,
    p_group=p_all,
    r2_group=r2_all,
    y_pred_group=y_pred_all,
    # Video identification
    vid_id_cat=cat_acc,
    vid_id_dim=dim_acc,
    vid_id_all=all_acc,
    # Subject-level
    r_subject=r_subj,
    r2_subject=r2_subj,
    # Targets
    all_targets=all_targets,
    cat_labels=np.array(CAT_LABELS),
    dim_labels=np.array(DIM_LABELS),
    all_labels=np.array(ALL_LABELS),
    n_videos=N_VIDEOS,
)
print(f"\nSaved → {OUT}/ch1_brain_to_behavior.npz")
print("Done.")
