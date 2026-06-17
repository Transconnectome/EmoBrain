"""
Chapter 1 보완: Noise Ceiling (올바른 방법)

Noise Ceiling = subject 간 fMRI 반응의 일관성이 결정하는 디코딩 상한.

방법 (Huth et al., Horikawa 방식):
  Upper NC: 모든 subject 포함 평균 fMRI → 디코딩 → r
            (자기 자신 포함이라 낙관적, 하지만 이게 현재 Ch1-A 결과)
  Lower NC: Leave-one-subject-out 평균 fMRI → 해당 subject의 실제 반응과 비교

  → 실제로 의미 있는 NC는:
     "subject i의 fMRI로 디코딩한 predicted score"와
     "나머지 subjects의 fMRI로 디코딩한 predicted score"가
     얼마나 일치하는가 = inter-subject consistency of decoding.

  하지만 가장 표준적인 방법:
     각 subject별로 독립 디코딩 → subject별 r 산출
     → subject 간 평균 r = 실제 달성 성능
     → NC = subject 간 fMRI 일관성으로 계산

실용적 NC 계산 (Lage-Castellanos et al. 2019):
  Upper NC: corr(subject_i, mean_all) averaged over subjects
  Lower NC: corr(subject_i, mean_others) averaged over subjects
  이건 fMRI 자체의 일관성이지, 디코딩 성능의 상한.

  디코딩 NC = 이 fMRI 일관성 × target의 예측 가능성
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
N_SUBJECTS = 5

# ── Load ──────────────────────────────────────────────────────────────────
print("Loading data...")
fmri = np.load(BASE / "raw_fmri_results/fmri_raw.npy").astype(np.float64)[:, :2185, :]

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

fmri_mean = fmri.mean(axis=0)
print(f"fMRI: {fmri.shape}, Targets: {all_targets.shape}")

# ── Decode function ───────────────────────────────────────────────────────
def decode_cv(X, y, n_splits=5):
    alphas = np.logspace(-2, 10, 20)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    y_pred = np.zeros_like(y)
    for train_idx, test_idx in kf.split(X):
        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X[train_idx])
        X_te = scaler.transform(X[test_idx])
        ridge = RidgeCV(alphas=alphas)
        ridge.fit(X_tr, y[train_idx])
        y_pred[test_idx] = ridge.predict(X_te)
    r, _ = pearsonr(y, y_pred)
    return r, y_pred

# ── Method 1: Subject-level decoding NC ──────────────────────────────────
# 각 subject 독립 디코딩 → subject별 r → 이것의 평균이 "실제 개인 수준 성능"
# Group mean 디코딩 r은 이 개인 수준보다 높음 (noise averaging)
# NC = group r이 개인 r 대비 얼마나 좋아졌나?

print("\n" + "="*70)
print("METHOD 1: Subject-level decoding")
print("="*70)

r_subject = np.zeros((N_SUBJECTS, N_TARGETS))
for s in range(N_SUBJECTS):
    print(f"  Subject {s+1}...")
    for t in range(N_TARGETS):
        r_s, _ = decode_cv(fmri[s], all_targets[:, t])
        r_subject[s, t] = r_s

r_subject_mean = r_subject.mean(axis=0)  # (48,)

# ── Method 2: LOO NC (Leave-One-Subject-Out 평균으로 디코딩) ──────────────
# 4명 평균 fMRI → 디코딩 → r
# 자기를 빠진 평균이니까 group mean보다 보수적

print("\n" + "="*70)
print("METHOD 2: LOO Noise Ceiling")
print("="*70)

r_loo = np.zeros((N_SUBJECTS, N_TARGETS))
for s in range(N_SUBJECTS):
    print(f"  LOO Subject {s+1}...")
    fmri_loo = np.delete(fmri, s, axis=0).mean(axis=0)  # 4명 평균
    for t in range(N_TARGETS):
        r_l, _ = decode_cv(fmri_loo, all_targets[:, t])
        r_loo[s, t] = r_l

lower_nc = r_loo.mean(axis=0)  # (48,) — LOO NC

# ── Method 3: fMRI ISC (Inter-Subject Correlation) ───────────────────────
# fMRI 자체의 subject 간 일관성 → 디코딩의 이론적 상한
# 각 parcel에서 subject 간 correlation → 평균

print("\n" + "="*70)
print("METHOD 3: fMRI Inter-Subject Correlation")
print("="*70)

isc_per_parcel = np.zeros(fmri.shape[2])
for p in range(fmri.shape[2]):
    rs = []
    for i in range(N_SUBJECTS):
        for j in range(i+1, N_SUBJECTS):
            r, _ = pearsonr(fmri[i, :, p], fmri[j, :, p])
            rs.append(r)
    isc_per_parcel[p] = np.mean(rs)

print(f"  Mean ISC across parcels: {isc_per_parcel.mean():.4f}")
print(f"  ISC range: [{isc_per_parcel.min():.4f}, {isc_per_parcel.max():.4f}]")

# ── Group results (from Ch1-A) ────────────────────────────────────────────
d = np.load(OUT / 'ch1_brain_to_behavior.npz', allow_pickle=True)
r_group = d['r_group']

# ── Upper NC = group mean r (이건 그대로, 상한) ──────────────────────────
upper_nc = r_group  # group mean은 상한의 역할

# ── Normalized: group r / lower NC ────────────────────────────────────────
# lower NC = LOO mean. group r이 이보다 높으면 = group averaging 효과
# 정규화 = group_r / lower_nc → 1에 가까우면 LOO와 비슷, >1이면 group이 더 좋음

# 더 의미있는 정규화: subject r / group r
# = "개인이 group 대비 얼마나 달성하는가"
# → 낮으면: group averaging이 많이 도움 = noise 많음

ratio_subj_to_group = r_subject_mean / (r_group + 1e-10)  # 개인/group

print("\n" + "="*70)
print("NOISE CEILING SUMMARY")
print("="*70)

print(f"\n{'Target':<25s} {'Group r':>8s} {'SubjMean':>9s} {'LOO NC':>7s} {'S/G%':>6s} {'Type':>5s}")
print("-"*63)
for i in np.argsort(r_group)[::-1]:
    t = "cat" if i < 34 else "dim"
    sg = ratio_subj_to_group[i] * 100
    print(f"{ALL_LABELS[i]:<25s} {r_group[i]:8.4f} {r_subject_mean[i]:9.4f} {lower_nc[i]:7.4f} {sg:5.1f}% {t:>5s}")

# Cat vs Dim with NC
print(f"\n{'':>20s} {'Group r':>8s} {'Subj r':>8s} {'LOO NC':>8s} {'S/G ratio':>9s}")
print("-"*55)
for name, idx_range in [("Category (34)", slice(0,34)), ("Dimension (14)", slice(34,48))]:
    gr = r_group[idx_range].mean()
    sr = r_subject_mean[idx_range].mean()
    lr = lower_nc[idx_range].mean()
    sg = sr / max(gr, 1e-10)
    print(f"{name:<20s} {gr:8.4f} {sr:8.4f} {lr:8.4f} {sg:9.3f}")

cat_sg = r_subject_mean[:34].mean() / max(r_group[:34].mean(), 1e-10)
dim_sg = r_subject_mean[34:].mean() / max(r_group[34:].mean(), 1e-10)
print(f"\n  Cat subject/group ratio: {cat_sg:.3f}")
print(f"  Dim subject/group ratio: {dim_sg:.3f}")
if cat_sg > dim_sg:
    print(f"  → Cat이 group averaging으로부터 덜 이득 (개인 수준에서도 안정적)")
else:
    print(f"  → Dim이 group averaging으로부터 덜 이득")

# Subject-level Cat/Dim
cat_subj = r_subject[:, :34].mean(axis=1)
dim_subj = r_subject[:, 34:].mean(axis=1)
print(f"\n  Subject-level Cat/Dim ratios:")
for s in range(N_SUBJECTS):
    ratio = cat_subj[s] / max(dim_subj[s], 1e-10)
    print(f"    S{s+1}: cat={cat_subj[s]:.4f}, dim={dim_subj[s]:.4f}, C/D={ratio:.3f}")

# ── Save ──────────────────────────────────────────────────────────────────
np.savez(OUT / 'ch1_noise_ceiling.npz',
    r_group=r_group,
    r_subject=r_subject,           # (5, 48)
    r_subject_mean=r_subject_mean, # (48,)
    lower_nc=lower_nc,             # (48,) LOO NC
    upper_nc=upper_nc,             # (48,) = group r
    ratio_subj_to_group=ratio_subj_to_group,
    isc_per_parcel=isc_per_parcel, # (450,)
    all_labels=np.array(ALL_LABELS),
)
print(f"\nSaved → {OUT}/ch1_noise_ceiling.npz")
print("Done.")
