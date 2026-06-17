"""
CCN Analysis 10: CKA/RSA vs k + Brain-predictable dimensions

실험 1: CKA(brain_k, vjepa_k) vs k
    Brain embedding과 V-JEPA2/CLIP embedding 사이의 직접 CKA가
    k에 따라 어떻게 변하는가? k=27 근방에서 plateau?

실험 2: RSA(RSM_brain_k, RSM_vjepa_k) vs k
    각 k에서 PCA 축소 후 cosine RSM을 만들고
    brain RSM과 model RSM의 Spearman r이 k에 따라 어떻게 변하는가?

실험 3: Brain-predictable V-JEPA2 dimensions
    V-JEPA2의 각 PC를 brain embedding으로 얼마나 예측할 수 있는가?
    Cumulative curve가 k=27 근방에서 saturation되는가?
    → "brain이 접근 가능한 video model의 구조는 ~27차원"

Input:
    brain_embeddings/brain_jepa_embeddings.npy  (5, 2196, 768)
    video_embeddings/vjepa2_embeddings.npy      (2196, 1408)
    video_embeddings/clip_embeddings.npy        (2196, 512)

Output:
    CCN/results/cka_rsa_vs_k.npz
    CCN/results/brain_predictable_dims.npz
    CCN/figures/cka_rsa_vs_k.png
    CCN/figures/brain_predictable_dims.png
"""

import numpy as np
from pathlib import Path
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

# ── Paths ─────────────────────────────────────────────────────────────────────
BRAIN_PATH  = Path("/pscratch/sd/s/sjmoon/EmoFM/brain_embeddings/brain_jepa_embeddings.npy")
VJEPA2_PATH = Path("/pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy")
CLIP_PATH   = Path("/pscratch/sd/s/sjmoon/EmoFM/video_embeddings/clip_embeddings.npy")
OUTPUT_DIR  = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results")
FIG_DIR     = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

K_VALUES  = [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]
N_DIM     = 100   # number of PCs for Exp 3
SEED      = 42

# ── CKA helpers ───────────────────────────────────────────────────────────────
def center_gram(K):
    """Double-center Gram matrix."""
    row  = K.mean(axis=1, keepdims=True)
    col  = K.mean(axis=0, keepdims=True)
    grand = K.mean()
    return K - row - col + grand

def linear_cka(X, Y):
    """Linear CKA between feature matrices X (n,p) and Y (n,q)."""
    # Gram matrices
    Kx = X @ X.T
    Ky = Y @ Y.T
    Kxc = center_gram(Kx)
    Kyc = center_gram(Ky)
    hsic_xy = np.sum(Kxc * Kyc)
    hsic_xx = np.sum(Kxc * Kxc)
    hsic_yy = np.sum(Kyc * Kyc)
    return float(hsic_xy / (np.sqrt(hsic_xx * hsic_yy) + 1e-10))

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
brain_emb  = np.load(BRAIN_PATH).astype(np.float64)
brain_mean = brain_emb.mean(axis=0)    # (2196, 768)
vjepa_emb  = np.load(VJEPA2_PATH).astype(np.float64)
clip_emb   = np.load(CLIP_PATH).astype(np.float64)
print(f"  brain_mean: {brain_mean.shape}")
print(f"  vjepa2:     {vjepa_emb.shape}")
print(f"  clip:       {clip_emb.shape}")

# ══════════════════════════════════════════════════════════════════════════════
# 실험 1: CKA(brain_k, model_k) vs k
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{'='*65}")
print("실험 1: Linear CKA(brain_k, model_k) vs k")
print("방법: PCA(k)로 각 embedding 축소 → linear CKA 직접 계산")
print(f"{'='*65}")
print(f"{'k':>4}  {'CKA_vjepa':>10}  {'CKA_clip':>9}  {'Δ(v-c)':>8}")

cka_v = []
cka_c = []

for k in K_VALUES:
    t0 = time.time()
    brain_k = PCA(n_components=k, random_state=SEED).fit_transform(brain_mean)
    vjepa_k = PCA(n_components=k, random_state=SEED).fit_transform(vjepa_emb)
    clip_k  = PCA(n_components=k, random_state=SEED).fit_transform(clip_emb)

    cv = linear_cka(brain_k, vjepa_k)
    cc = linear_cka(brain_k, clip_k)
    cka_v.append(cv)
    cka_c.append(cc)
    print(f"{k:>4}  {cv:>10.6f}  {cc:>9.6f}  {cv-cc:>+8.6f}  [{time.time()-t0:.0f}s]")

cka_v = np.array(cka_v)
cka_c = np.array(cka_c)

k27_idx = K_VALUES.index(27)
print(f"\nAt k=27: CKA_vjepa={cka_v[k27_idx]:.6f} ({cka_v[k27_idx]/cka_v.max()*100:.1f}% of max={cka_v.max():.6f})")
print(f"         CKA_clip ={cka_c[k27_idx]:.6f} ({cka_c[k27_idx]/cka_c.max()*100:.1f}% of max={cka_c.max():.6f})")
print(f"V-JEPA2 > CLIP in CKA: {(cka_v > cka_c).sum()}/{len(K_VALUES)} k values")

# ══════════════════════════════════════════════════════════════════════════════
# 실험 2: RSA(RSM_brain_k, RSM_model_k) vs k
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{'='*65}")
print("실험 2: RSA(RSM_brain_k, RSM_model_k) vs k")
print("방법: PCA(k) → cosine RSM → Spearman r(brain RSM, model RSM)")
print(f"{'='*65}")
print(f"{'k':>4}  {'RSA_vjepa':>10}  {'RSA_clip':>9}  {'Δ(v-c)':>8}")

N = 2196
idx_upper = np.triu_indices(N, k=1)

rsa_v = []
rsa_c = []

for k in K_VALUES:
    t0 = time.time()
    brain_k = PCA(n_components=k, random_state=SEED).fit_transform(brain_mean)
    vjepa_k = PCA(n_components=k, random_state=SEED).fit_transform(vjepa_emb)
    clip_k  = PCA(n_components=k, random_state=SEED).fit_transform(clip_emb)

    rsm_b = cosine_similarity(brain_k)
    rsm_v = cosine_similarity(vjepa_k)
    rsm_c = cosine_similarity(clip_k)

    rv = spearmanr(rsm_b[idx_upper], rsm_v[idx_upper]).statistic
    rc = spearmanr(rsm_b[idx_upper], rsm_c[idx_upper]).statistic
    rsa_v.append(rv)
    rsa_c.append(rc)
    print(f"{k:>4}  {rv:>10.6f}  {rc:>9.6f}  {rv-rc:>+8.6f}  [{time.time()-t0:.0f}s]")

rsa_v = np.array(rsa_v)
rsa_c = np.array(rsa_c)

print(f"\nAt k=27: RSA_vjepa={rsa_v[k27_idx]:.6f} ({rsa_v[k27_idx]/rsa_v.max()*100:.1f}% of max)")
print(f"         RSA_clip ={rsa_c[k27_idx]:.6f} ({rsa_c[k27_idx]/rsa_c.max()*100:.1f}% of max)")
print(f"V-JEPA2 > CLIP in RSA: {(rsa_v > rsa_c).sum()}/{len(K_VALUES)} k values")

# ══════════════════════════════════════════════════════════════════════════════
# 실험 3: Brain-predictable V-JEPA2 dimensions
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{'='*65}")
print("실험 3: Brain-predictable V-JEPA2/CLIP dimensions")
print("방법: model PCA(100) → 각 PC를 brain으로 Ridge 5-fold CV 예측")
print("      PC order curve (variance 순) + sorted curve (R² 순)")
print(f"{'='*65}")

def compute_brain_predictable(brain, model_emb, n_dim=N_DIM, label=""):
    """
    model_emb → PCA(n_dim) → 각 PC를 brain으로 Ridge 5-fold CV R² 예측
    Returns: r2_per_dim (n_dim,), cumul_variance_order, cumul_sorted_order
    """
    pca = PCA(n_components=n_dim, random_state=SEED)
    model_pcs = pca.fit_transform(model_emb)     # (2196, n_dim)
    var_ratio = pca.explained_variance_ratio_     # (n_dim,)

    pipe = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

    r2_per_dim = np.zeros(n_dim)
    print(f"\n  {label}: predicting {n_dim} PCs from brain ({brain.shape[1]}-dim)...")
    t_all = time.time()
    for i in range(n_dim):
        r2 = cross_val_score(pipe, brain, model_pcs[:, i], cv=5, scoring='r2').mean()
        r2_per_dim[i] = max(r2, 0.0)
        if (i+1) % 20 == 0:
            print(f"    PC {i+1}/{n_dim}  [{time.time()-t_all:.0f}s]  "
                  f"last R²={r2_per_dim[i-19:i+1].mean():.4f}")

    # Curve 1: PC 순서대로 (variance order)
    cumul_var_order = np.cumsum(r2_per_dim)

    # Curve 2: R² 높은 순으로 정렬 (brain-predictability order)
    sorted_idx = np.argsort(-r2_per_dim)
    cumul_sorted = np.cumsum(r2_per_dim[sorted_idx])

    # Saturation: 95% of total cumulative R²
    total_r2 = cumul_var_order[-1]
    if total_r2 > 0:
        sat_var   = int(np.argmax(cumul_var_order    >= 0.95 * total_r2)) + 1
        sat_sorted = int(np.argmax(cumul_sorted       >= 0.95 * total_r2)) + 1
    else:
        sat_var = sat_sorted = n_dim

    print(f"  {label} total predictable R²: {total_r2:.4f}")
    print(f"  {label} 95% saturation: variance-order at PC={sat_var}, sorted at PC={sat_sorted}")
    print(f"  {label} top-10 predictable PCs (sorted by R²):")
    for rank, pc_i in enumerate(sorted_idx[:10]):
        print(f"    rank {rank+1}: PC{pc_i+1}  R²={r2_per_dim[pc_i]:.4f}  "
              f"var_explained={var_ratio[pc_i]*100:.2f}%")

    return r2_per_dim, cumul_var_order, cumul_sorted, sat_var, sat_sorted, var_ratio

# V-JEPA2
r2_vjepa, cumul_vjepa_var, cumul_vjepa_sorted, sat_v_var, sat_v_sort, vjepa_var = \
    compute_brain_predictable(brain_mean, vjepa_emb, N_DIM, "V-JEPA2")

# CLIP
r2_clip, cumul_clip_var, cumul_clip_sorted, sat_c_var, sat_c_sort, clip_var = \
    compute_brain_predictable(brain_mean, clip_emb, N_DIM, "CLIP")

print(f"\n{'='*65}")
print("실험 3 요약")
print(f"{'='*65}")
print(f"  V-JEPA2: 95% sat — variance-order PC={sat_v_var}, sorted PC={sat_v_sort}")
print(f"  CLIP:    95% sat — variance-order PC={sat_c_var}, sorted PC={sat_c_sort}")
print(f"  [Reference: k=27 from Cowen 2017]")

# PC별 R² 상위 30개 출력
print(f"\n  PC-by-PC R² (첫 30개, variance order):")
print(f"  {'PC':>4}  {'R2_vjepa':>10}  {'R2_clip':>9}  {'cumR2_v':>9}  {'cumR2_c':>9}")
for i in range(30):
    print(f"  {i+1:>4}  {r2_vjepa[i]:>10.4f}  {r2_clip[i]:>9.4f}  "
          f"{cumul_vjepa_var[i]:>9.4f}  {cumul_clip_var[i]:>9.4f}")

# ── Figures ───────────────────────────────────────────────────────────────────
print("\nGenerating figures...")

# Figure 1: Exp 1+2 combined (CKA and RSA vs k)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor('white')

ax = axes[0]
ax.plot(K_VALUES, cka_v, 'b-o', linewidth=2, markersize=6, label='Brain vs V-JEPA2')
ax.plot(K_VALUES, cka_c, 'r-o', linewidth=2, markersize=6, label='Brain vs CLIP')
ax.axvline(x=27, color='gray', linestyle='--', alpha=0.8, linewidth=1.5, label='k=27 (Cowen 2017)')
# mark k where each curve is at 95% of its max
for curve, color, name in [(cka_v, 'b', 'V-JEPA2'), (cka_c, 'r', 'CLIP')]:
    thresh = 0.95 * curve.max()
    k95 = K_VALUES[int(np.argmax(curve >= thresh))]
    ax.axvline(x=k95, color=color, linestyle=':', alpha=0.5, linewidth=1.2,
               label=f'95% max {name} (k={k95})')
ax.set_xlabel('Number of PCA dimensions (k)', fontsize=12)
ax.set_ylabel('Linear CKA (embedding-level)', fontsize=12)
ax.set_title('Exp 1: Direct CKA(brain_k, model_k) vs k', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

ax = axes[1]
ax.plot(K_VALUES, rsa_v, 'b-o', linewidth=2, markersize=6, label='Brain vs V-JEPA2')
ax.plot(K_VALUES, rsa_c, 'r-o', linewidth=2, markersize=6, label='Brain vs CLIP')
ax.axvline(x=27, color='gray', linestyle='--', alpha=0.8, linewidth=1.5, label='k=27 (Cowen 2017)')
ax.set_xlabel('Number of PCA dimensions (k)', fontsize=12)
ax.set_ylabel('Spearman r (RSM_brain_k vs RSM_model_k)', fontsize=12)
ax.set_title('Exp 2: RSA(RSM_brain_k, RSM_model_k) vs k', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

plt.tight_layout()
fig1_path = FIG_DIR / "cka_rsa_vs_k.png"
plt.savefig(fig1_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig1_path}")
plt.close()

# Figure 2: Exp 3 — brain-predictable dims
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor('white')
dims = np.arange(1, N_DIM + 1)

# Panel 1: Variance order cumulative
ax = axes[0]
ax.plot(dims, cumul_vjepa_var, 'b-', linewidth=2, label='V-JEPA2 (cumulative R²)')
ax.plot(dims, cumul_clip_var,  'r-', linewidth=2, label='CLIP (cumulative R²)')
ax.axvline(x=27, color='gray', linestyle='--', alpha=0.8, linewidth=1.5, label='k=27 (Cowen 2017)')
ax.axvline(x=sat_v_var, color='b', linestyle=':', alpha=0.6, linewidth=1.2,
           label=f'V-JEPA2 95% sat (k={sat_v_var})')
ax.axvline(x=sat_c_var, color='r', linestyle=':', alpha=0.6, linewidth=1.2,
           label=f'CLIP 95% sat (k={sat_c_var})')
ax.set_xlabel('PC index (variance order, top PC = 1)', fontsize=12)
ax.set_ylabel('Cumulative brain-predictable R²', fontsize=12)
ax.set_title('Exp 3a: Brain-predictable dims (variance order)', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

# Panel 2: Sorted by brain-predictability
ax = axes[1]
ax.plot(dims, cumul_vjepa_sorted, 'b-', linewidth=2, label='V-JEPA2')
ax.plot(dims, cumul_clip_sorted,  'r-', linewidth=2, label='CLIP')
ax.axvline(x=27, color='gray', linestyle='--', alpha=0.8, linewidth=1.5, label='k=27 (Cowen 2017)')
ax.axvline(x=sat_v_sort, color='b', linestyle=':', alpha=0.6, linewidth=1.2,
           label=f'V-JEPA2 95% sat (k={sat_v_sort})')
ax.axvline(x=sat_c_sort, color='r', linestyle=':', alpha=0.6, linewidth=1.2,
           label=f'CLIP 95% sat (k={sat_c_sort})')
ax.set_xlabel('Number of dims included (sorted by brain-predictability)', fontsize=12)
ax.set_ylabel('Cumulative brain-predictable R²', fontsize=12)
ax.set_title('Exp 3b: Brain-predictable dims (sorted by R², upper bound)',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

plt.tight_layout()
fig2_path = FIG_DIR / "brain_predictable_dims.png"
plt.savefig(fig2_path, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig2_path}")
plt.close()

# ── Save ──────────────────────────────────────────────────────────────────────
np.savez(OUTPUT_DIR / "cka_rsa_vs_k.npz",
         k_values=np.array(K_VALUES),
         cka_brain_vjepa=cka_v,
         cka_brain_clip=cka_c,
         rsa_brain_vjepa=rsa_v,
         rsa_brain_clip=rsa_c)

np.savez(OUTPUT_DIR / "brain_predictable_dims.npz",
         r2_vjepa_per_dim=r2_vjepa,
         r2_clip_per_dim=r2_clip,
         cumul_vjepa_var_order=cumul_vjepa_var,
         cumul_clip_var_order=cumul_clip_var,
         cumul_vjepa_sorted=cumul_vjepa_sorted,
         cumul_clip_sorted=cumul_clip_sorted,
         vjepa_pca_var_ratio=vjepa_var,
         clip_pca_var_ratio=clip_var,
         sat_vjepa_var_order=sat_v_var,
         sat_clip_var_order=sat_c_var,
         sat_vjepa_sorted=sat_v_sort,
         sat_clip_sorted=sat_c_sort)

print(f"\nSaved: {OUTPUT_DIR}/cka_rsa_vs_k.npz")
print(f"Saved: {OUTPUT_DIR}/brain_predictable_dims.npz")
print("\nDone.")
