"""
Exp 34 — Emotion decoding from video-predictable brain subspace.

We've established (Exp 33 Part A) that reverse direction works when both sides
are PCA'd to 100 PCs: some brain PCs ARE V-JEPA2-predictable.

The decisive question: do those video-predictable brain PCs show the same
categorical-versus-dimensional bias as the brain-predictable V-JEPA2 PCs?

For each brain rep:
  1. PCA brain → 100 PCs
  2. PCA V-JEPA2 → 100 PCs
  3. Reverse ridge: each brain PC ← V-JEPA2 PCs (alpha=1)
  4. Video-predictable brain PCs = those with R² > 0
  5. From those PCs, decode 34 cat + arousal + valence
  6. Compute cat R² mean, V-A R² mean, ratio

Compare with forward direction (V-JEPA2 PC ← Brain PC) and full brain PC space.

Stimulus: 2185 canonical.
"""

import numpy as np
import torch
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, KFold
from sklearn.decomposition import PCA
import pandas as pd
from pathlib import Path

N_STIM = 2185
N_PC = 100
SEED = 42

VJEPA_PATH = Path("/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/data/raw/video_embeddings/emovis_vjepa2_pretrained.npy")
META_PATH = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
BRAIN_DIRS = {
    'pretrained': Path("/pscratch/sd/s/sjmoon/FEELIN/project/shared/output/embeddings/brain_jepa_resting_pad-mean"),
    'scratch':    Path("/pscratch/sd/s/sjmoon/FEELIN/project/shared/output/embeddings/brain_jepa_scratch_pad-mean"),
}
RAW_FMRI_PATH = Path("/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/data/raw/raw_fmri/fmri_raw.npy")
OUTPUT_DIR = Path("/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/study1/data")

cv = KFold(n_splits=5, shuffle=True, random_state=SEED)
ridge = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

def load_brain_jepa_mean(dir_path):
    embs = []
    for s in range(1, 6):
        d = torch.load(dir_path / f"sub-0{s}.pt", map_location='cpu', weights_only=False)
        e = d['embeddings'].numpy().astype(np.float64)
        if e.shape[0] > N_STIM: e = e[:N_STIM]
        embs.append(e)
    return np.stack(embs).mean(axis=0)

def decode_emotion(X, emotion_scores, arousal, valence):
    cat_r2 = np.zeros(34)
    for t in range(34):
        cat_r2[t] = max(cross_val_score(ridge, X, emotion_scores[:, t], cv=cv, scoring='r2').mean(), 0.0)
    av_r2 = np.zeros(2)
    for t, tgt in enumerate([arousal, valence]):
        av_r2[t] = max(cross_val_score(ridge, X, tgt, cv=cv, scoring='r2').mean(), 0.0)
    return cat_r2.mean(), av_r2.mean(), cat_r2.mean() / max(av_r2.mean(), 1e-10)

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading...")
vjepa = np.load(VJEPA_PATH).astype(np.float64)[:N_STIM]
brains = {
    'pretrained': load_brain_jepa_mean(BRAIN_DIRS['pretrained']),
    'scratch':    load_brain_jepa_mean(BRAIN_DIRS['scratch']),
    'raw_bold':   np.load(RAW_FMRI_PATH).astype(np.float64)[:, :N_STIM, :].mean(axis=0),
}

meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)
score_cols = [f"score_{i}" for i in range(34)]
emotion_scores = meta[score_cols].values.astype(np.float64)[:N_STIM]
arousal = meta['arousal_score'].values.astype(np.float64)[:N_STIM]
valence = meta['valence_score'].values.astype(np.float64)[:N_STIM]

# PCA V-JEPA2
pca_v = PCA(n_components=N_PC, random_state=SEED)
vj_pcs = pca_v.fit_transform(vjepa)

print(f"\n{'='*80}")
print("  Emotion decoding from VIDEO-PREDICTABLE BRAIN SUBSPACE")
print(f"{'='*80}")

results = {}
for name, brain in brains.items():
    print(f"\n--- Brain: {name} ({brain.shape}) ---")

    # PCA brain
    n_pc = min(N_PC, brain.shape[1])
    pca_b = PCA(n_components=n_pc, random_state=SEED)
    brain_pcs = pca_b.fit_transform(brain)

    # Reverse ridge: each brain PC ← V-JEPA2 PCs
    r2_per_brainpc = np.zeros(n_pc)
    for k in range(n_pc):
        r2_per_brainpc[k] = cross_val_score(ridge, vj_pcs, brain_pcs[:, k], cv=cv, scoring='r2').mean()

    pos_mask = r2_per_brainpc > 0
    n_pos = int(pos_mask.sum())
    pos_sorted = np.where(pos_mask)[0][np.argsort(-r2_per_brainpc[pos_mask])]
    print(f"  Video-predictable brain PCs (R²>0): {n_pos}/{n_pc}")
    print(f"  Top 5: {[int(i)+1 for i in pos_sorted[:5]]}, "
          f"R²: {[f'{r2_per_brainpc[i]:.3f}' for i in pos_sorted[:5]]}")

    # Top-3 video-predictable brain PCs
    if n_pos >= 3:
        c3, a3, r3 = decode_emotion(brain_pcs[:, pos_sorted[:3]], emotion_scores, arousal, valence)
        print(f"  Top-3 video-predictable brain subspace:")
        print(f"    cat R²={c3:.4f}, AV R²={a3:.4f}, ratio={r3:.3f}")
    else:
        c3, a3, r3 = None, None, None

    # All video-predictable brain PCs
    if n_pos > 0:
        cA, aA, rA = decode_emotion(brain_pcs[:, pos_sorted], emotion_scores, arousal, valence)
        print(f"  All {n_pos} video-predictable brain PCs:")
        print(f"    cat R²={cA:.4f}, AV R²={aA:.4f}, ratio={rA:.3f}")
    else:
        cA, aA, rA = None, None, None

    # Full brain PC space baseline
    cF, aF, rF = decode_emotion(brain_pcs, emotion_scores, arousal, valence)
    print(f"  Full brain {n_pc}-PC space:")
    print(f"    cat R²={cF:.4f}, AV R²={aF:.4f}, ratio={rF:.3f}")

    # Video-NON-predictable (R²<=0) brain PCs as control
    nonpos = np.where(~pos_mask)[0]
    if len(nonpos) > 0:
        cN, aN, rN = decode_emotion(brain_pcs[:, nonpos], emotion_scores, arousal, valence)
        print(f"  Non-video-predictable {len(nonpos)} brain PCs (control):")
        print(f"    cat R²={cN:.4f}, AV R²={aN:.4f}, ratio={rN:.3f}")
    else:
        cN, aN, rN = None, None, None

    results[name] = dict(
        n_pos=n_pos, top_pos_ids=pos_sorted[:5].tolist(),
        top3_cat=c3, top3_av=a3, top3_ratio=r3,
        all_cat=cA, all_av=aA, all_ratio=rA, all_n=n_pos,
        full_cat=cF, full_av=aF, full_ratio=rF,
        non_cat=cN, non_av=aN, non_ratio=rN,
    )

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'='*80}")
print(f"  SUMMARY — REVERSE DIRECTION CATEGORICAL BIAS")
print(f"{'='*80}")
print(f"\n{'Brain':<12} {'n_pred':>7} {'top3 ratio':>11} {'all ratio':>11} {'full ratio':>11} {'non-pred ratio':>16}")
print("-"*80)
for n, r in results.items():
    t3  = f"{r['top3_ratio']:.3f}" if r['top3_ratio'] is not None else "n/a"
    al  = f"{r['all_ratio']:.3f}"  if r['all_ratio']  is not None else "n/a"
    fl  = f"{r['full_ratio']:.3f}" if r['full_ratio'] is not None else "n/a"
    no  = f"{r['non_ratio']:.3f}"  if r['non_ratio']  is not None else "n/a"
    print(f"{n:<12} {r['n_pos']:>7} {t3:>11} {al:>11} {fl:>11} {no:>16}")

print("\n  Interpretation:")
print("  - If 'video-pred' ratio > 'full' ratio: brain's video-readable subspace is more")
print("    categorical than overall brain PC space (= reverse-direction categorical bias).")
print("  - If 'video-pred' ratio > 'non-pred' ratio: the video link itself amplifies cat bias.")
print("  - This is the symmetric counterpart of the abstract's forward-direction finding.")

# Save
save_dict = {}
for n, r in results.items():
    for k, v in r.items():
        save_dict[f'{n}_{k}'] = v if v is not None else np.nan
np.savez(OUTPUT_DIR / 'exp34_reverse_categorical_bias.npz', **save_dict)
print(f"\nSaved → study1/data/exp34_reverse_categorical_bias.npz")
print("Done.")
