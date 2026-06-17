"""
CCN Analysis 01: Brain-JEPA Subject-level RSM

Purpose:
    Compute per-subject RSM from Brain-JEPA embeddings.
    Subject-averaged RSM = shared neural emotion geometry.

Note:
    rsm_brain.npy already exists = RSM of MEAN embedding (mean first, then RSM).
    This script computes: per-subject RSM, then MEAN of per-subject RSMs.
    These are subtly different. Both are saved.

Input:
    brain_embeddings/brain_jepa_embeddings.npy  (5, 2196, 768)

Output:
    CCN/results/brain_jepa_rsm_per_subject.npy  (5, 2196, 2196)
    CCN/results/brain_jepa_rsm_mean.npy         (2196, 2196)
    CCN/results/brain_jepa_rsm_stats.npz
"""

import numpy as np
from pathlib import Path
from scipy.stats import spearmanr
import time

# ── Paths ─────────────────────────────────────────────────────────────────────
BRAIN_EMB_PATH = Path("/pscratch/sd/s/sjmoon/EmoFM/brain_embeddings/brain_jepa_embeddings.npy")
OUTPUT_DIR     = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

N_SUBJECTS = 5
N_STIMULI  = 2196

def cosine_rsm(X):
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    X_n = X / (norms + 1e-8)
    return (X_n @ X_n.T).astype(np.float32)

# ── Load Brain-JEPA embeddings ────────────────────────────────────────────────
print("Loading Brain-JEPA embeddings...")
brain_emb = np.load(BRAIN_EMB_PATH).astype(np.float32)  # (5, 2196, 768)
print(f"  Shape: {brain_emb.shape}")

# ── Per-subject RSMs ──────────────────────────────────────────────────────────
print("\nComputing per-subject RSMs...")
rsm_per_subj = np.zeros((N_SUBJECTS, N_STIMULI, N_STIMULI), dtype=np.float32)
for s in range(N_SUBJECTS):
    t0 = time.time()
    rsm_per_subj[s] = cosine_rsm(brain_emb[s].astype(np.float64))
    print(f"  sub-{s+1:02d}: done  [{time.time()-t0:.1f}s]")

# ── Subject-averaged RSM ──────────────────────────────────────────────────────
rsm_mean = rsm_per_subj.mean(axis=0)  # (2196, 2196)
print(f"\nSubject-averaged RSM: {rsm_mean.shape}")
print(f"  off-diagonal mean: {rsm_mean[~np.eye(N_STIMULI, dtype=bool)].mean():.4f}")

# ── Cross-subject consistency ─────────────────────────────────────────────────
print("\nCross-subject RSM consistency (Spearman r):")
idx = np.triu_indices(N_STIMULI, k=1)
tris = [rsm_per_subj[s][idx] for s in range(N_SUBJECTS)]

rsa_mat = np.zeros((N_SUBJECTS, N_SUBJECTS))
for i in range(N_SUBJECTS):
    for j in range(N_SUBJECTS):
        rsa_mat[i, j] = spearmanr(tris[i], tris[j]).statistic

print("  5×5 Spearman r matrix:")
for i in range(N_SUBJECTS):
    row = "  ".join(f"{rsa_mat[i,j]:.4f}" for j in range(N_SUBJECTS))
    print(f"    sub-{i+1:02d}: {row}")
off_mask = ~np.eye(N_SUBJECTS, dtype=bool)
print(f"  Off-diagonal mean: {rsa_mat[off_mask].mean():.4f} ± {rsa_mat[off_mask].std():.4f}")
print(f"  (compare: raw fMRI cross-subj r = 0.083)")

# ── Save ──────────────────────────────────────────────────────────────────────
np.save(OUTPUT_DIR / "brain_jepa_rsm_per_subject.npy", rsm_per_subj)
np.save(OUTPUT_DIR / "brain_jepa_rsm_mean.npy",        rsm_mean)
np.savez(OUTPUT_DIR / "brain_jepa_rsm_stats.npz",
         rsa_cross_subject=rsa_mat,
         off_diag_mean=rsa_mat[off_mask].mean(),
         off_diag_std=rsa_mat[off_mask].std())

print(f"\nSaved:")
print(f"  {OUTPUT_DIR}/brain_jepa_rsm_per_subject.npy")
print(f"  {OUTPUT_DIR}/brain_jepa_rsm_mean.npy")
print(f"  {OUTPUT_DIR}/brain_jepa_rsm_stats.npz")
