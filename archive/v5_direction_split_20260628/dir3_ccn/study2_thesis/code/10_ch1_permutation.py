"""
Chapter 1 보완: Permutation test (48 targets)

각 target에 대해 emotion label shuffle → null r 분포 생성 → p-value.
FDR correction (BH, q<0.05).
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
N_PERM = 1000

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
all_targets = np.hstack([cat_scores, dim_scores])

# Load observed r from Ch1-A
d1 = np.load(OUT / 'ch1_brain_to_behavior.npz', allow_pickle=True)
r_obs = d1['r_group']

print(f"fMRI: {fmri_mean.shape}, Targets: {all_targets.shape}")
print(f"Permutations: {N_PERM}")

# ── Permutation test ──────────────────────────────────────────────────────
alphas = np.logspace(-2, 10, 20)
kf = KFold(n_splits=5, shuffle=True, random_state=42)
rng = np.random.default_rng(42)

r_null = np.zeros((N_TARGETS, N_PERM))

for t in range(N_TARGETS):
    if (t + 1) % 10 == 0 or t == 0:
        print(f"  Target {t+1}/{N_TARGETS}: {ALL_LABELS[t]}...")

    y_true = all_targets[:, t]

    for p in range(N_PERM):
        y_shuf = rng.permutation(y_true)
        y_pred = np.zeros_like(y_shuf)

        for train_idx, test_idx in kf.split(fmri_mean):
            sc = StandardScaler()
            X_tr = sc.fit_transform(fmri_mean[train_idx])
            X_te = sc.transform(fmri_mean[test_idx])
            ridge = RidgeCV(alphas=alphas)
            ridge.fit(X_tr, y_shuf[train_idx])
            y_pred[test_idx] = ridge.predict(X_te)

        r_null[t, p], _ = pearsonr(y_shuf, y_pred)

# ── P-values ──────────────────────────────────────────────────────────────
p_values = np.array([(r_null[t] >= r_obs[t]).mean() for t in range(N_TARGETS)])

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

q_values = fdr_bh(p_values)

# ── Results ───────────────────────────────────────────────────────────────
print("\n" + "="*70)
print(f"PERMUTATION TEST RESULTS (n={N_PERM})")
print("="*70)

print(f"\n| {'Target':<25s} | {'r':>7s} | {'p':>7s} | {'q(FDR)':>7s} | {'Sig':>4s} | {'Type':>5s} |")
print(f"|{'-'*27}|{'-'*9}|{'-'*9}|{'-'*9}|{'-'*6}|{'-'*7}|")
for i in np.argsort(r_obs)[::-1]:
    t = "cat" if i < 34 else "dim"
    sig = "***" if q_values[i] < 0.001 else "**" if q_values[i] < 0.01 else "*" if q_values[i] < 0.05 else ""
    print(f"| {ALL_LABELS[i]:<25s} | {r_obs[i]:7.4f} | {p_values[i]:7.4f} | {q_values[i]:7.4f} | {sig:>4s} | {t:>5s} |")

n_sig = (q_values < 0.05).sum()
print(f"\nSignificant (FDR q<0.05): {n_sig}/48")
print(f"  Cat: {(q_values[:34] < 0.05).sum()}/34")
print(f"  Dim: {(q_values[34:] < 0.05).sum()}/14")

# ── Save ──────────────────────────────────────────────────────────────────
np.savez(OUT / 'ch1_permutation.npz',
    r_obs=r_obs,
    r_null=r_null,
    p_values=p_values,
    q_values=q_values,
    n_perm=N_PERM,
    all_labels=np.array(ALL_LABELS),
)
print(f"\nSaved → {OUT}/ch1_permutation.npz")
print("Done.")
