"""
Exp 32 — Reverse direction (brain-side PCA) robustness.

So far we did: V-JEPA2 → 100 PCs, find which PCs brain predicts.
Now reverse: brain → 100 PCs, find which brain PCs V-JEPA2 predicts.
Then decode emotion from video-predictable BRAIN subspace.

This tests the analysis from the BRAIN's perspective.
Repeat for all 3 brain representations (pretrained / scratch / raw BOLD).

If categorical bias appears in the video-predictable brain subspace as well,
the phenomenological finding is doubly robust.
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

def load_brain_jepa_mean(dir_path):
    embs = []
    for s in range(1, 6):
        d = torch.load(dir_path / f"sub-0{s}.pt", map_location='cpu', weights_only=False)
        e = d['embeddings'].numpy().astype(np.float64)
        if e.shape[0] > N_STIM: e = e[:N_STIM]
        embs.append(e)
    return np.stack(embs).mean(axis=0)

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading V-JEPA2 and brain reps...")
vjepa = np.load(VJEPA_PATH).astype(np.float64)
if vjepa.shape[0] > N_STIM: vjepa = vjepa[:N_STIM]

brain_pretrained = load_brain_jepa_mean(BRAIN_DIRS['pretrained'])
brain_scratch    = load_brain_jepa_mean(BRAIN_DIRS['scratch'])
raw_bold = np.load(RAW_FMRI_PATH).astype(np.float64)[:, :N_STIM, :].mean(axis=0)
print(f"  V-JEPA2: {vjepa.shape}")
print(f"  Brain pretrained: {brain_pretrained.shape}")
print(f"  Brain scratch:    {brain_scratch.shape}")
print(f"  Raw BOLD:         {raw_bold.shape}")

# Targets
meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)
score_cols = [f"score_{i}" for i in range(34)]
emotion_scores = meta[score_cols].values.astype(np.float64)[:N_STIM]
arousal = meta['arousal_score'].values.astype(np.float64)[:N_STIM]
valence = meta['valence_score'].values.astype(np.float64)[:N_STIM]
print(f"  Emotion targets: cats={emotion_scores.shape}, arousal+valence ready")

ridge = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])
cv = KFold(n_splits=5, shuffle=True, random_state=SEED)

# ── Reverse analysis per brain ────────────────────────────────────────────────
def reverse_analysis(brain, name):
    print(f"\n{'='*72}")
    print(f"  REVERSE direction: brain → PCs ← V-JEPA2 predicts | {name}")
    print(f"{'='*72}")

    # PCA on brain
    n_pc = min(N_PC, brain.shape[1])
    pca_b = PCA(n_components=n_pc, random_state=SEED)
    brain_pcs = pca_b.fit_transform(brain)
    print(f"  Brain PCs: {brain_pcs.shape}, cum var: {pca_b.explained_variance_ratio_.cumsum()[-1]:.4f}")

    # For each brain PC, can V-JEPA2 predict it?
    r2_per_pc = np.zeros(n_pc)
    for k in range(n_pc):
        scores = cross_val_score(ridge, vjepa, brain_pcs[:, k], cv=cv, scoring='r2')
        r2_per_pc[k] = scores.mean()

    top5_pos = np.argsort(-r2_per_pc)[:5]
    print(f"  Top 5 brain PCs predictable from V-JEPA2:")
    for i in top5_pos:
        print(f"    Brain-PC{i+1}: R²={r2_per_pc[i]:+.4f}")
    pos_pcs = np.where(r2_per_pc > 0)[0]
    print(f"  Brain PCs with R² > 0: {len(pos_pcs)} / {n_pc}")

    # Decode emotion from video-predictable brain subspace
    def decode(pcs_subset):
        if pcs_subset.shape[1] == 0:
            return None, None, None
        cat_r2 = np.zeros(34)
        for t in range(34):
            cat_r2[t] = max(cross_val_score(ridge, pcs_subset, emotion_scores[:, t],
                                             cv=cv, scoring='r2').mean(), 0.0)
        av_r2 = np.zeros(2)
        for t, tgt in enumerate([arousal, valence]):
            av_r2[t] = max(cross_val_score(ridge, pcs_subset, tgt, cv=cv, scoring='r2').mean(), 0.0)
        return cat_r2.mean(), av_r2.mean(), cat_r2.mean() / max(av_r2.mean(), 1e-10)

    sorted_pos = pos_pcs[np.argsort(-r2_per_pc[pos_pcs])]

    # Top-3 video-predictable brain PCs
    if len(sorted_pos) >= 3:
        sub3 = brain_pcs[:, sorted_pos[:3]]
        c3, a3, r3 = decode(sub3)
        print(f"  Top-3 video-predictable brain subspace ({sorted_pos[:3]+1}):")
        print(f"    cat R²={c3:.4f}, AV R²={a3:.4f}, ratio={r3:.3f}")
    else:
        c3, a3, r3 = None, None, None

    # All video-predictable brain PCs
    sub_all = brain_pcs[:, sorted_pos]
    if sub_all.shape[1] > 0:
        cA, aA, rA = decode(sub_all)
        print(f"  All video-predictable brain subspace ({sub_all.shape[1]} PCs):")
        print(f"    cat R²={cA:.4f}, AV R²={aA:.4f}, ratio={rA:.3f}")
    else:
        cA, aA, rA = None, None, None

    # Full brain PC space baseline
    cF, aF, rF = decode(brain_pcs)
    print(f"  Full brain {n_pc}-PC space:")
    print(f"    cat R²={cF:.4f}, AV R²={aF:.4f}, ratio={rF:.3f}")

    return dict(name=name, r2_per_pc=r2_per_pc, n_pos=len(pos_pcs),
                top3_ratio=r3, top3_cat=c3, top3_av=a3,
                all_ratio=rA, all_cat=cA, all_av=aA, all_n=sub_all.shape[1],
                full_ratio=rF, full_cat=cF, full_av=aF)

results = {
    'pretrained': reverse_analysis(brain_pretrained, "Brain-JEPA pretrained"),
    'scratch':    reverse_analysis(brain_scratch,    "Brain-JEPA scratch"),
    'raw_bold':   reverse_analysis(raw_bold,          "Raw BOLD"),
}

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n\n" + "="*78)
print("  REVERSE-DIRECTION SUMMARY (decode emotion from video-predictable brain subspace)")
print("="*78)
print(f"{'Brain side':<28} {'n_pred':>7} {'top3 ratio':>14} {'all ratio':>13} {'full ratio':>14}")
print("-"*78)
for k, r in results.items():
    t3 = f"{r['top3_ratio']:.3f}" if r['top3_ratio'] else "n/a"
    allr = f"{r['all_ratio']:.3f}" if r['all_ratio'] else "n/a"
    fullr = f"{r['full_ratio']:.3f}" if r['full_ratio'] else "n/a"
    print(f"{r['name']:<28} {r['n_pos']:>7} {t3:>14} {allr:>13} {fullr:>14}")

np.savez(OUTPUT_DIR / 'exp32_reverse_robustness.npz',
         pre_top3=results['pretrained']['top3_ratio'],
         scr_top3=results['scratch']['top3_ratio'],
         raw_top3=results['raw_bold']['top3_ratio'],
         pre_all=results['pretrained']['all_ratio'],
         scr_all=results['scratch']['all_ratio'],
         raw_all=results['raw_bold']['all_ratio'],
         pre_full=results['pretrained']['full_ratio'],
         scr_full=results['scratch']['full_ratio'],
         raw_full=results['raw_bold']['full_ratio'])
print("\nSaved → study1/data/exp32_reverse_robustness.npz")
print("Done.")
