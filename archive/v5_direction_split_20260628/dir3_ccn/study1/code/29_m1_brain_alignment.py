"""
Exp 29 (refactored) — M1 brain-aligned subspace identification (generic, any model).

For a given video model (V-JEPA2, CLIP, DINOv2, VideoMAE, untrained, supervised):
  1. PCA on model embedding → 100 PCs (variance-based)
  2. For each PC, ridge-regress on group-mean Brain-JEPA representation (5-fold CV)
  3. Permutation test (n=1000) on observed R² to compute p-value
  4. FDR (Benjamini-Hochberg) over 100 PCs
  5. Survive PCs = brain-aligned subspace (M1)

Multi-metric collection (per CLAUDE.md rule):
  - R² (raw, no max-clipping)
  - R² (max-clipped at 0, for abstract continuity)
  - Pearson r on CV predictions
  - Spearman r on CV predictions

Multi-variant: sequential CV vs shuffled CV (tests CV leakage robustness).

Stimulus: 2185 canonical (Horikawa repeat clips excluded).

Usage:
  python 29_m1_brain_alignment.py --model vjepa2_pretrained
  python 29_m1_brain_alignment.py --model clip_pretrained
  python 29_m1_brain_alignment.py --model dinov2_pretrained
  python 29_m1_brain_alignment.py --model videomae_pretrained
  python 29_m1_brain_alignment.py --model vjepa2_scratch        # untrained
  python 29_m1_brain_alignment.py --model clip_scratch
"""

import argparse
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import r2_score
from sklearn.decomposition import PCA
from scipy.stats import pearsonr, spearmanr
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────
N_STIM = 2185  # canonical, excludes Horikawa repeat clips
N_PC = 100
N_PERM = 1000
ALPHA = 0.05
SEED = 42

EMBED_DIR = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/data/raw/video_embeddings")
BRAIN_PATH = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/data/raw/brain_embeddings/brain_jepa_embeddings.npy")
OUTPUT_DIR = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/study1/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATHS = {
    'vjepa2_pretrained':  'emovis_vjepa2_pretrained.npy',
    'vjepa2_scratch':     'emovis_vjepa2_scratch.npy',
    'clip_pretrained':    'emovis_clip_pretrained.npy',
    'clip_scratch':       'emovis_clip_scratch.npy',
    'dinov2_pretrained':  'emovis_dinov2_pretrained.npy',
    'dinov2_scratch':     'emovis_dinov2_scratch.npy',
    'videomae_pretrained':'emovis_videomae_pretrained.npy',
    'videomae_scratch':   'emovis_videomae_scratch.npy',
}

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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True, choices=list(MODEL_PATHS.keys()))
    args = ap.parse_args()

    print(f"=== Exp 29 M1 brain alignment: model={args.model}, n_stim={N_STIM}, n_pc={N_PC} ===\n")

    # Load
    print("Loading data...")
    embed = np.load(EMBED_DIR / MODEL_PATHS[args.model]).astype(np.float64)
    brain_raw = np.load(BRAIN_PATH).astype(np.float64)
    print(f"  Model embed: {embed.shape}, Brain raw: {brain_raw.shape}")

    # Slice to 2185 canonical
    if embed.shape[0] > N_STIM:
        embed = embed[:N_STIM]
    if brain_raw.shape[1] > N_STIM:
        brain_raw = brain_raw[:, :N_STIM, :]
    brain = brain_raw.mean(axis=0)  # (2185, 768)
    print(f"  After slice: model={embed.shape}, brain={brain.shape}")

    # PCA
    print(f"\nFitting PCA ({N_PC} components)...")
    pca = PCA(n_components=N_PC, random_state=SEED)
    pcs = pca.fit_transform(embed)
    print(f"  Cumulative variance: {pca.explained_variance_ratio_.cumsum()[-1]:.4f}")

    # Setup
    model_pipeline = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])
    cv_seq = KFold(n_splits=5, shuffle=False)
    cv_shuf = KFold(n_splits=5, shuffle=True, random_state=SEED)
    rng = np.random.default_rng(SEED)

    # ── Observed R² (multi-variant, multi-metric) ────────────────────────────
    print("\nComputing observed R² across 4 variants × multi-metric...")
    variants = {}
    for cv_name, cv_obj in [('seq', cv_seq), ('shuf', cv_shuf)]:
        r2_raw = np.zeros(N_PC)
        pearson = np.zeros(N_PC)
        spearman = np.zeros(N_PC)
        for k in range(N_PC):
            y = pcs[:, k]
            y_pred = np.zeros_like(y)
            r2_folds = []
            for train_idx, test_idx in cv_obj.split(brain):
                model_pipeline.fit(brain[train_idx], y[train_idx])
                y_pred[test_idx] = model_pipeline.predict(brain[test_idx])
                r2_folds.append(r2_score(y[test_idx], y_pred[test_idx]))
            r2_raw[k] = float(np.mean(r2_folds))
            pearson[k] = pearsonr(y, y_pred)[0]
            spearman[k] = spearmanr(y, y_pred)[0]
        variants[cv_name] = {
            'r2_raw': r2_raw,
            'r2_clipped': np.maximum(r2_raw, 0.0),
            'pearson_r': pearson,
            'spearman_r': spearman,
        }
        print(f"  CV={cv_name}: top-5 PCs by r2_raw: PC{np.argsort(-r2_raw)[:5]+1}")
        for k in np.argsort(-r2_raw)[:5]:
            print(f"    PC{k+1}: r2_raw={r2_raw[k]:+.4f}, r2_clipped={max(r2_raw[k],0):.4f}, "
                  f"pearson={pearson[k]:+.4f}, spearman={spearman[k]:+.4f}")

    # ── Permutation test (raw and clipped null) on top-20 by raw R² (shuf CV) ──
    print(f"\nPermutation test (n={N_PERM}) on top 20 PCs...")
    top_pcs = np.argsort(-variants['shuf']['r2_raw'])[:20]
    print(f"  Test PCs (1-indexed): {sorted(top_pcs+1)}")

    for cv_name, cv_obj in [('seq', cv_seq), ('shuf', cv_shuf)]:
        v = variants[cv_name]
        null_raw  = np.zeros((N_PC, N_PERM))
        null_clip = np.zeros((N_PC, N_PERM))
        p_raw  = np.ones(N_PC)
        p_clip = np.ones(N_PC)
        for idx, k in enumerate(top_pcs):
            target = pcs[:, k]
            for p in range(N_PERM):
                target_perm = rng.permutation(target)
                scores = cross_val_score(model_pipeline, brain, target_perm, cv=cv_obj, scoring='r2')
                null_raw[k, p]  = scores.mean()
                null_clip[k, p] = max(scores.mean(), 0.0)
            p_raw[k]  = np.mean(null_raw[k]  >= v['r2_raw'][k])
            p_clip[k] = np.mean(null_clip[k] >= v['r2_clipped'][k])
            if (idx+1) % 5 == 0:
                print(f"  [{cv_name} {idx+1}/20] PC{k+1}: p_raw={p_raw[k]:.4f}, p_clip={p_clip[k]:.4f}")
        v['p_raw']  = p_raw
        v['p_clip'] = p_clip
        v['q_raw']  = fdr_bh(p_raw)
        v['q_clip'] = fdr_bh(p_clip)
        v['null_raw_dist']  = null_raw
        v['null_clip_dist'] = null_clip

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*70}\nSUMMARY — surviving PCs by FDR<{ALPHA}\n{'='*70}")
    for cv_name in ['seq', 'shuf']:
        v = variants[cv_name]
        sig_clip = np.where(v['q_clip'] < ALPHA)[0] + 1
        sig_raw  = np.where(v['q_raw']  < ALPHA)[0] + 1
        print(f"  CV={cv_name}:")
        print(f"    clipped null (original method): PCs {sorted(sig_clip)} ({len(sig_clip)} PCs)")
        print(f"    raw null     (no artifact):     PCs {sorted(sig_raw)}  ({len(sig_raw)} PCs)")
        print(f"    same? {sorted(sig_clip)==sorted(sig_raw)}")

    # ── Save ──────────────────────────────────────────────────────────────────
    save_dict = {
        'model_name': args.model,
        'n_stim': N_STIM,
        'n_pc': N_PC,
        'n_perm': N_PERM,
        'cumulative_variance': pca.explained_variance_ratio_.cumsum(),
        'pcs': pcs,
    }
    for cv_name in ['seq', 'shuf']:
        v = variants[cv_name]
        for key in ['r2_raw', 'r2_clipped', 'pearson_r', 'spearman_r',
                    'p_raw', 'p_clip', 'q_raw', 'q_clip']:
            save_dict[f'{cv_name}_{key}'] = v[key]
        save_dict[f'{cv_name}_null_raw_dist'] = v['null_raw_dist']
        save_dict[f'{cv_name}_null_clip_dist'] = v['null_clip_dist']

    out_path = OUTPUT_DIR / f'exp29_m1_brain_alignment_{args.model}.npz'
    np.savez(out_path, **save_dict)
    print(f"\nSaved → {out_path}\nDone.")

if __name__ == '__main__':
    main()
