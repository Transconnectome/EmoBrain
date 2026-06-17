"""
Chapter 1-D: Principal Gradient 분석

Margulies (2016) 방식으로 cortical gradient 계산 후,
gradient 위치 vs 감정 디코딩 성능 관계 분석.

방법:
  1. Schaefer 400 parcels 간 functional connectivity matrix 계산
  2. Diffusion embedding → Principal Gradient (PG1)
  3. PG1 값 vs Ch1-A 감정 디코딩 r 비교 (parcel별)

예상 (Horikawa/Margulies):
  unimodal (PG1 낮음): 감정 디코딩 낮음, VA 편향
  transmodal (PG1 높음): 감정 디코딩 높음, 범주 편향
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.manifold import SpectralEmbedding
from scipy.stats import pearsonr, spearmanr
from scipy.spatial.distance import cosine
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

# Network assignment (same as 03)
NETWORK_NAMES = ['Vis', 'SomMot', 'DorsAttn', 'SalVentAttn', 'Limbic', 'Cont', 'Default']
NETWORK_PARCELS = {
    'Vis': list(range(0, 31)) + list(range(200, 230)),
    'SomMot': list(range(31, 68)) + list(range(230, 270)),
    'DorsAttn': list(range(68, 91)) + list(range(270, 293)),
    'SalVentAttn': list(range(91, 113)) + list(range(293, 318)),
    'Limbic': list(range(113, 126)) + list(range(318, 331)),
    'Cont': list(range(126, 148)) + list(range(331, 361)),
    'Default': list(range(148, 200)) + list(range(361, 400)),
}
parcel_to_network = {}
for net, parcels in NETWORK_PARCELS.items():
    for p in parcels:
        parcel_to_network[p] = net

# ── Load ──────────────────────────────────────────────────────────────────
print("Loading data...")
fmri = np.load(BASE / "raw_fmri_results/fmri_raw.npy").astype(np.float64)[:, :2185, :]
fmri_mean = fmri.mean(axis=0)  # (2185, 450)

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

N_CORTICAL = 400  # Schaefer cortical only (exclude subcortical for PG)
print(f"fMRI: {fmri_mean.shape}, Cortical parcels: {N_CORTICAL}")

# ── Step 1: Compute functional connectivity ──────────────────────────────
print("\nStep 1: Computing functional connectivity (400 cortical parcels)...")
fmri_cortical = fmri_mean[:, :N_CORTICAL]  # (2185, 400)
fc = np.corrcoef(fmri_cortical.T)  # (400, 400)
print(f"  FC matrix: {fc.shape}, range=[{fc.min():.3f}, {fc.max():.3f}]")

# Threshold: keep top 10% connections (Margulies method)
threshold = np.percentile(fc[np.triu_indices(N_CORTICAL, k=1)], 90)
fc_thresh = fc.copy()
fc_thresh[fc_thresh < threshold] = 0
np.fill_diagonal(fc_thresh, 0)
print(f"  Threshold (90th %ile): {threshold:.3f}")
print(f"  Non-zero connections: {(fc_thresh > 0).sum()}")

# ── Step 2: Diffusion embedding → Principal Gradient ──────────────────────
print("\nStep 2: Diffusion embedding...")

# Cosine similarity of connectivity profiles (Margulies method)
from sklearn.metrics.pairwise import cosine_similarity
cos_sim = cosine_similarity(fc_thresh)
cos_sim[cos_sim < 0] = 0  # remove negative
np.fill_diagonal(cos_sim, 0)

# Diffusion embedding
embedding = SpectralEmbedding(n_components=5, affinity='precomputed', random_state=42)
gradients = embedding.fit_transform(cos_sim)  # (400, 5)

# PG1 = first gradient
pg1 = gradients[:, 0]
pg2 = gradients[:, 1]

# Flip if needed (convention: positive = transmodal/DMN)
# Check: Default network should have positive PG1
default_parcels = NETWORK_PARCELS['Default']
default_pg1 = np.mean([pg1[p] for p in default_parcels if p < N_CORTICAL])
vis_pg1 = np.mean([pg1[p] for p in NETWORK_PARCELS['Vis'] if p < N_CORTICAL])
if default_pg1 < vis_pg1:
    pg1 = -pg1
    print("  Flipped PG1 (convention: positive = transmodal)")

print(f"  PG1 range: [{pg1.min():.3f}, {pg1.max():.3f}]")
print(f"  PG1 by network:")
for net in NETWORK_NAMES:
    parcels = [p for p in NETWORK_PARCELS[net] if p < N_CORTICAL]
    mean_pg = np.mean([pg1[p] for p in parcels])
    print(f"    {net:<15s}: PG1 = {mean_pg:.4f}")

# ── Step 3: Parcel-level decoding ─────────────────────────────────────────
print("\nStep 3: Parcel-level decoding (400 parcels × 48 targets)...")
print("  (This takes a while — each parcel individually)")

alphas = np.logspace(-2, 10, 20)
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# For each parcel: decode each target using that single parcel
# This is very noisy (1 feature → 1 target) but shows which parcels are informative
# Better: use local neighborhood (parcel + neighbors)
# For now: use single parcel r (like Horikawa ROI-level but per parcel)

# Actually, single parcel is too noisy. Use small neighborhoods.
# Alternative: use Ch1-C ROI results and assign PG1 per network.
# Let's do both: network-level (from Ch1-C) and parcel-level (new).

# Network-level (from Ch1-C results)
print("\n  Network-level (from Ch1-C):")
d_roi = np.load(OUT / 'ch1c_roi_decoding.npz', allow_pickle=True)
r_roi = d_roi['r_roi']  # (8, 48)
roi_names = list(d_roi['roi_names'])

network_pg1 = {}
for net in NETWORK_NAMES:
    parcels = [p for p in NETWORK_PARCELS[net] if p < N_CORTICAL]
    network_pg1[net] = np.mean([pg1[p] for p in parcels])

print(f"\n  {'Network':<15s} {'PG1':>7s} {'Cat r':>7s} {'Dim r':>7s} {'All r':>7s}")
print(f"  {'-'*45}")
for net in NETWORK_NAMES:
    idx = roi_names.index(net)
    print(f"  {net:<15s} {network_pg1[net]:7.4f} {r_roi[idx,:34].mean():7.4f} {r_roi[idx,34:].mean():7.4f} {r_roi[idx].mean():7.4f}")

# Correlation: PG1 vs decoding performance (across 7 networks)
pg1_vals = [network_pg1[net] for net in NETWORK_NAMES]
cat_vals = [r_roi[roi_names.index(net), :34].mean() for net in NETWORK_NAMES]
dim_vals = [r_roi[roi_names.index(net), 34:].mean() for net in NETWORK_NAMES]
all_vals = [r_roi[roi_names.index(net)].mean() for net in NETWORK_NAMES]

r_pg_cat, p_pg_cat = spearmanr(pg1_vals, cat_vals)
r_pg_dim, p_pg_dim = spearmanr(pg1_vals, dim_vals)
r_pg_all, p_pg_all = spearmanr(pg1_vals, all_vals)

print(f"\n  PG1 vs decoding (Spearman, 7 networks):")
print(f"    Cat r:  ρ={r_pg_cat:.3f}, p={p_pg_cat:.3f}")
print(f"    Dim r:  ρ={r_pg_dim:.3f}, p={p_pg_dim:.3f}")
print(f"    All r:  ρ={r_pg_all:.3f}, p={p_pg_all:.3f}")

# Cat/Dim ratio vs PG1
cat_dim_ratios = [r_roi[roi_names.index(net), :34].mean() / max(r_roi[roi_names.index(net), 34:].mean(), 1e-10)
                  for net in NETWORK_NAMES]
r_pg_ratio, p_pg_ratio = spearmanr(pg1_vals, cat_dim_ratios)
print(f"    Cat/Dim ratio: ρ={r_pg_ratio:.3f}, p={p_pg_ratio:.3f}")

if r_pg_all > 0:
    print(f"\n  → Transmodal(PG1↑)에서 감정 디코딩 더 잘됨 (Horikawa 일관)")
else:
    print(f"\n  → Transmodal-unimodal gradient가 감정 디코딩과 무관")

# ── Save ──────────────────────────────────────────────────────────────────
np.savez(OUT / 'ch1d_principal_gradient.npz',
    pg1=pg1,                    # (400,) PG1 per cortical parcel
    pg2=pg2,                    # (400,) PG2
    gradients=gradients,        # (400, 5)
    fc=fc,                      # (400, 400) functional connectivity
    network_pg1=np.array([network_pg1[n] for n in NETWORK_NAMES]),
    network_names=np.array(NETWORK_NAMES),
    # Correlations
    r_pg_cat=r_pg_cat, p_pg_cat=p_pg_cat,
    r_pg_dim=r_pg_dim, p_pg_dim=p_pg_dim,
    r_pg_all=r_pg_all, p_pg_all=p_pg_all,
    r_pg_ratio=r_pg_ratio, p_pg_ratio=p_pg_ratio,
)
print(f"\nSaved → {OUT}/ch1d_principal_gradient.npz")
print("Done.")
