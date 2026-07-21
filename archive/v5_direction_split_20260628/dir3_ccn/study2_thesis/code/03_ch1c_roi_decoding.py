"""
Chapter 1-C: ROI별 감정 디코딩 지도

각 ROI(network)에서 48 targets을 독립적으로 디코딩.
"어떤 뇌 영역이 어떤 감정을 인코딩하는가?"

Cortical: Schaefer 400 → Yeo 7 networks
  Vis(61), SomMot(77), DorsAttn(46), SalVentAttn(47),
  Limbic(26), Cont(52), Default(91)

Subcortical: Tian S3 50 parcels
  → 기존 fmri_raw.npy의 parcel 401-450

각 network의 parcels만 사용하여 디코딩 → network별 R², Pearson r.
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

# ── Define ROIs ───────────────────────────────────────────────────────────
# Schaefer 400: parcels 0-399 (cortical)
# Tian S3 50: parcels 400-449 (subcortical)
# Network assignment from Yeo 7 networks

NETWORK_PARCELS = {
    'Vis': list(range(0, 31)) + list(range(200, 230)),           # ~61
    'SomMot': list(range(31, 68)) + list(range(230, 270)),       # ~77
    'DorsAttn': list(range(68, 91)) + list(range(270, 293)),     # ~46
    'SalVentAttn': list(range(91, 113)) + list(range(293, 318)), # ~47
    'Limbic': list(range(113, 126)) + list(range(318, 331)),     # ~26
    'Cont': list(range(126, 148)) + list(range(331, 361)),       # ~52
    'Default': list(range(148, 200)) + list(range(361, 400)),    # ~91
    'Subcortical': list(range(400, 450)),                         # 50
}

# ── Load data ─────────────────────────────────────────────────────────────
print("Loading data...")
fmri = np.load(BASE / "raw_fmri_results/fmri_raw.npy").astype(np.float64)  # (5, 2196, 450)

meta = pd.read_csv(Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv"))
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

meta14 = pd.read_csv(Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_14dims.csv"))
meta14 = meta14.sort_values('stim_idx').reset_index(drop=True)

# Remove repeats
UNIQUE = np.arange(2185)
fmri = fmri[:, UNIQUE, :]
meta = meta.iloc[UNIQUE].reset_index(drop=True)
meta14 = meta14.iloc[UNIQUE].reset_index(drop=True)

fmri_mean = fmri.mean(axis=0)  # (2185, 450)

cat_scores = meta[[f"score_{i}" for i in range(34)]].values.astype(np.float64)
dim_cols = ['arousal_score', 'valence_score', 'dominance_score',
            'approach_score', 'attention_score', 'certainty_score', 'commitment_score',
            'control_score', 'effort_score', 'fairness_score', 'identity_score',
            'obstruction_score', 'safety_score', 'upswing_score']
dim_scores = meta14[dim_cols].values.astype(np.float64)
all_targets = np.hstack([cat_scores, dim_scores])

print(f"fMRI: {fmri_mean.shape}, Targets: {all_targets.shape}")

# Verify network parcel counts
for net, parcels in NETWORK_PARCELS.items():
    valid = [p for p in parcels if p < fmri_mean.shape[1]]
    print(f"  {net}: {len(valid)} parcels")

# ── Decode function ───────────────────────────────────────────────────────
def decode_roi(fmri_data, parcel_indices, targets, n_splits=5):
    """Decode 48 targets from a subset of parcels. Returns r, r2, y_pred_all."""
    valid_idx = [p for p in parcel_indices if p < fmri_data.shape[1]]
    X = fmri_data[:, valid_idx]

    if X.shape[1] == 0:
        return np.zeros(N_TARGETS), np.zeros(N_TARGETS), np.zeros_like(targets)

    alphas = np.logspace(-2, 10, 20)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

    r_vals = np.zeros(N_TARGETS)
    r2_vals = np.zeros(N_TARGETS)
    y_pred_all = np.zeros_like(targets)

    for t in range(N_TARGETS):
        y = targets[:, t]
        y_pred = np.zeros_like(y)

        for train_idx, test_idx in kf.split(X):
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X[train_idx])
            X_test = scaler.transform(X[test_idx])

            ridge = RidgeCV(alphas=alphas)
            ridge.fit(X_train, y[train_idx])
            y_pred[test_idx] = ridge.predict(X_test)

        r, _ = pearsonr(y, y_pred)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r2 = max(1 - ss_res / ss_tot, 0.0) if ss_tot > 0 else 0.0

        r_vals[t] = r
        r2_vals[t] = r2
        y_pred_all[:, t] = y_pred

    return r_vals, r2_vals, y_pred_all


def video_identification_fast(y_true, y_pred):
    """Pairwise video identification accuracy."""
    n = y_true.shape[0]
    pred_n = (y_pred - y_pred.mean(1, keepdims=True)) / (y_pred.std(1, keepdims=True) + 1e-10)
    true_n = (y_true - y_true.mean(1, keepdims=True)) / (y_true.std(1, keepdims=True) + 1e-10)
    corr_mat = pred_n @ true_n.T / y_pred.shape[1]
    diag = np.diag(corr_mat)
    pairwise_correct = (corr_mat < diag[:, None]).sum(axis=1)
    return pairwise_correct.mean() / (n - 1)

# ── ROI-wise decoding ─────────────────────────────────────────────────────
print("\n" + "="*70)
print("ROI-WISE DECODING (8 networks × 48 targets)")
print("="*70)

roi_names = list(NETWORK_PARCELS.keys())
n_rois = len(roi_names)

r_roi = np.zeros((n_rois, N_TARGETS))
r2_roi = np.zeros((n_rois, N_TARGETS))
vid_id_roi = np.zeros((n_rois, 3))  # cat, dim, all

for idx, (net, parcels) in enumerate(NETWORK_PARCELS.items()):
    print(f"\n[{idx+1}/{n_rois}] {net} ({len(parcels)} parcels)...")
    r_vals, r2_vals, y_pred = decode_roi(fmri_mean, parcels, all_targets)
    r_roi[idx] = r_vals
    r2_roi[idx] = r2_vals

    # Video identification
    cat_acc = video_identification_fast(all_targets[:, :34], y_pred[:, :34])
    dim_acc = video_identification_fast(all_targets[:, 34:], y_pred[:, 34:])
    all_acc = video_identification_fast(all_targets, y_pred)
    vid_id_roi[idx] = [cat_acc, dim_acc, all_acc]

    cat_r = r_vals[:34].mean()
    dim_r = r_vals[34:].mean()
    top3 = np.argsort(r_vals)[::-1][:3]
    print(f"  cat r={cat_r:.4f}, dim r={dim_r:.4f}, Cat/Dim={cat_r/max(dim_r,1e-10):.3f}")
    print(f"  Vid ID: cat={cat_acc*100:.1f}%, dim={dim_acc*100:.1f}%, all={all_acc*100:.1f}%")
    print(f"  Top 3: {ALL_LABELS[top3[0]]}({r_vals[top3[0]]:.3f}), "
          f"{ALL_LABELS[top3[1]]}({r_vals[top3[1]]:.3f}), "
          f"{ALL_LABELS[top3[2]]}({r_vals[top3[2]]:.3f})")

# ── Summary ───────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("SUMMARY: Network × Emotion")
print("="*70)

print(f"\n{'Network':<15s} {'#P':>4s} {'Cat r':>7s} {'Dim r':>7s} {'C/D':>5s} {'VidID cat':>9s} {'VidID dim':>9s} {'Top emotion':>25s} {'r':>6s}")
print("-"*95)
for idx, net in enumerate(roi_names):
    n_p = len(NETWORK_PARCELS[net])
    cat_r = r_roi[idx, :34].mean()
    dim_r = r_roi[idx, 34:].mean()
    ratio = cat_r / max(dim_r, 1e-10)
    top_i = np.argmax(r_roi[idx])
    print(f"{net:<15s} {n_p:>4d} {cat_r:>7.4f} {dim_r:>7.4f} {ratio:>5.2f} {vid_id_roi[idx,0]*100:>8.1f}% {vid_id_roi[idx,1]*100:>8.1f}% {ALL_LABELS[top_i]:>25s} {r_roi[idx, top_i]:>6.3f}")

# Horikawa prediction: transmodal (Default, SalVentAttn) > unimodal (Vis, SomMot)
print("\n--- Horikawa 예측 검증: transmodal > unimodal ---")
unimodal = ['Vis', 'SomMot']
transmodal = ['Default', 'SalVentAttn', 'Limbic']
uni_r = np.mean([r_roi[roi_names.index(n), :34].mean() for n in unimodal])
trans_r = np.mean([r_roi[roi_names.index(n), :34].mean() for n in transmodal])
print(f"  Unimodal (Vis+SomMot) cat r:      {uni_r:.4f}")
print(f"  Transmodal (Default+SalVA+Limb) r: {trans_r:.4f}")
print(f"  Transmodal > Unimodal? {'YES' if trans_r > uni_r else 'NO'}")

# ── Full heatmap data ─────────────────────────────────────────────────────
print("\n--- Full heatmap: Network × Target (Pearson r) ---")
print(f"{'':>25s}", end="")
for net in roi_names:
    print(f" {net:>10s}", end="")
print()
for t in range(N_TARGETS):
    print(f"{ALL_LABELS[t]:<25s}", end="")
    for idx in range(n_rois):
        print(f" {r_roi[idx, t]:>10.3f}", end="")
    print()

# ── Save ──────────────────────────────────────────────────────────────────
np.savez(OUT / 'ch1c_roi_decoding.npz',
    r_roi=r_roi,           # (8, 48)
    r2_roi=r2_roi,         # (8, 48)
    vid_id_roi=vid_id_roi, # (8, 3) — cat, dim, all
    roi_names=np.array(roi_names),
    all_labels=np.array(ALL_LABELS),
)
print(f"\nSaved → {OUT}/ch1c_roi_decoding.npz")
print("Done.")
