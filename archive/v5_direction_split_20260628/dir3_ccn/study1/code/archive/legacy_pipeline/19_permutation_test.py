"""
Exp 19: Permutation test for brain-predictable PC definition
Replaces R² > 0.01 threshold with FDR-corrected permutation test (n=1000).

Permutations run for all 100 PCs.
Exception: when observed R² = 0 (after max-clipping), p = 1.0 by construction —
  null R² values are also clipped at 0, so every null value satisfies null >= 0 = observed,
  making p trivially 1.0 without needing simulation.
"""

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.decomposition import PCA

# ─── Load data ─────────────────────────────────────────────────────────────────
print("Loading data...")
brain_raw = np.load('/pscratch/sd/s/sjmoon/EmoFM/brain_embeddings/brain_jepa_embeddings.npy')
vjepa_raw = np.load('/pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy')

brain = brain_raw.mean(axis=0)                # (2196, 768) — subject-mean
print(f"Brain shape: {brain.shape}, V-JEPA2 shape: {vjepa_raw.shape}")

# PCA on V-JEPA2 → 100 PCs (same as in original pipeline)
print("Fitting PCA on V-JEPA2...")
pca = PCA(n_components=100, random_state=42)
vjepa_pcs = pca.fit_transform(vjepa_raw)      # (2196, 100)
print(f"V-JEPA2 PCs shape: {vjepa_pcs.shape}")

# ─── Setup ─────────────────────────────────────────────────────────────────────
n_pcs   = 100
n_perm  = 1000
alpha   = 0.05
rng     = np.random.default_rng(42)

model = Pipeline([
    ('scaler', StandardScaler()),
    ('ridge',  Ridge(alpha=1.0)),
])

# ─── Observed R² for all 100 PCs ───────────────────────────────────────────────
print("Computing observed R² (5-fold CV) for all 100 PCs...")
r2_obs = np.zeros(n_pcs)
for i in range(n_pcs):
    scores = cross_val_score(model, brain, vjepa_pcs[:, i], cv=5, scoring='r2')
    r2_obs[i] = max(scores.mean(), 0.0)
    if (i + 1) % 10 == 0:
        print(f"  PC{i+1}: R²={r2_obs[i]:.6f}")

print(f"\nObserved R² (all 100):")
print(r2_obs)
nonzero_pcs = np.where(r2_obs > 0)[0]
print(f"PCs with R² > 0: {nonzero_pcs + 1} → R²={r2_obs[nonzero_pcs]}")

# ─── Permutation test ──────────────────────────────────────────────────────────
# For PCs where observed R² = 0 (after max-clipping):
#   All null values are also clipped to ≥ 0 = observed, so p = 1.0 by construction.
#   No simulation needed — this is a mathematical statement, not a threshold.
# For PCs where observed R² > 0: run n_perm permutations.

r2_null  = np.zeros((n_pcs, n_perm))
p_values = np.ones(n_pcs)   # default p=1.0 for R²=0 PCs

n_test = len(nonzero_pcs)
print(f"\nRunning {n_perm} permutations for {n_test} PC(s) with observed R² > 0...")
for idx, i in enumerate(nonzero_pcs):
    target = vjepa_pcs[:, i]
    for p in range(n_perm):
        target_perm = rng.permutation(target)
        null_score  = cross_val_score(model, brain, target_perm, cv=5, scoring='r2')
        r2_null[i, p] = max(null_score.mean(), 0.0)
    p_values[i] = np.mean(r2_null[i] >= r2_obs[i])
    print(f"  [{idx+1}/{n_test}] PC{i+1}: obs R²={r2_obs[i]:.4f}, "
          f"p={p_values[i]:.4f} "
          f"(null mean={r2_null[i].mean():.4f}, max={r2_null[i].max():.4f})")

# ─── FDR correction (Benjamini-Hochberg, manual — statsmodels not available) ───
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

p_corrected     = fdr_bh(p_values)
brain_pred_mask = p_corrected < alpha

# ─── Report ────────────────────────────────────────────────────────────────────
pred_pcs = np.where(brain_pred_mask)[0]
print("\n" + "="*60)
print("PERMUTATION TEST RESULTS")
print("="*60)
print(f"Brain-predictable PCs (1-indexed): {pred_pcs + 1}")
print(f"Observed R²:            {r2_obs[brain_pred_mask]}")
print(f"Raw p-values:           {p_values[brain_pred_mask]}")
print(f"FDR-corrected p-values: {p_corrected[brain_pred_mask]}")
print()

old_mask = np.array([0.3728, 0.0748, 0.0878, 0.0003] + [0]*96) > 0.01
# Recompute with actual observed R²
old_mask2 = r2_obs > 0.01
print(f"Original threshold (R²>0.01) PCs:  {np.where(old_mask2)[0] + 1}")
print(f"Permutation test PCs:              {pred_pcs + 1}")
same = np.array_equal(old_mask2, brain_pred_mask)
print(f"Same result? {'Yes — original threshold validated' if same else 'No — update downstream analyses'}")
print("="*60)

# ─── Save ──────────────────────────────────────────────────────────────────────
out_path = '/pscratch/sd/s/sjmoon/EmoFM/CCN/results/permutation_test_results.npz'
np.savez(out_path,
         r2_obs=r2_obs,
         r2_null=r2_null,
         p_values=p_values,
         p_corrected=p_corrected,
         brain_pred_mask=brain_pred_mask,
         n_perm=n_perm,
         alpha=alpha)
print(f"\nSaved → {out_path}")
