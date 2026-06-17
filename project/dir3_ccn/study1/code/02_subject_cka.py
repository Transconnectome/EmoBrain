"""
CCN Analysis 02: Per-subject CKA — Brain-JEPA vs V-JEPA2 / CLIP

Purpose:
    For each subject, compute CKA between their Brain-JEPA RSM and model RSMs.
    Shows subject-level consistency of the overall alignment finding.

    Overall result already known:
        V-JEPA2 CKA = 0.1282 (p<0.0001)
        CLIP CKA     = 0.1115 (p<0.0001)
        Δ = +0.017   (p=0.017)
    This script breaks it down per subject.

Input:
    CCN/results/brain_jepa_rsm_per_subject.npy  (5, 2196, 2196)
    cka_results/rsm_vjepa2.npy
    cka_results/rsm_clip.npy

Output:
    CCN/results/subject_cka_results.npz
"""

import numpy as np
from pathlib import Path
import time

# ── Paths ─────────────────────────────────────────────────────────────────────
RSM_PER_SUBJ_PATH = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results/brain_jepa_rsm_per_subject.npy")
VJEPA2_RSM_PATH   = Path("/pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_vjepa2.npy")
CLIP_RSM_PATH     = Path("/pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_clip.npy")
OUTPUT_DIR        = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results")

# ── CKA ───────────────────────────────────────────────────────────────────────
def center_matrix(K):
    row_mean   = K.mean(axis=1, keepdims=True)
    col_mean   = K.mean(axis=0, keepdims=True)
    grand_mean = K.mean()
    return K - row_mean - col_mean + grand_mean

def cka(K1, K2):
    K1c = center_matrix(K1)
    K2c = center_matrix(K2)
    hsic_12 = np.sum(K1c * K2c)
    hsic_11 = np.sum(K1c * K1c)
    hsic_22 = np.sum(K2c * K2c)
    return float(hsic_12 / (np.sqrt(hsic_11 * hsic_22) + 1e-10))

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
rsm_per_subj = np.load(RSM_PER_SUBJ_PATH).astype(np.float64)  # (5, 2196, 2196)
rsm_vjepa2   = np.load(VJEPA2_RSM_PATH).astype(np.float64)
rsm_clip     = np.load(CLIP_RSM_PATH).astype(np.float64)
print(f"  Brain-JEPA per-subject RSMs: {rsm_per_subj.shape}")

# Pre-center model RSMs (shared across subjects)
rsm_vjepa2_c = center_matrix(rsm_vjepa2)
rsm_clip_c   = center_matrix(rsm_clip)
hsic_vv = np.sum(rsm_vjepa2_c * rsm_vjepa2_c)
hsic_cc = np.sum(rsm_clip_c   * rsm_clip_c)

# ── Per-subject CKA ───────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("PER-SUBJECT CKA: Brain-JEPA vs V-JEPA2 / CLIP")
print(f"{'='*60}")
print(f"{'Subject':<10}  {'V-JEPA2':>10}  {'CLIP':>10}  {'Δ(V-C)':>10}")

cka_vjepa = np.zeros(5)
cka_clip  = np.zeros(5)

for s in range(5):
    t0 = time.time()
    rsm_s = rsm_per_subj[s]

    # Efficient: re-use pre-centered model matrices
    rsm_s_c  = center_matrix(rsm_s)
    hsic_ss  = np.sum(rsm_s_c * rsm_s_c)
    hsic_sv  = np.sum(rsm_s_c * rsm_vjepa2_c)
    hsic_sc  = np.sum(rsm_s_c * rsm_clip_c)

    cka_vjepa[s] = float(hsic_sv / (np.sqrt(hsic_ss * hsic_vv) + 1e-10))
    cka_clip[s]  = float(hsic_sc / (np.sqrt(hsic_ss * hsic_cc) + 1e-10))
    delta = cka_vjepa[s] - cka_clip[s]

    print(f"  sub-{s+1:02d}      {cka_vjepa[s]:>10.4f}  {cka_clip[s]:>10.4f}  {delta:>+10.4f}  [{time.time()-t0:.0f}s]")

print(f"  {'Mean':<10}  {cka_vjepa.mean():>10.4f}  {cka_clip.mean():>10.4f}  "
      f"{(cka_vjepa-cka_clip).mean():>+10.4f}")
print(f"  {'Std':<10}  {cka_vjepa.std():>10.4f}  {cka_clip.std():>10.4f}")
print(f"\n  V-JEPA2 > CLIP: {(cka_vjepa > cka_clip).sum()}/5 subjects")
print(f"\n  Reference (mean across subjects, Brain-JEPA mean):")
print(f"    V-JEPA2 = 0.1282, CLIP = 0.1115, Δ = +0.017 (p=0.017)")

# ── Save ──────────────────────────────────────────────────────────────────────
np.savez(OUTPUT_DIR / "subject_cka_results.npz",
         cka_vjepa_per_subj=cka_vjepa,
         cka_clip_per_subj=cka_clip,
         delta_per_subj=cka_vjepa - cka_clip,
         mean_cka_vjepa=cka_vjepa.mean(),
         mean_cka_clip=cka_clip.mean())

print(f"\nSaved: {OUTPUT_DIR}/subject_cka_results.npz")
