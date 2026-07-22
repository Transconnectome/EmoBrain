"""
Exp 33 — Resolve asymmetry: was it ridge dim problem or true information asymmetry?

Two follow-ups to Exp 32 (which found 0 brain PCs predictable from V-JEPA2):

A. Symmetric PCA — both sides PCA'd to 100 PCs.
   Forward: V-JEPA2 PC (1d target) ← Brain PC (100d features)
   Reverse: Brain PC (1d target) ← V-JEPA2 PC (100d features)
   Both use 100d features → 1d target, so feature dim is matched.
   If reverse still fails, asymmetry is real.

B. Alpha sweep — vary ridge regularization in the reverse direction.
   alpha ∈ {1, 10, 100, 1000, 10000}
   If reverse fails at all alphas, the V-JEPA2 → brain prediction is fundamentally
   weak (information asymmetry). If it succeeds at high alpha, original failure
   was overfitting.

Three brain reps: pretrained / scratch / raw BOLD.
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

VJEPA_PATH = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/data/raw/video_embeddings/emovis_vjepa2_pretrained.npy")
META_PATH = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
BRAIN_DIRS = {
    'pretrained': Path("/pscratch/sd/s/sjmoon/EmoBrain/project/shared/output/embeddings/brain_jepa_resting_pad-mean"),
    'scratch':    Path("/pscratch/sd/s/sjmoon/EmoBrain/project/shared/output/embeddings/brain_jepa_scratch_pad-mean"),
}
RAW_FMRI_PATH = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/data/raw/raw_fmri/fmri_raw.npy")
OUTPUT_DIR = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/study1/data")

ALPHAS = [1.0, 10.0, 100.0, 1000.0, 10000.0]
cv = KFold(n_splits=5, shuffle=True, random_state=SEED)

def load_brain_jepa_mean(dir_path):
    embs = []
    for s in range(1, 6):
        d = torch.load(dir_path / f"sub-0{s}.pt", map_location='cpu', weights_only=False)
        e = d['embeddings'].numpy().astype(np.float64)
        if e.shape[0] > N_STIM: e = e[:N_STIM]
        embs.append(e)
    return np.stack(embs).mean(axis=0)

def ridge_pipe(alpha):
    return Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=alpha))])

def predict_each_dim(X, Y, alpha):
    """For each column of Y, fit Ridge(X → Y[:, k]) with CV, return per-dim R²."""
    n_dim = Y.shape[1]
    r2 = np.zeros(n_dim)
    pipe = ridge_pipe(alpha)
    for k in range(n_dim):
        r2[k] = cross_val_score(pipe, X, Y[:, k], cv=cv, scoring='r2').mean()
    return r2

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading...")
vjepa = np.load(VJEPA_PATH).astype(np.float64)[:N_STIM]
brains = {
    'pretrained': load_brain_jepa_mean(BRAIN_DIRS['pretrained']),
    'scratch':    load_brain_jepa_mean(BRAIN_DIRS['scratch']),
    'raw_bold':   np.load(RAW_FMRI_PATH).astype(np.float64)[:, :N_STIM, :].mean(axis=0),
}
print(f"  V-JEPA2: {vjepa.shape}")
for n, b in brains.items(): print(f"  {n}: {b.shape}")

# PCA both sides to 100 PCs
print(f"\nFitting PCA on V-JEPA2 ({N_PC} PCs)...")
pca_v = PCA(n_components=N_PC, random_state=SEED)
vj_pcs = pca_v.fit_transform(vjepa)
print(f"  V-JEPA2 PCs cumvar: {pca_v.explained_variance_ratio_.cumsum()[-1]:.4f}")

brain_pcs = {}
for n, b in brains.items():
    n_pc = min(N_PC, b.shape[1])
    p = PCA(n_components=n_pc, random_state=SEED)
    brain_pcs[n] = p.fit_transform(b)
    print(f"  {n} PCs cumvar (n_pc={n_pc}): {p.explained_variance_ratio_.cumsum()[-1]:.4f}")

# ── Part A: Symmetric PCA both sides (alpha=1.0) ──────────────────────────────
print("\n" + "="*72)
print("PART A — Symmetric: both sides 100 PCs, alpha=1.0")
print("="*72)

partA = {}
for name, bpc in brain_pcs.items():
    print(f"\n  Brain side: {name}")
    # Forward: V-JEPA2 PC ← Brain PC
    r2_fwd = predict_each_dim(bpc, vj_pcs, alpha=1.0)
    n_pos_fwd = (r2_fwd > 0).sum()
    top5_fwd = np.argsort(-r2_fwd)[:5]
    print(f"    Forward (V-JEPA2 PC ← Brain PC):")
    print(f"      Top 5: {[int(i)+1 for i in top5_fwd]}, R²: {[f'{r2_fwd[i]:+.3f}' for i in top5_fwd]}")
    print(f"      n PCs R²>0: {n_pos_fwd}")

    # Reverse: Brain PC ← V-JEPA2 PC
    r2_rev = predict_each_dim(vj_pcs, bpc, alpha=1.0)
    n_pos_rev = (r2_rev > 0).sum()
    top5_rev = np.argsort(-r2_rev)[:5]
    print(f"    Reverse (Brain PC ← V-JEPA2 PC):")
    print(f"      Top 5: {[int(i)+1 for i in top5_rev]}, R²: {[f'{r2_rev[i]:+.3f}' for i in top5_rev]}")
    print(f"      n PCs R²>0: {n_pos_rev}")

    partA[name] = dict(r2_fwd=r2_fwd, r2_rev=r2_rev,
                       n_pos_fwd=int(n_pos_fwd), n_pos_rev=int(n_pos_rev),
                       top5_fwd=top5_fwd, top5_rev=top5_rev)

# ── Part B: Alpha sweep, reverse direction with full V-JEPA2 (1408) → brain PC
print("\n" + "="*72)
print("PART B — Alpha sweep on reverse (1408 V-JEPA2 → brain PC)")
print("="*72)

partB = {}
for name, bpc in brain_pcs.items():
    print(f"\n  Brain side: {name}")
    for alpha in ALPHAS:
        r2 = predict_each_dim(vjepa, bpc, alpha=alpha)
        n_pos = (r2 > 0).sum()
        top3 = np.argsort(-r2)[:3]
        print(f"    alpha={alpha:>7.0f}: n PCs R²>0 = {n_pos:>3}; "
              f"top3 PCs={[int(i)+1 for i in top3]}, R²={[f'{r2[i]:+.3f}' for i in top3]}")
        partB[(name, alpha)] = dict(r2=r2, n_pos=int(n_pos), top3=top3)

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "="*72)
print("SUMMARY")
print("="*72)
print("\nPART A (symmetric PCA both sides):")
print(f"{'Brain':<14} {'fwd n>0':>8} {'fwd top1 R²':>14} {'rev n>0':>8} {'rev top1 R²':>14}")
print("-"*72)
for n, r in partA.items():
    print(f"{n:<14} {r['n_pos_fwd']:>8} {r['r2_fwd'][r['top5_fwd'][0]]:>+14.3f} "
          f"{r['n_pos_rev']:>8} {r['r2_rev'][r['top5_rev'][0]]:>+14.3f}")

print("\nPART B (reverse with alpha sweep):")
print(f"{'Brain':<14} {'alpha':>8} {'n PCs R²>0':>12} {'top1 R²':>10}")
print("-"*72)
for (n, a), r in partB.items():
    top1_r2 = r['r2'][r['top3'][0]]
    print(f"{n:<14} {a:>8.0f} {r['n_pos']:>12} {top1_r2:>+10.3f}")

# Save
np.savez(OUTPUT_DIR / 'exp33_symmetric_alpha_sweep.npz',
         **{f'A_{k}_r2_fwd': v['r2_fwd'] for k,v in partA.items()},
         **{f'A_{k}_r2_rev': v['r2_rev'] for k,v in partA.items()},
         **{f'B_{k}_a{int(a)}_r2': r['r2'] for (k,a),r in partB.items()},
         )
print("\nSaved → study1/data/exp33_symmetric_alpha_sweep.npz")
print("Done.")
