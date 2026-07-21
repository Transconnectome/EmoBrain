"""
Exp 29: R² clipping artifact check.

Issue: Original permutation test (19_permutation_test.py, 23_reverse_pca_ridge.py)
uses max(R², 0) clipping on both observed and null R² values. This may inflate
p-values for PCs with small observed R² by piling null mass at 0.

This script re-runs the permutation test WITHOUT clipping and compares.

Output: per-PC p-value comparison (clipped vs raw), so we can see if PC2/PC3
significance is robust to this methodological choice.
"""

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, KFold
from sklearn.decomposition import PCA
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BRAIN_PATH = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/data/raw/brain_embeddings/brain_jepa_embeddings.npy")
VJEPA_PATH = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/data/raw/video_embeddings/vjepa2_embeddings.npy")
OUTPUT_DIR = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/study1/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
brain_raw = np.load(BRAIN_PATH)
vjepa_raw = np.load(VJEPA_PATH)
brain = brain_raw.mean(axis=0)
print(f"  Brain: {brain.shape},  V-JEPA2: {vjepa_raw.shape}")

# ── PCA on V-JEPA2 ────────────────────────────────────────────────────────────
N_PC = 100
print(f"\nFitting PCA ({N_PC} components)...")
pca = PCA(n_components=N_PC, random_state=42)
vjepa_pcs = pca.fit_transform(vjepa_raw)
print(f"  Cumulative variance: {pca.explained_variance_ratio_.cumsum()[-1]:.4f}")

# ── Settings ──────────────────────────────────────────────────────────────────
N_PERM = 1000
ALPHA = 0.05
rng = np.random.default_rng(42)

model = Pipeline([
    ('scaler', StandardScaler()),
    ('ridge',  Ridge(alpha=1.0)),
])

# Use both fixed-order and shuffled KFold to also check CV leakage
cv_sequential = KFold(n_splits=5, shuffle=False)
cv_shuffled   = KFold(n_splits=5, shuffle=True, random_state=42)

# ── Observed R² (no clipping) ─────────────────────────────────────────────────
def compute_r2(X, y, cv):
    """Return raw mean CV R² without clipping."""
    return cross_val_score(model, X, y, cv=cv, scoring='r2').mean()

print(f"\nComputing observed R² (raw, no clipping)...")
r2_obs_raw_seq = np.array([compute_r2(brain, vjepa_pcs[:, i], cv_sequential) for i in range(N_PC)])
r2_obs_raw_shuf = np.array([compute_r2(brain, vjepa_pcs[:, i], cv_shuffled) for i in range(N_PC)])

# Also keep clipped version for comparison
r2_obs_clip_seq = np.maximum(r2_obs_raw_seq, 0.0)
r2_obs_clip_shuf = np.maximum(r2_obs_raw_shuf, 0.0)

print(f"\nTop PC R² (sequential CV):")
for i in range(5):
    print(f"  PC{i+1}: raw={r2_obs_raw_seq[i]:+.4f}, clipped={r2_obs_clip_seq[i]:.4f}")
print(f"\nTop PC R² (shuffled CV):")
for i in range(5):
    print(f"  PC{i+1}: raw={r2_obs_raw_shuf[i]:+.4f}, clipped={r2_obs_clip_shuf[i]:.4f}")

# ── Permutation test — both clipping variants × both CV variants ─────────────
print(f"\nRunning {N_PERM} permutations...")
print("  Variants: 2 (clip / raw) × 2 (sequential / shuffled CV) = 4")

# Only test PCs likely to be informative (top 20 by raw R²)
test_pcs = np.argsort(-r2_obs_raw_shuf)[:20]
print(f"  Testing top 20 PCs by shuffled-CV raw R²: {sorted(test_pcs + 1)}")

results = {}
for cv_name, cv_obj, r2_obs_raw, r2_obs_clip in [
    ('sequential', cv_sequential, r2_obs_raw_seq, r2_obs_clip_seq),
    ('shuffled',   cv_shuffled,   r2_obs_raw_shuf, r2_obs_clip_shuf),
]:
    print(f"\n  CV={cv_name}...")
    r2_null_raw  = np.zeros((N_PC, N_PERM))
    r2_null_clip = np.zeros((N_PC, N_PERM))
    p_raw  = np.ones(N_PC)
    p_clip = np.ones(N_PC)

    for idx, i in enumerate(test_pcs):
        target = vjepa_pcs[:, i]
        for p in range(N_PERM):
            target_perm = rng.permutation(target)
            null = cross_val_score(model, brain, target_perm, cv=cv_obj, scoring='r2').mean()
            r2_null_raw[i, p]  = null
            r2_null_clip[i, p] = max(null, 0.0)
        p_raw[i]  = np.mean(r2_null_raw[i]  >= r2_obs_raw[i])
        p_clip[i] = np.mean(r2_null_clip[i] >= r2_obs_clip[i])
        print(f"    [{idx+1}/20] PC{i+1}: raw R²={r2_obs_raw[i]:+.4f}, "
              f"p_raw={p_raw[i]:.4f}, p_clip={p_clip[i]:.4f} "
              f"(null mean raw={r2_null_raw[i].mean():+.4f}, clip={r2_null_clip[i].mean():.4f})")

    results[cv_name] = {
        'r2_obs_raw':  r2_obs_raw,
        'r2_obs_clip': r2_obs_clip,
        'p_raw':       p_raw,
        'p_clip':      p_clip,
        'r2_null_raw': r2_null_raw,
        'r2_null_clip': r2_null_clip,
    }

# ── FDR correction ────────────────────────────────────────────────────────────
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

print(f"\n{'='*70}")
print("SUMMARY: How does PC2 / PC3 significance change under variants?")
print(f"{'='*70}")

for cv_name in ['sequential', 'shuffled']:
    r = results[cv_name]
    q_raw  = fdr_bh(r['p_raw'])
    q_clip = fdr_bh(r['p_clip'])

    sig_raw  = np.where(q_raw  < ALPHA)[0] + 1
    sig_clip = np.where(q_clip < ALPHA)[0] + 1

    print(f"\n  CV = {cv_name}:")
    print(f"    Clipped null (original method) FDR-survived PCs: {sorted(sig_clip)}")
    print(f"    Raw null     (no artifact)     FDR-survived PCs: {sorted(sig_raw)}")
    same = np.array_equal(sorted(sig_clip), sorted(sig_raw))
    print(f"    Same? {'YES — robust' if same else 'NO — clipping changes conclusion'}")
    r['q_raw'] = q_raw
    r['q_clip'] = q_clip

# ── Save ──────────────────────────────────────────────────────────────────────
save_path = OUTPUT_DIR / 'exp29_r2_clipping_check.npz'
np.savez(save_path,
         r2_obs_raw_seq=r2_obs_raw_seq,
         r2_obs_clip_seq=r2_obs_clip_seq,
         r2_obs_raw_shuf=r2_obs_raw_shuf,
         r2_obs_clip_shuf=r2_obs_clip_shuf,
         seq_p_raw=results['sequential']['p_raw'],
         seq_p_clip=results['sequential']['p_clip'],
         seq_q_raw=results['sequential']['q_raw'],
         seq_q_clip=results['sequential']['q_clip'],
         shuf_p_raw=results['shuffled']['p_raw'],
         shuf_p_clip=results['shuffled']['p_clip'],
         shuf_q_raw=results['shuffled']['q_raw'],
         shuf_q_clip=results['shuffled']['q_clip'],
         test_pcs=test_pcs,
         n_perm=N_PERM)
print(f"\nSaved → {save_path}")
print("\nDone.")
