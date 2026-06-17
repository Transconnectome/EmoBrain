"""
Exp 31 — Brain-side robustness check.

The accepted paper uses Brain-JEPA (pretrained on UK Biobank rest-fMRI) as the
brain-side representation. This raises a fundamental interpretability concern:
the pretraining domain (rest) differs from the application domain (emotional
video task). Does the alignment we measure reflect emotion-related brain
processing, or pretrained-feature artifacts?

This script tests robustness across three brain-side representations:
  1. Brain-JEPA pretrained (resting)   — abstract's main analysis
  2. Brain-JEPA scratch (random init)  — null brain encoder
  3. Raw BOLD parcels                  — direct fMRI, no foundation model

For each brain representation, we run the same pipeline:
  - V-JEPA2 → 100 PCs
  - Brain → V-JEPA2 PC ridge regression with 5-fold CV
  - Identify brain-predictable PCs (raw R² > 0)
  - Compute category R² / V-A R² ratio in the brain-predictable subspace and
    in the full 100-PC space

Stimulus: 2185 canonical.

The expected scenarios:
  - Pretrained ≈ scratch    → Brain-JEPA pretraining contributes nothing
                              specific (purely architectural)
  - Pretrained > scratch    → pretraining captures something specific
                              applicable to task fMRI
  - Pretrained ≈ raw BOLD   → Brain-JEPA preserves what raw BOLD has
  - Pretrained ≠ raw BOLD   → Brain-JEPA reshapes the signal in non-trivial way
"""

import numpy as np
import torch
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import r2_score
from sklearn.decomposition import PCA
import pandas as pd
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────
N_STIM = 2185
N_PC = 100
SEED = 42

VJEPA_PATH = Path("/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/data/raw/video_embeddings/emovis_vjepa2_pretrained.npy")
META_PATH = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
BRAIN_JEPA_PRETRAINED_DIR = Path("/pscratch/sd/s/sjmoon/FEELIN/project/shared/output/embeddings/brain_jepa_resting_pad-mean")
BRAIN_JEPA_SCRATCH_DIR = Path("/pscratch/sd/s/sjmoon/FEELIN/project/shared/output/embeddings/brain_jepa_scratch_pad-mean")
RAW_FMRI_PATH = Path("/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/data/raw/raw_fmri/fmri_raw.npy")
OUTPUT_DIR = Path("/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/study1/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load V-JEPA2 ──────────────────────────────────────────────────────────────
print("Loading V-JEPA2 (2185, 1408)...")
vjepa = np.load(VJEPA_PATH).astype(np.float64)
if vjepa.shape[0] > N_STIM:
    vjepa = vjepa[:N_STIM]
print(f"  V-JEPA2 shape: {vjepa.shape}")

# PCA
print(f"Fitting PCA on V-JEPA2 ({N_PC} PCs)...")
pca = PCA(n_components=N_PC, random_state=SEED)
vjepa_pcs = pca.fit_transform(vjepa)
print(f"  Cumulative variance: {pca.explained_variance_ratio_.cumsum()[-1]:.4f}")

# ── Load brain-side representations ───────────────────────────────────────────
def load_brain_jepa_variant(dir_path, n_stim=N_STIM):
    """Load 5 subjects' Brain-JEPA dict-style .pt files and average."""
    embs = []
    for s in range(1, 6):
        p = dir_path / f"sub-0{s}.pt"
        d = torch.load(p, map_location='cpu', weights_only=False)
        e = d['embeddings'].numpy().astype(np.float64)
        if e.shape[0] > n_stim:
            e = e[:n_stim]
        embs.append(e)
    return np.stack(embs).mean(axis=0)  # (n_stim, 768)

print("\nLoading brain-side representations...")
brain_pretrained = load_brain_jepa_variant(BRAIN_JEPA_PRETRAINED_DIR)
print(f"  Brain-JEPA pretrained: {brain_pretrained.shape}")
brain_scratch = load_brain_jepa_variant(BRAIN_JEPA_SCRATCH_DIR)
print(f"  Brain-JEPA scratch:    {brain_scratch.shape}")

# Raw BOLD: (5, 2196, 450) → slice + mean
raw_fmri = np.load(RAW_FMRI_PATH).astype(np.float64)
print(f"  Raw fMRI loaded: {raw_fmri.shape}")
raw_fmri = raw_fmri[:, :N_STIM, :].mean(axis=0)  # (2185, 450)
print(f"  Raw BOLD (mean subj): {raw_fmri.shape}")

# Cross-subject reliability (for context)
def cross_subj_corr(dir_path):
    embs = []
    for s in range(1, 6):
        d = torch.load(dir_path / f"sub-0{s}.pt", map_location='cpu', weights_only=False)
        e = d['embeddings'].numpy().astype(np.float64)
        if e.shape[0] > N_STIM:
            e = e[:N_STIM]
        embs.append(e.flatten())
    cm = np.corrcoef(embs)
    upper = cm[np.triu_indices_from(cm, k=1)]
    return upper.mean()

def cross_subj_corr_raw():
    embs = [raw_fmri.flatten()]  # only mean here
    # Compute from per-subject
    full = np.load(RAW_FMRI_PATH).astype(np.float64)[:, :N_STIM, :]
    embs = [full[s].flatten() for s in range(5)]
    cm = np.corrcoef(embs)
    upper = cm[np.triu_indices_from(cm, k=1)]
    return upper.mean()

print("\nCross-subject Pearson correlation of brain reps (mean across pairs):")
print(f"  Brain-JEPA pretrained: {cross_subj_corr(BRAIN_JEPA_PRETRAINED_DIR):.4f}")
print(f"  Brain-JEPA scratch:    {cross_subj_corr(BRAIN_JEPA_SCRATCH_DIR):.4f}")
print(f"  Raw BOLD:              {cross_subj_corr_raw():.4f}")

# ── Emotion targets ───────────────────────────────────────────────────────────
print("\nLoading emotion targets...")
meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)
score_cols = [f"score_{i}" for i in range(34)]
emotion_scores = meta[score_cols].values.astype(np.float64)[:N_STIM]
arousal = meta['arousal_score'].values.astype(np.float64)[:N_STIM]
valence = meta['valence_score'].values.astype(np.float64)[:N_STIM]
all_targets = np.column_stack([emotion_scores, arousal, valence])
print(f"  Targets: {all_targets.shape}")

# ── Per-brain analysis ────────────────────────────────────────────────────────
def analyze(brain, brain_name):
    print(f"\n{'='*70}\n  ANALYSIS for brain side = {brain_name}\n{'='*70}")
    print(f"  Brain shape: {brain.shape}")

    ridge = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])
    cv = KFold(n_splits=5, shuffle=True, random_state=SEED)

    # Step 1: brain-predictable PCs (V-JEPA2 PC ← brain)
    r2_per_pc = np.zeros(N_PC)
    for k in range(N_PC):
        scores = cross_val_score(ridge, brain, vjepa_pcs[:, k], cv=cv, scoring='r2')
        r2_per_pc[k] = scores.mean()

    # No permutation here (time): use raw R² > 0 threshold
    pred_mask = r2_per_pc > 0
    n_pred = pred_mask.sum()
    top5 = np.argsort(-r2_per_pc)[:5]
    print(f"  Top 5 PCs by R²: {[int(i)+1 for i in top5]}")
    print(f"    R²: {[f'{r2_per_pc[i]:+.4f}' for i in top5]}")
    print(f"  PCs with R² > 0: {n_pred} / {N_PC}")
    # Top 5 by sign (positive)
    pos_pcs = np.where(r2_per_pc > 0)[0]
    pos_sorted = pos_pcs[np.argsort(-r2_per_pc[pos_pcs])]
    print(f"  Top 5 positive PCs: {[int(i)+1 for i in pos_sorted[:5]]}")
    print(f"    R²: {[f'{r2_per_pc[i]:.4f}' for i in pos_sorted[:5]]}")

    # Step 2: decode emotion from brain-predictable subspace (using top-K)
    # We'll try K=3 (to match abstract) and K=all positive-R² PCs
    def decode_from_subset(pcs_subset):
        if pcs_subset.shape[1] == 0:
            return None, None, None
        cat_r2 = np.zeros(34)
        for t in range(34):
            scores = cross_val_score(ridge, pcs_subset, emotion_scores[:, t], cv=cv, scoring='r2')
            cat_r2[t] = max(scores.mean(), 0.0)
        av_r2 = np.zeros(2)
        for t, tgt in enumerate([arousal, valence]):
            scores = cross_val_score(ridge, pcs_subset, tgt, cv=cv, scoring='r2')
            av_r2[t] = max(scores.mean(), 0.0)
        return cat_r2.mean(), av_r2.mean(), cat_r2.mean() / max(av_r2.mean(), 1e-10)

    # Top-3 brain-predictable
    if len(pos_sorted) >= 3:
        sub3 = vjepa_pcs[:, pos_sorted[:3]]
        c3, a3, r3 = decode_from_subset(sub3)
        print(f"  Top-3 brain-predictable subspace ({pos_sorted[:3]+1}):")
        print(f"    cat R²={c3:.4f}, AV R²={a3:.4f}, ratio={r3:.3f}")
    else:
        c3, a3, r3 = None, None, None

    # All brain-predictable (positive R²)
    sub_all = vjepa_pcs[:, pos_sorted]
    if sub_all.shape[1] > 0:
        cA, aA, rA = decode_from_subset(sub_all)
        print(f"  All brain-predictable subspace ({sub_all.shape[1]} PCs):")
        print(f"    cat R²={cA:.4f}, AV R²={aA:.4f}, ratio={rA:.3f}")
    else:
        cA, aA, rA = None, None, None

    # Full 100 PCs baseline
    cF, aF, rF = decode_from_subset(vjepa_pcs)
    print(f"  Full 100-PC space:")
    print(f"    cat R²={cF:.4f}, AV R²={aF:.4f}, ratio={rF:.3f}")

    return {
        'brain_name': brain_name,
        'r2_per_pc': r2_per_pc,
        'n_predictable': int(n_pred),
        'top_pc_ids': pos_sorted[:5].astype(int) + 1,
        'top3_pcs': pos_sorted[:3].astype(int) + 1 if len(pos_sorted) >= 3 else None,
        'top3_cat_r2': c3, 'top3_av_r2': a3, 'top3_ratio': r3,
        'all_n': int(sub_all.shape[1]),
        'all_cat_r2': cA, 'all_av_r2': aA, 'all_ratio': rA,
        'full_cat_r2': cF, 'full_av_r2': aF, 'full_ratio': rF,
    }

results = {}
results['pretrained'] = analyze(brain_pretrained, "Brain-JEPA pretrained (resting)")
results['scratch']    = analyze(brain_scratch,    "Brain-JEPA scratch (random init)")
results['raw_bold']   = analyze(raw_fmri,          "Raw BOLD (450 parcels, subj mean)")

# ── Summary table ────────────────────────────────────────────────────────────
print("\n\n" + "="*78)
print("ROBUSTNESS SUMMARY")
print("="*78)
print(f"{'Brain side':<35} {'n>0':>5} {'cat ratio (top3)':>20} {'cat ratio (full)':>18}")
print("-"*78)
for k, r in results.items():
    top3_str = f"{r['top3_ratio']:.3f}" if r['top3_ratio'] is not None else "n/a"
    print(f"{r['brain_name']:<35} {r['n_predictable']:>5} {top3_str:>20} {r['full_ratio']:.3f if r['full_ratio'] else 'n/a':>18}")

# Save
np.savez(OUTPUT_DIR / 'exp31_brain_side_robustness.npz',
         pretrained_r2_per_pc=results['pretrained']['r2_per_pc'],
         scratch_r2_per_pc=results['scratch']['r2_per_pc'],
         raw_bold_r2_per_pc=results['raw_bold']['r2_per_pc'],
         pretrained_top3_ratio=results['pretrained']['top3_ratio'],
         scratch_top3_ratio=results['scratch']['top3_ratio'],
         raw_bold_top3_ratio=results['raw_bold']['top3_ratio'],
         pretrained_full_ratio=results['pretrained']['full_ratio'],
         scratch_full_ratio=results['scratch']['full_ratio'],
         raw_bold_full_ratio=results['raw_bold']['full_ratio'],
)
print("\nSaved → study1/data/exp31_brain_side_robustness.npz")
print("Done.")
