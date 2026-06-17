"""
Chapter 2-1: Variance Partitioning (Banded Ridge)

핵심 분석: fMRI의 감정 디코딩에서 AI가 설명하는 부분과 못하는 부분 분리.

방법 (Du 2023 / Horikawa 2020 방식):
  Feature sets:
    AI:       V-JEPA2 (1408) 또는 CLIP (512)
    Emotion:  34 cat + 14 dim = 48 targets (이건 output이 아니라 confound)
    Visual:   vision features (1000)
    Semantic: semantic features (73)

  Banded Ridge: 각 feature set에 별도 alpha → unique variance 추정

  하지만 우리 질문은 "Brain→Behavior에서 AI가 설명하는/못하는 부분"이므로:

  Step 1: fMRI 전체 → emotion decoding (R² = total) — Ch1에서 완료
  Step 2: fMRI에서 AI가 설명하는 성분만 → emotion decoding (R² = AI-shared)
  Step 3: fMRI에서 AI가 설명 못하는 성분 → emotion decoding (R² = AI-unique = ???)

  Confound control: visual + semantic features도 고려

  Variance Partitioning:
    R²(AI only) — AI embedding만으로 fMRI 얼마나 설명?
    R²(AI + Visual) — AI + 시각 특성?
    R²(AI + Visual + Semantic) — 전부?
    R²(fMRI) - R²(위 전부) = 뇌 고유 (???), 어떤 feature로도 설명 안 되는 부분

주의: 단순 residual(fMRI - predicted)이 아닌 cross-validated variance partitioning.
"""

import numpy as np
import scipy.io as sio
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

# ── Load ──────────────────────────────────────────────────────────────────
print("Loading data...")
fmri = np.load(BASE / "raw_fmri_results/fmri_raw.npy").astype(np.float64)[:, :2185, :]
fmri_mean = fmri.mean(axis=0)  # (2185, 450)

# AI embeddings
vjepa = np.load(BASE / "video_embeddings/vjepa2_embeddings.npy").astype(np.float64)[:2185]
clip_emb = np.load(BASE / "video_embeddings/clip_embeddings.npy").astype(np.float64)[:2185]

# Emotion targets
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

# Visual + Semantic features (Horikawa/Du 방식)
vis_feat = sio.loadmat(BASE / "feature/vision.mat")['L'][0, 0]['feat'][:2185]  # (2185, 1000)
sem_feat = sio.loadmat(BASE / "feature/semantic.mat")['L'][0, 0]['feat'][:2185]  # (2185, 73)

print(f"fMRI: {fmri_mean.shape}")
print(f"V-JEPA2: {vjepa.shape}, CLIP: {clip_emb.shape}")
print(f"Vision: {vis_feat.shape}, Semantic: {sem_feat.shape}")
print(f"Targets: {all_targets.shape}")

# ── Decoding function ─────────────────────────────────────────────────────
alphas = np.logspace(-2, 10, 20)

def decode_from_features(brain_data, feature_data, targets, label=""):
    """
    brain_data에서 feature_data로 설명되는 성분 vs 안 되는 성분 분리하여 디코딩.

    Returns:
      r_total: fMRI 전체 → emotion (각 target의 r)
      r_shared: fMRI 중 feature가 설명하는 부분 → emotion
      r_unique: fMRI 중 feature가 설명 못하는 부분 → emotion
      fmri_var_explained: feature가 fMRI의 몇 %를 설명하는가
    """
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    n = brain_data.shape[0]
    n_targets = targets.shape[1]

    # Cross-validated fMRI decomposition
    # 각 fold에서: feature → fMRI regression 학습 → test에서 predicted/residual 구함
    fmri_predicted = np.zeros_like(brain_data)
    fmri_residual = np.zeros_like(brain_data)

    for train_idx, test_idx in kf.split(brain_data):
        sc_f = StandardScaler()
        feat_tr = sc_f.fit_transform(feature_data[train_idx])
        feat_te = sc_f.transform(feature_data[test_idx])

        # For each parcel, predict from features
        for p in range(brain_data.shape[1]):
            ridge = RidgeCV(alphas=alphas)
            ridge.fit(feat_tr, brain_data[train_idx, p])
            fmri_predicted[test_idx, p] = ridge.predict(feat_te)

    fmri_residual = brain_data - fmri_predicted

    # fMRI variance explained by features
    total_var = np.var(brain_data, axis=0).sum()
    resid_var = np.var(fmri_residual, axis=0).sum()
    var_explained = 1 - resid_var / total_var

    # Decode emotion from: total, shared (predicted), unique (residual)
    r_total = np.zeros(n_targets)
    r_shared = np.zeros(n_targets)
    r_unique = np.zeros(n_targets)

    for t in range(n_targets):
        y = targets[:, t]

        # Total: fMRI → emotion (same as Ch1)
        y_pred_total = np.zeros(n)
        for train_idx, test_idx in kf.split(brain_data):
            sc = StandardScaler()
            X_tr = sc.fit_transform(brain_data[train_idx])
            X_te = sc.transform(brain_data[test_idx])
            ridge = RidgeCV(alphas=alphas)
            ridge.fit(X_tr, y[train_idx])
            y_pred_total[test_idx] = ridge.predict(X_te)
        r_total[t], _ = pearsonr(y, y_pred_total)

        # Shared: predicted fMRI → emotion
        y_pred_shared = np.zeros(n)
        for train_idx, test_idx in kf.split(fmri_predicted):
            sc = StandardScaler()
            X_tr = sc.fit_transform(fmri_predicted[train_idx])
            X_te = sc.transform(fmri_predicted[test_idx])
            ridge = RidgeCV(alphas=alphas)
            ridge.fit(X_tr, y[train_idx])
            y_pred_shared[test_idx] = ridge.predict(X_te)
        r_shared[t], _ = pearsonr(y, y_pred_shared)

        # Unique: residual fMRI → emotion (= ???)
        y_pred_unique = np.zeros(n)
        for train_idx, test_idx in kf.split(fmri_residual):
            sc = StandardScaler()
            X_tr = sc.fit_transform(fmri_residual[train_idx])
            X_te = sc.transform(fmri_residual[test_idx])
            ridge = RidgeCV(alphas=alphas)
            ridge.fit(X_tr, y[train_idx])
            y_pred_unique[test_idx] = ridge.predict(X_te)
        r_unique[t], _ = pearsonr(y, y_pred_unique)

    return r_total, r_shared, r_unique, var_explained

# ── Run for each AI model ─────────────────────────────────────────────────
results = {}

for model_name, model_feat in [("V-JEPA2", vjepa), ("CLIP", clip_emb)]:
    print(f"\n{'='*70}")
    print(f"AI LENS: {model_name} ({model_feat.shape[1]}d)")
    print(f"{'='*70}")

    r_t, r_s, r_u, var_exp = decode_from_features(fmri_mean, model_feat, all_targets, model_name)

    print(f"\n  fMRI variance explained by {model_name}: {var_exp*100:.1f}%")
    print(f"\n  {'Target':<25s} {'Total r':>8s} {'Shared r':>9s} {'Unique r':>9s} {'Type':>5s}")
    print(f"  {'-'*58}")
    for i in np.argsort(r_u)[::-1][:20]:
        t = "cat" if i < 34 else "dim"
        print(f"  {ALL_LABELS[i]:<25s} {r_t[i]:8.4f} {r_s[i]:9.4f} {r_u[i]:9.4f} {t:>5s}")

    cat_t = r_t[:34].mean(); dim_t = r_t[34:].mean()
    cat_s = r_s[:34].mean(); dim_s = r_s[34:].mean()
    cat_u = r_u[:34].mean(); dim_u = r_u[34:].mean()

    print(f"\n  {'':>25s} {'Total':>8s} {'Shared':>9s} {'Unique':>9s}")
    print(f"  {'Cat mean r':<25s} {cat_t:8.4f} {cat_s:9.4f} {cat_u:9.4f}")
    print(f"  {'Dim mean r':<25s} {dim_t:8.4f} {dim_s:9.4f} {dim_u:9.4f}")
    print(f"  {'Cat/Dim':<25s} {cat_t/max(dim_t,1e-10):8.3f} {cat_s/max(dim_s,1e-10):9.3f} {cat_u/max(dim_u,1e-10):9.3f}")

    # ⚠️ Critical check
    if cat_u > 0.05:
        print(f"\n  ✓ AI-unique에서 범주 감정 디코딩됨 → ???가 존재!")
    elif cat_u > 0.01:
        print(f"\n  △ AI-unique에서 약한 범주 감정 디코딩 → ??? 약하게 존재")
    else:
        print(f"\n  ✗ AI-unique에서 범주 감정 디코딩 안 됨 → ??? 없을 수 있음")

    results[model_name] = {
        'r_total': r_t, 'r_shared': r_s, 'r_unique': r_u,
        'var_explained': var_exp
    }

# ── 중간 저장 (V-JEPA2 + CLIP 결과) ──────────────────────────────────────
print("\nSaving intermediate results (before confound)...")
save_dict = {'all_labels': np.array(ALL_LABELS)}
for key, val in results.items():
    safe_key = key.replace('+', '_plus_')
    for metric, arr in val.items():
        if isinstance(arr, np.ndarray):
            save_dict[f'{safe_key}_{metric}'] = arr
        else:
            save_dict[f'{safe_key}_{metric}'] = np.array([arr])
np.savez(OUT / 'ch2_1_variance_partitioning.npz', **save_dict)
print(f"Saved intermediate → {OUT}/ch2_1_variance_partitioning.npz")

# ── Visual + Semantic confound control ────────────────────────────────────
print(f"\n{'='*70}")
print("CONFOUND CONTROL: AI + Visual + Semantic")
print(f"{'='*70}")

for model_name, model_feat in [("V-JEPA2", vjepa), ("CLIP", clip_emb)]:
    print(f"\n--- {model_name} + Vision + Semantic ---")
    combined = np.hstack([model_feat, vis_feat, sem_feat])
    print(f"  Combined features: {combined.shape}")

    _, _, r_u_all, var_all = decode_from_features(fmri_mean, combined, all_targets)

    cat_u_all = r_u_all[:34].mean()
    dim_u_all = r_u_all[34:].mean()

    print(f"  fMRI variance explained: {var_all*100:.1f}%")
    print(f"  Unique (after removing AI+Vis+Sem):")
    print(f"    Cat mean r: {cat_u_all:.4f}")
    print(f"    Dim mean r: {dim_u_all:.4f}")

    # Compare
    cat_u_ai = results[model_name]['r_unique'][:34].mean()
    print(f"  Compare: AI-only unique cat r={cat_u_ai:.4f} → AI+Vis+Sem unique cat r={cat_u_all:.4f}")

    results[f"{model_name}+Vis+Sem"] = {
        'r_unique': r_u_all, 'var_explained': var_all
    }

# ── Save ──────────────────────────────────────────────────────────────────
save_dict = {'all_labels': np.array(ALL_LABELS)}
for key, val in results.items():
    safe_key = key.replace('+', '_plus_')
    for metric, arr in val.items():
        if isinstance(arr, np.ndarray):
            save_dict[f'{safe_key}_{metric}'] = arr
        else:
            save_dict[f'{safe_key}_{metric}'] = np.array([arr])

np.savez(OUT / 'ch2_1_variance_partitioning.npz', **save_dict)
print(f"\nSaved → {OUT}/ch2_1_variance_partitioning.npz")
print("Done.")
