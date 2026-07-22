"""
Exp 21b: CCA 100 components — NO permutation test (fast version).
PCA 100 → CCA 100, emotion correlation, decoding comparison.
Permutation test skipped to save time.
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

BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
VJEPA_PATH = BASE / "video_embeddings/vjepa2_embeddings.npy"
BRAIN_PATH = BASE / "brain_embeddings/brain_jepa_embeddings.npy"
META_PATH  = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
OUTPUT_DIR = BASE / "CCN2026/results"

EMOTION_LABELS = [
    'Admiration', 'Adoration', 'Aesthetic appreciation', 'Amusement', 'Anger',
    'Anxiety', 'Awe', 'Awkwardness', 'Boredom', 'Calmness', 'Confusion',
    'Contempt', 'Craving', 'Disgust', 'Empathic pain', 'Entrancement',
    'Excitement', 'Fear', 'Horror', 'Interest', 'Joy', 'Nostalgia', 'Relief',
    'Romance', 'Sadness', 'Satisfaction', 'Sexual desire', 'Surprise',
    'Sympathy', 'Triumph', 'Uncomfortable', 'Annoyance', 'Envy', 'Guilt'
]

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
vjepa = np.load(VJEPA_PATH).astype(np.float64)
brain_raw = np.load(BRAIN_PATH).astype(np.float64)
brain_mean = brain_raw.mean(axis=0)

meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)
score_cols = [f"score_{i}" for i in range(34)]
emotion_scores = meta[score_cols].values.astype(np.float64)
arousal = meta['arousal_score'].values.astype(np.float64)
valence = meta['valence_score'].values.astype(np.float64)

# ── PCA 100 ──────────────────────────────────────────────────────────────────
N_PCA = 100
N_CC = 100
print(f"PCA({N_PCA}) + CCA({N_CC})...")

scaler_v = StandardScaler()
scaler_b = StandardScaler()
pca_v = PCA(n_components=N_PCA, random_state=42)
pca_b = PCA(n_components=N_PCA, random_state=42)

vjepa_pca = pca_v.fit_transform(scaler_v.fit_transform(vjepa))
brain_pca = pca_b.fit_transform(scaler_b.fit_transform(brain_mean))

print(f"  V-JEPA2 var: {pca_v.explained_variance_ratio_.sum():.3f}")
print(f"  Brain var: {pca_b.explained_variance_ratio_.sum():.3f}")

# ── CCA ──────────────────────────────────────────────────────────────────────
cca = CCA(n_components=N_CC, max_iter=1000)
brain_cc, video_cc = cca.fit_transform(brain_pca, vjepa_pca)

cc_r = np.array([np.corrcoef(brain_cc[:, i], video_cc[:, i])[0, 1] for i in range(N_CC)])
print(f"\nCanonical correlations:")
for i in range(min(20, N_CC)):
    print(f"  CC{i+1}: r = {cc_r[i]:.4f}")
print(f"  ... CC{N_CC}: r = {cc_r[-1]:.4f}")
print(f"  CCs with r > 0.3: {(cc_r > 0.3).sum()}")

# ── Emotion correlations ─────────────────────────────────────────────────────
print("\nEmotion correlations...")
corr_cc_emo = np.zeros((N_CC, 34))
for i in range(N_CC):
    for j in range(34):
        r, _ = spearmanr(video_cc[:, i], emotion_scores[:, j])
        corr_cc_emo[i, j] = r

corr_cc_emo_brain = np.zeros((N_CC, 34))
for i in range(N_CC):
    for j in range(34):
        r, _ = spearmanr(brain_cc[:, i], emotion_scores[:, j])
        corr_cc_emo_brain[i, j] = r

corr_cc_av = np.zeros((N_CC, 2))
for i in range(N_CC):
    corr_cc_av[i, 0], _ = spearmanr(video_cc[:, i], arousal)
    corr_cc_av[i, 1], _ = spearmanr(video_cc[:, i], valence)

max_r_per_cc = np.max(np.abs(corr_cc_emo), axis=1)

print("Top 10 CCs emotion profiles:")
for i in range(10):
    top3_idx = np.argsort(np.abs(corr_cc_emo[i]))[-3:][::-1]
    top3 = [(EMOTION_LABELS[j], f"{corr_cc_emo[i,j]:+.3f}") for j in top3_idx]
    print(f"  CC{i+1} (r={cc_r[i]:.3f}): max|r|={max_r_per_cc[i]:.3f}, "
          f"A={corr_cc_av[i,0]:+.3f}, V={corr_cc_av[i,1]:+.3f}, top={top3}")

# ── Decoding ──────────────────────────────────────────────────────────────────
print("\nEmotion decoding...")
targets = np.hstack([emotion_scores, arousal[:, None], valence[:, None]])
model = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

vjepa_pca_full = PCA(n_components=100, random_state=42).fit_transform(
    StandardScaler().fit_transform(vjepa))

# meaningful CCs: r > 0.3
meaningful_mask = cc_r > 0.3
n_meaningful = meaningful_mask.sum()
print(f"  Meaningful CCs (r>0.3): {n_meaningful}")

feature_sets = {
    f'CCA-meaningful({n_meaningful})': video_cc[:, meaningful_mask],
    f'CCA-all{N_CC}': video_cc,
    'PCA-PC1to3': vjepa_pca_full[:, :3],
    'PCA-PC1to10': vjepa_pca_full[:, :10],
    'PCA-all100': vjepa_pca_full,
}

r2_results = {}
for feat_name, X in feature_sets.items():
    r2_vals = np.zeros(36)
    for t in range(36):
        scores = cross_val_score(model, X, targets[:, t], cv=5, scoring='r2')
        r2_vals[t] = max(scores.mean(), 0.0)
    r2_results[feat_name] = r2_vals
    cat_mean = r2_vals[:34].mean()
    av_mean = r2_vals[34:].mean()
    ratio = cat_mean / max(av_mean, 1e-10)
    print(f"  {feat_name} ({X.shape[1]}d): cat={cat_mean:.4f}, AV={av_mean:.4f}, ratio={ratio:.3f}")

# ── Subject-level CCA ─────────────────────────────────────────────────────────
print("\nSubject-level CCA...")
cc_r_per_subj = np.zeros((5, N_CC))
for s in range(5):
    brain_s_subj = StandardScaler().fit_transform(brain_raw[s])
    brain_pca_subj = PCA(n_components=N_PCA, random_state=42).fit_transform(brain_s_subj)
    cca_subj = CCA(n_components=N_CC, max_iter=1000)
    b_subj, v_subj = cca_subj.fit_transform(brain_pca_subj, vjepa_pca)
    for i in range(N_CC):
        cc_r_per_subj[s, i] = np.corrcoef(b_subj[:, i], v_subj[:, i])[0, 1]
    print(f"  Subject {s+1}: CC1={cc_r_per_subj[s,0]:.4f}, CC2={cc_r_per_subj[s,1]:.4f}")

# ── Save ──────────────────────────────────────────────────────────────────────
print("\nSaving...")
meaningful_key = f'CCA-meaningful({n_meaningful})'
np.savez(
    OUTPUT_DIR / 'cca100_results.npz',
    cc_r=cc_r,
    brain_cc=brain_cc,
    video_cc=video_cc,
    corr_cc_emo=corr_cc_emo,
    corr_cc_emo_brain=corr_cc_emo_brain,
    corr_cc_av=corr_cc_av,
    max_r_per_cc=max_r_per_cc,
    r2_cca_meaningful=r2_results.get(meaningful_key, np.zeros(36)),
    r2_cca_all=r2_results.get(f'CCA-all{N_CC}', np.zeros(36)),
    r2_pca_3=r2_results.get('PCA-PC1to3', np.zeros(36)),
    r2_pca_10=r2_results.get('PCA-PC1to10', np.zeros(36)),
    r2_pca_100=r2_results.get('PCA-all100', np.zeros(36)),
    cc_r_per_subj=cc_r_per_subj,
    n_meaningful=n_meaningful,
    meaningful_mask=meaningful_mask,
    emotion_labels=np.array(EMOTION_LABELS),
    n_pca=N_PCA,
    n_cc=N_CC,
    pca_v_var=pca_v.explained_variance_ratio_.sum(),
    pca_b_var=pca_b.explained_variance_ratio_.sum(),
)
print(f"Saved → {OUTPUT_DIR}/cca100_results.npz")
print("Done.")
