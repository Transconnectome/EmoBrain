"""
CCN Raw fMRI Analysis 07: Raw fMRI RSM → Cross-space RSA + CKA

Priority 1: Raw fMRI RSM → Cross-space RSA per emotion
Priority 2: Raw fMRI RSM → Overall CKA with permutation test + bootstrap CI

Motivation:
    Brain-JEPA RSM had RSA mean=-0.009 (near zero).
    Brain-JEPA may compress emotion-specific variance.
    Raw fMRI (5, 2196, 450) is the direct neural signal.
    If raw fMRI RSA mean > 0.02 → Brain-JEPA compresses emotion info.
    If raw fMRI RSA also near 0 → emotion kernel RSA approach itself is the issue.

Input:
    /pscratch/sd/s/sjmoon/EmoFM/raw_fmri_results/fmri_raw.npy     (5, 2196, 450)
    /pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_vjepa2.npy        (2196, 2196)
    /pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_clip.npy          (2196, 2196)
    metadata CSV

Output:
    CCN/results/raw_rsm_per_subject.npy   (5, 2196, 2196)  — per-subject cosine RSM
    CCN/results/raw_rsm_mean.npy          (2196, 2196)     — mean RSM
    CCN/results/raw_rsa_cka_results.npz   — all RSA + CKA + perm + boot results
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr
import time

# ── Paths ─────────────────────────────────────────────────────────────────────
FMRI_PATH      = Path("/pscratch/sd/s/sjmoon/EmoFM/raw_fmri_results/fmri_raw.npy")
VJEPA2_RSM     = Path("/pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_vjepa2.npy")
CLIP_RSM       = Path("/pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_clip.npy")
META_PATH      = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
OUTPUT_DIR     = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EMOTION_LABELS = [
    'Admiration','Adoration','Aesthetic appreciation','Amusement','Anger','Anxiety',
    'Awe','Awkwardness','Boredom','Calmness','Confusion','Contempt','Craving',
    'Disgust','Empathic pain','Entrancement','Excitement','Fear','Horror','Interest',
    'Joy','Nostalgia','Relief','Romance','Sadness','Satisfaction','Sexual desire',
    'Surprise','Sympathy','Triumph','Uncomfortable','Annoyance','Envy','Guilt'
]
N_EMO   = 34
N       = 2196
N_PERM  = 1000
N_BOOT  = 1000
SEED    = 42
rng     = np.random.default_rng(SEED)

# ── CKA helpers ───────────────────────────────────────────────────────────────
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

def cka_precentered(K1c, hsic_11, K2c, hsic_22):
    hsic_12 = np.sum(K1c * K2c)
    return float(hsic_12 / (np.sqrt(hsic_11 * hsic_22) + 1e-10))

def cosine_rsm(X):
    """Compute cosine similarity RSM. X: (N, D)"""
    X = X.astype(np.float64)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    X_norm = X / (norms + 1e-10)
    return X_norm @ X_norm.T   # (N, N)

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
fmri_raw   = np.load(FMRI_PATH)              # (5, 2196, 450) float32
rsm_vjepa2 = np.load(VJEPA2_RSM).astype(np.float64)
rsm_clip   = np.load(CLIP_RSM).astype(np.float64)
meta       = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

print(f"  fmri_raw:   {fmri_raw.shape}  dtype={fmri_raw.dtype}")
print(f"  rsm_vjepa2: {rsm_vjepa2.shape}")
print(f"  rsm_clip:   {rsm_clip.shape}")

# ── STEP 1: Per-subject cosine RSM ────────────────────────────────────────────
print(f"\n{'='*60}")
print("STEP 1: Computing per-subject cosine RSMs")
print(f"{'='*60}")

rsm_per_subj = np.zeros((5, N, N), dtype=np.float32)

for s in range(5):
    t0 = time.time()
    rsm_s = cosine_rsm(fmri_raw[s])   # (2196, 2196)
    rsm_per_subj[s] = rsm_s.astype(np.float32)
    print(f"  sub-{s+1:02d}: min={rsm_s.min():.4f}  max={rsm_s.max():.4f}  "
          f"mean={rsm_s.mean():.4f}  std={rsm_s.std():.4f}  [{time.time()-t0:.1f}s]")

rsm_raw_mean = rsm_per_subj.mean(axis=0).astype(np.float64)   # (2196, 2196)

# Cross-subject Spearman r consistency
idx_upper = np.triu_indices(N, k=1)
print(f"\n  Cross-subject Spearman r (5×5):")
r_mat = np.zeros((5, 5))
for i in range(5):
    for j in range(i+1, 5):
        r, _ = spearmanr(rsm_per_subj[i][idx_upper], rsm_per_subj[j][idx_upper])
        r_mat[i, j] = r_mat[j, i] = r
    r_mat[i, i] = 1.0
for row in r_mat:
    print("  ", ["%.4f" % v for v in row])
off_diag = r_mat[np.triu_indices(5, k=1)]
print(f"  off-diag mean: {off_diag.mean():.4f}  std: {off_diag.std():.4f}")

print(f"\n  Mean RSM stats: min={rsm_raw_mean.min():.4f}  max={rsm_raw_mean.max():.4f}  "
      f"mean={rsm_raw_mean.mean():.4f}  std={rsm_raw_mean.std():.4f}")

# Save RSMs
np.save(OUTPUT_DIR / "raw_rsm_per_subject.npy", rsm_per_subj)
np.save(OUTPUT_DIR / "raw_rsm_mean.npy", rsm_raw_mean.astype(np.float32))
print(f"\n  Saved: raw_rsm_per_subject.npy, raw_rsm_mean.npy")

# ── STEP 2: Cross-space RSA ───────────────────────────────────────────────────
print(f"\n{'='*75}")
print("STEP 2: Cross-space RSA (Spearman r, raw fMRI RSM)")
print(f"{'='*75}")
print(f"{'#':>3}  {'Emotion':<28}  {'RawFMRI':>8}  {'V-JEPA2':>8}  {'CLIP':>7}  {'Align':>7}  {'Diverg':>7}")

raw_tri    = rsm_raw_mean[idx_upper]
vjepa2_tri = rsm_vjepa2[idx_upper]
clip_tri   = rsm_clip[idx_upper]

rsa_raw    = np.zeros(N_EMO)
rsa_vjepa2 = np.zeros(N_EMO)
rsa_clip   = np.zeros(N_EMO)
alignment  = np.zeros(N_EMO)
divergence = np.zeros(N_EMO)

t_total = time.time()
for i in range(N_EMO):
    t0 = time.time()
    score_i = meta[f"score_{i}"].values.astype(np.float64)
    E_i_tri = np.outer(score_i, score_i)[idx_upper]

    rsa_raw[i]    = spearmanr(raw_tri,    E_i_tri).statistic
    rsa_vjepa2[i] = spearmanr(vjepa2_tri, E_i_tri).statistic
    rsa_clip[i]   = spearmanr(clip_tri,   E_i_tri).statistic

    alignment[i]  = min(rsa_raw[i], rsa_vjepa2[i])
    divergence[i] = abs(rsa_raw[i] - rsa_vjepa2[i])

    print(f"[{i:2d}] {EMOTION_LABELS[i]:<28}  "
          f"{rsa_raw[i]:>8.4f}  {rsa_vjepa2[i]:>8.4f}  {rsa_clip[i]:>7.4f}  "
          f"{alignment[i]:>7.4f}  {divergence[i]:>7.4f}  [{time.time()-t0:.0f}s]")

print(f"\nTotal RSA: {(time.time()-t_total)/60:.1f} min")

# RSA summary
print(f"\n{'='*60}")
print("RSA SUMMARY")
print(f"{'='*60}")
print(f"  Raw fMRI:  {rsa_raw.mean():.4f}  ±  {rsa_raw.std():.4f}")
print(f"  V-JEPA2:   {rsa_vjepa2.mean():.4f}  ±  {rsa_vjepa2.std():.4f}")
print(f"  CLIP:      {rsa_clip.mean():.4f}  ±  {rsa_clip.std():.4f}")
print(f"  [Brain-JEPA reference: -0.009]")
print(f"\n  Raw fMRI > V-JEPA2: {(rsa_raw > rsa_vjepa2).sum()}/34")
print(f"  Raw fMRI > CLIP:    {(rsa_raw > rsa_clip).sum()}/34")
print(f"  V-JEPA2  > CLIP:    {(rsa_vjepa2 > rsa_clip).sum()}/34")

print(f"\n  Top 5 Raw fMRI RSA:")
for idx_e in np.argsort(-rsa_raw)[:5]:
    print(f"    {EMOTION_LABELS[idx_e]:<28}  raw={rsa_raw[idx_e]:.4f}  vjepa={rsa_vjepa2[idx_e]:.4f}  clip={rsa_clip[idx_e]:.4f}")
print(f"\n  Top 5 Divergence (|raw - vjepa|):")
for idx_e in np.argsort(-divergence)[:5]:
    print(f"    {EMOTION_LABELS[idx_e]:<28}  raw={rsa_raw[idx_e]:.4f}  vjepa={rsa_vjepa2[idx_e]:.4f}  diverg={divergence[idx_e]:.4f}")

# Per-subject RSA
print(f"\n{'='*60}")
print("PER-SUBJECT RSA (mean across 34 emotions)")
print(f"{'='*60}")
rsa_raw_per_subj = np.zeros((5, N_EMO))
for s in range(5):
    t0 = time.time()
    sub_tri = rsm_per_subj[s].astype(np.float64)[idx_upper]
    for i in range(N_EMO):
        score_i = meta[f"score_{i}"].values.astype(np.float64)
        E_i_tri = np.outer(score_i, score_i)[idx_upper]
        rsa_raw_per_subj[s, i] = spearmanr(sub_tri, E_i_tri).statistic
    print(f"  sub-{s+1:02d}: mean_RSA={rsa_raw_per_subj[s].mean():.4f}  [{time.time()-t0:.0f}s]")
print(f"  Mean across subjects: {rsa_raw_per_subj.mean():.4f}  std: {rsa_raw_per_subj.std(axis=0).mean():.4f}")

# ── STEP 3: CKA (mean + per-subject) ──────────────────────────────────────────
print(f"\n{'='*60}")
print("STEP 3: CKA — Raw fMRI vs V-JEPA2 / CLIP")
print(f"{'='*60}")

# Pre-center model RSMs
rsm_vj_c = center_matrix(rsm_vjepa2)
rsm_cl_c = center_matrix(rsm_clip)
hsic_vv  = np.sum(rsm_vj_c * rsm_vj_c)
hsic_cc  = np.sum(rsm_cl_c * rsm_cl_c)

# Mean RSM CKA
cka_mean_vjepa = cka(rsm_raw_mean, rsm_vjepa2)
cka_mean_clip  = cka(rsm_raw_mean, rsm_clip)
print(f"  Mean RSM CKA:  V-JEPA2={cka_mean_vjepa:.6f}  CLIP={cka_mean_clip:.6f}  "
      f"Δ={cka_mean_vjepa-cka_mean_clip:+.6f}")
print(f"  [Brain-JEPA reference: V-JEPA2=0.0584  CLIP=0.0539  Δ=+0.0044]")

# Per-subject CKA
print(f"\n  {'Subject':<10}  {'V-JEPA2':>10}  {'CLIP':>10}  {'Δ(V-C)':>10}")
cka_vjepa_subj = np.zeros(5)
cka_clip_subj  = np.zeros(5)
for s in range(5):
    t0 = time.time()
    rsm_s_c = center_matrix(rsm_per_subj[s].astype(np.float64))
    hsic_ss = np.sum(rsm_s_c * rsm_s_c)
    cka_vjepa_subj[s] = cka_precentered(rsm_s_c, hsic_ss, rsm_vj_c, hsic_vv)
    cka_clip_subj[s]  = cka_precentered(rsm_s_c, hsic_ss, rsm_cl_c, hsic_cc)
    delta = cka_vjepa_subj[s] - cka_clip_subj[s]
    print(f"  sub-{s+1:02d}      {cka_vjepa_subj[s]:>10.6f}  {cka_clip_subj[s]:>10.6f}  {delta:>+10.6f}  [{time.time()-t0:.0f}s]")
print(f"  {'Mean':<10}  {cka_vjepa_subj.mean():>10.6f}  {cka_clip_subj.mean():>10.6f}  "
      f"{(cka_vjepa_subj-cka_clip_subj).mean():>+10.6f}")
print(f"  V-JEPA2 > CLIP: {(cka_vjepa_subj > cka_clip_subj).sum()}/5")

# ── STEP 4: Permutation test ───────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"STEP 4: Permutation test for CKA (N={N_PERM})")
print(f"{'='*60}")

rsm_mean_c = center_matrix(rsm_raw_mean)
hsic_mm    = np.sum(rsm_mean_c * rsm_mean_c)

perm_cka_vjepa = np.zeros(N_PERM)
perm_cka_clip  = np.zeros(N_PERM)
perm_delta     = np.zeros(N_PERM)

t0 = time.time()
for p in range(N_PERM):
    perm_idx = rng.permutation(N)
    rsm_perm = rsm_raw_mean[np.ix_(perm_idx, perm_idx)]
    rsm_perm_c = center_matrix(rsm_perm)
    hsic_pp   = np.sum(rsm_perm_c * rsm_perm_c)
    cv = cka_precentered(rsm_perm_c, hsic_pp, rsm_vj_c, hsic_vv)
    cc = cka_precentered(rsm_perm_c, hsic_pp, rsm_cl_c, hsic_cc)
    perm_cka_vjepa[p] = cv
    perm_cka_clip[p]  = cc
    perm_delta[p]     = cv - cc
    if (p+1) % 100 == 0:
        print(f"  perm {p+1}/{N_PERM}  [{time.time()-t0:.0f}s]")

p_val_vjepa = (perm_cka_vjepa >= cka_mean_vjepa).mean()
p_val_clip  = (perm_cka_clip  >= cka_mean_clip).mean()
p_val_delta = (perm_delta     >= (cka_mean_vjepa - cka_mean_clip)).mean()

print(f"\n  Observed: V-JEPA2={cka_mean_vjepa:.4f}  CLIP={cka_mean_clip:.4f}  Δ={cka_mean_vjepa-cka_mean_clip:+.4f}")
print(f"  Null mean: V-JEPA2={perm_cka_vjepa.mean():.4f}  CLIP={perm_cka_clip.mean():.4f}  Δ={perm_delta.mean():+.4f}")
print(f"  p-value:   V-JEPA2={p_val_vjepa:.4f}  CLIP={p_val_clip:.4f}  Δ={p_val_delta:.4f}")

# ── STEP 5: Bootstrap CI ──────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"STEP 5: Bootstrap CI for CKA (N={N_BOOT})")
print(f"{'='*60}")

boot_cka_vjepa = np.zeros(N_BOOT)
boot_cka_clip  = np.zeros(N_BOOT)
boot_delta     = np.zeros(N_BOOT)

t0 = time.time()
for b in range(N_BOOT):
    boot_idx = rng.integers(0, N, size=N)   # sample with replacement
    rsm_b = rsm_raw_mean[np.ix_(boot_idx, boot_idx)]
    bv = cka(rsm_b, rsm_vjepa2[np.ix_(boot_idx, boot_idx)])
    bc = cka(rsm_b, rsm_clip[np.ix_(boot_idx, boot_idx)])
    boot_cka_vjepa[b] = bv
    boot_cka_clip[b]  = bc
    boot_delta[b]     = bv - bc
    if (b+1) % 100 == 0:
        print(f"  boot {b+1}/{N_BOOT}  [{time.time()-t0:.0f}s]")

ci_lo_v, ci_hi_v = np.percentile(boot_cka_vjepa, [2.5, 97.5])
ci_lo_c, ci_hi_c = np.percentile(boot_cka_clip,  [2.5, 97.5])
ci_lo_d, ci_hi_d = np.percentile(boot_delta,      [2.5, 97.5])

print(f"\n  95% Bootstrap CI:")
print(f"    V-JEPA2: [{ci_lo_v:.4f}, {ci_hi_v:.4f}]  (observed={cka_mean_vjepa:.4f})")
print(f"    CLIP:    [{ci_lo_c:.4f}, {ci_hi_c:.4f}]  (observed={cka_mean_clip:.4f})")
print(f"    Δ(V-C):  [{ci_lo_d:.4f}, {ci_hi_d:.4f}]  (observed={cka_mean_vjepa-cka_mean_clip:+.4f})")

# ── Save ──────────────────────────────────────────────────────────────────────
np.savez(OUTPUT_DIR / "raw_rsa_cka_results.npz",
         # RSM stats
         cross_subj_r_mat=r_mat,
         cross_subj_off_diag_mean=off_diag.mean(),
         cross_subj_off_diag_std=off_diag.std(),
         rsm_mean_stats=np.array([rsm_raw_mean.min(), rsm_raw_mean.max(),
                                   rsm_raw_mean.mean(), rsm_raw_mean.std()]),
         # RSA
         emotion_labels=np.array(EMOTION_LABELS),
         rsa_raw=rsa_raw,
         rsa_vjepa2=rsa_vjepa2,
         rsa_clip=rsa_clip,
         alignment=alignment,
         divergence=divergence,
         rsa_raw_per_subj=rsa_raw_per_subj,
         # CKA mean
         cka_mean_vjepa=cka_mean_vjepa,
         cka_mean_clip=cka_mean_clip,
         cka_delta=cka_mean_vjepa - cka_mean_clip,
         # CKA per-subject
         cka_vjepa_per_subj=cka_vjepa_subj,
         cka_clip_per_subj=cka_clip_subj,
         cka_delta_per_subj=cka_vjepa_subj - cka_clip_subj,
         # Permutation test
         perm_cka_vjepa=perm_cka_vjepa,
         perm_cka_clip=perm_cka_clip,
         perm_delta=perm_delta,
         p_val_vjepa=p_val_vjepa,
         p_val_clip=p_val_clip,
         p_val_delta=p_val_delta,
         # Bootstrap CI
         boot_cka_vjepa=boot_cka_vjepa,
         boot_cka_clip=boot_cka_clip,
         boot_delta=boot_delta,
         ci_vjepa=np.array([ci_lo_v, ci_hi_v]),
         ci_clip=np.array([ci_lo_c, ci_hi_c]),
         ci_delta=np.array([ci_lo_d, ci_hi_d]))

print(f"\nSaved: {OUTPUT_DIR}/raw_rsa_cka_results.npz")
print(f"Saved: {OUTPUT_DIR}/raw_rsm_per_subject.npy")
print(f"Saved: {OUTPUT_DIR}/raw_rsm_mean.npy")
