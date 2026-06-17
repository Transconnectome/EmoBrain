"""
CCN Analysis 12: Dimensional Emotion Analysis (Arousal / Valence / Dominance)

목적:
  Script 11에서 categorical emotion (34개)에 대한 PC 분석을 했다.
  여기서는 dimensional emotion (Arousal, Valence, Dominance)에 대해:
  (A) 각 video model PC와 A/V/D의 Spearman r (전체 100 PC × 3)
  (B) brain이 A/V/D를 얼마나 직접 예측하는가 (Ridge CV)
  (C) brain-predictable PC가 A/V/D를 더 잘 표상하는가
  (D) video model PCA k차원으로 A/V/D를 예측할 때 R²가 k에 따라 어떻게 변하는가

  Exp 11과 합쳐서: "brain이 읽는 차원이 categorical emotion과 dimensional emotion 중
  어느 것과 더 aligned인가?" 비교 가능.

Input:
  video_embeddings/vjepa2_embeddings.npy    (2196, 1408)
  video_embeddings/clip_embeddings.npy      (2196, 512)
  brain_embeddings/brain_jepa_embeddings.npy  (5, 2196, 768)
  metadata CSV
  CCN/results/brain_predictable_dims.npz    (Script 10 Exp 3)

Output:
  CCN/results/dimensional_emotion_results.npz
  CCN/figures/dim_pc_avd_heatmap.png          — 100 PC × A/V/D heatmap (full)
  CCN/figures/dim_brain_pred_avd.png          — brain-pred vs unpred bar + scatter
  CCN/figures/dim_brain_avd_prediction.png    — brain → A/V/D direct Ridge CV R²
  CCN/figures/dim_avd_k_sweep.png             — model PC k차원 → A/V/D R² vs k
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE       = Path("/pscratch/sd/s/sjmoon/EmoFM")
VJEPA_PATH = BASE / "video_embeddings/vjepa2_embeddings.npy"
CLIP_PATH  = BASE / "video_embeddings/clip_embeddings.npy"
BRAIN_PATH = BASE / "brain_embeddings/brain_jepa_embeddings.npy"
META_PATH  = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
PRED_PATH  = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results/brain_predictable_dims.npz")
OUTPUT_DIR = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results")
FIG_DIR    = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

N_PC      = 100
R2_THRESH = 0.01
K_VALUES  = [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]
CV        = 5
AVD_LABELS = ['Arousal', 'Valence', 'Dominance']

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
vjepa      = np.load(VJEPA_PATH).astype(np.float64)
clip_emb   = np.load(CLIP_PATH).astype(np.float64)
brain_raw  = np.load(BRAIN_PATH).astype(np.float64)   # (5, 2196, 768)
brain_mean = brain_raw.mean(axis=0)                    # (2196, 768)

meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

# 1~9 Likert scale, NaN=0, n=2196
arousal   = meta['arousal_score'].values.astype(np.float64)
valence   = meta['valence_score'].values.astype(np.float64)
dominance = meta['dominance_score'].values.astype(np.float64)
avd       = np.stack([arousal, valence, dominance], axis=1)  # (2196, 3)

# 0~1 정규화 버전도 저장
arousal_n   = meta['arousal_all_mean'].values.astype(np.float64)
valence_n   = meta['valence_all_mean'].values.astype(np.float64)
dominance_n = meta['dominance_all_mean'].values.astype(np.float64)
avd_norm    = np.stack([arousal_n, valence_n, dominance_n], axis=1)  # (2196, 3)

# Script 10 결과
pred_data = np.load(PRED_PATH)
r2_vjepa  = pred_data['r2_vjepa_per_dim']
r2_clip   = pred_data['r2_clip_per_dim']

print(f"  vjepa={vjepa.shape}, clip={clip_emb.shape}, brain_mean={brain_mean.shape}")
print(f"  avd={avd.shape}, range: A=[{arousal.min():.1f},{arousal.max():.1f}] "
      f"V=[{valence.min():.1f},{valence.max():.1f}] D=[{dominance.min():.1f},{dominance.max():.1f}]")
print(f"  NaN check: {np.isnan(avd).sum()} NaNs in AVD")

# ── BH FDR correction ─────────────────────────────────────────────────────────
def fdr_correct(pval_mat):
    shape = pval_mat.shape
    flat  = pval_mat.flatten()
    n     = len(flat)
    order = np.argsort(flat)
    adj   = flat[order] * n / (np.arange(1, n + 1))
    for i in range(n - 2, -1, -1):
        adj[i] = min(adj[i], adj[i + 1])
    adj = np.clip(adj, 0, 1)
    result = np.empty(n)
    result[order] = adj
    return result.reshape(shape)

# ── Part A: PCA + Spearman r (PC × A/V/D) ────────────────────────────────────
print("\nFitting PCA (100 components)...")
vjepa_pca = PCA(n_components=N_PC, random_state=42)
vjepa_pcs = vjepa_pca.fit_transform(vjepa)

clip_pca  = PCA(n_components=N_PC, random_state=42)
clip_pcs  = clip_pca.fit_transform(clip_emb)

print("Computing Spearman r: PC × A/V/D...")
def compute_corr(pcs, targets, label):
    n_pc, n_t = pcs.shape[1], targets.shape[1]
    corr = np.zeros((n_pc, n_t))
    pval = np.zeros((n_pc, n_t))
    for i in range(n_pc):
        for j in range(n_t):
            r, p = spearmanr(pcs[:, i], targets[:, j])
            corr[i, j] = r
            pval[i, j] = p
        if (i + 1) % 20 == 0:
            print(f"  {label} PC {i+1}/{n_pc}")
    return corr, pval

corr_vjepa_avd, pval_vjepa_avd = compute_corr(vjepa_pcs, avd, "V-JEPA2")
corr_clip_avd,  pval_clip_avd  = compute_corr(clip_pcs,  avd, "CLIP")

pval_vjepa_avd_fdr = fdr_correct(pval_vjepa_avd)
pval_clip_avd_fdr  = fdr_correct(pval_clip_avd)

# ── Part B: Brain → A/V/D direct Ridge CV prediction ─────────────────────────
print("\nComputing brain → A/V/D Ridge CV R²...")
pipe = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

r2_brain_avd = np.zeros(3)
for j, name in enumerate(AVD_LABELS):
    scores = cross_val_score(pipe, brain_mean, avd[:, j], cv=CV, scoring='r2')
    r2_brain_avd[j] = max(scores.mean(), 0)
    print(f"  brain → {name}: R²={r2_brain_avd[j]:.4f} (raw mean={scores.mean():.4f})")

# 비교: vjepa/clip k=27 → A/V/D
print("\nComputing V-JEPA2/CLIP k=27 → A/V/D Ridge CV R²...")
r2_vjepa_avd_k27 = np.zeros(3)
r2_clip_avd_k27  = np.zeros(3)
vjepa_k27 = PCA(n_components=27, random_state=42).fit_transform(vjepa)
clip_k27  = PCA(n_components=27, random_state=42).fit_transform(clip_emb)
for j, name in enumerate(AVD_LABELS):
    r2_vjepa_avd_k27[j] = max(cross_val_score(pipe, vjepa_k27, avd[:, j], cv=CV, scoring='r2').mean(), 0)
    r2_clip_avd_k27[j]  = max(cross_val_score(pipe, clip_k27,  avd[:, j], cv=CV, scoring='r2').mean(), 0)
    print(f"  vjepa k=27 → {name}: R²={r2_vjepa_avd_k27[j]:.4f}  clip k=27: R²={r2_clip_avd_k27[j]:.4f}")

# ── Part C: Brain-pred vs unpred PC × A/V/D 비교 ─────────────────────────────
pred_v = r2_vjepa > R2_THRESH
pred_c = r2_clip  > R2_THRESH

print(f"\nBrain-pred PCs: V-JEPA2 n={pred_v.sum()}, CLIP n={pred_c.sum()}")

print("\n=== V-JEPA2: brain-pred PCs × A/V/D ===")
for i in range(N_PC):
    if r2_vjepa[i] > R2_THRESH:
        avd_str = "  ".join([f"{AVD_LABELS[j]}={corr_vjepa_avd[i,j]:+.4f}(q={pval_vjepa_avd_fdr[i,j]:.2e})"
                              for j in range(3)])
        print(f"  PC{i+1} (R²={r2_vjepa[i]:.4f}): {avd_str}")

print("\n=== CLIP: brain-pred PCs × A/V/D ===")
for i in range(N_PC):
    if r2_clip[i] > R2_THRESH:
        avd_str = "  ".join([f"{AVD_LABELS[j]}={corr_clip_avd[i,j]:+.4f}(q={pval_clip_avd_fdr[i,j]:.2e})"
                              for j in range(3)])
        print(f"  PC{i+1} (R²={r2_clip[i]:.4f}): {avd_str}")

# mean max|r| comparison
print("\n=== Brain-pred vs Unpred: mean max|r|(AVD) ===")
for name, r2, corr, pred_mask in [
    ('V-JEPA2', r2_vjepa, corr_vjepa_avd, pred_v),
    ('CLIP',    r2_clip,  corr_clip_avd,  pred_c),
]:
    max_r_all  = np.max(np.abs(corr), axis=1)   # (100,)
    pred_mean   = max_r_all[pred_mask].mean()
    unpred_mean = max_r_all[~pred_mask].mean()
    print(f"  {name}: pred={pred_mean:.4f} (n={pred_mask.sum()}), unpred={unpred_mean:.4f}, Δ={pred_mean-unpred_mean:+.4f}")
    for j, lbl in enumerate(AVD_LABELS):
        pred_r   = np.max(np.abs(corr[pred_mask,  j])) if pred_mask.sum() > 0 else 0
        unpred_r = np.max(np.abs(corr[~pred_mask, j]))
        print(f"    {lbl}: pred max|r|={pred_r:.4f}  unpred max|r|={unpred_r:.4f}")

# ── Part D: k-sweep — model PCA k → A/V/D R² ─────────────────────────────────
print("\nComputing k-sweep: model PCA k → A/V/D R²...")

def k_sweep_avd(emb, k_values, label):
    results = np.zeros((len(k_values), 3))
    for ki, k in enumerate(k_values):
        pcs = PCA(n_components=k, random_state=42).fit_transform(emb)
        for j in range(3):
            r2 = cross_val_score(pipe, pcs, avd[:, j], cv=CV, scoring='r2').mean()
            results[ki, j] = max(r2, 0)
        print(f"  {label} k={k}: A={results[ki,0]:.4f} V={results[ki,1]:.4f} D={results[ki,2]:.4f}")
    return results

r2_vjepa_k_avd = k_sweep_avd(vjepa,    K_VALUES, "V-JEPA2")
r2_clip_k_avd  = k_sweep_avd(clip_emb, K_VALUES, "CLIP")

# brain k-sweep for AVD
print("\nComputing brain k-sweep: brain PCA k → A/V/D R²...")
r2_brain_k_avd = np.zeros((len(K_VALUES), 3))
for ki, k in enumerate(K_VALUES):
    pcs = PCA(n_components=k, random_state=42).fit_transform(brain_mean)
    for j in range(3):
        r2 = cross_val_score(pipe, pcs, avd[:, j], cv=CV, scoring='r2').mean()
        r2_brain_k_avd[ki, j] = max(r2, 0)
    print(f"  Brain k={k}: A={r2_brain_k_avd[ki,0]:.4f} V={r2_brain_k_avd[ki,1]:.4f} D={r2_brain_k_avd[ki,2]:.4f}")

# ── Figure 1: Full PC × A/V/D heatmap (100 PCs) ──────────────────────────────
print("\nGenerating Figure 1: Full PC × A/V/D heatmap...")
fig, axes = plt.subplots(1, 2, figsize=(10, 20))
fig.patch.set_facecolor('white')

k27_idx = K_VALUES.index(27)

for ax, name, corr, pval_fdr, r2, pca_obj, pred_mask in [
    (axes[0], 'V-JEPA2', corr_vjepa_avd, pval_vjepa_avd_fdr, r2_vjepa, vjepa_pca, pred_v),
    (axes[1], 'CLIP',    corr_clip_avd,  pval_clip_avd_fdr,  r2_clip,  clip_pca,  pred_c),
]:
    var_pct = pca_obj.explained_variance_ratio_ * 100
    ylabels = [
        f"{'*' if pred_mask[i] else ' '}PC{i+1:3d}(R²={r2[i]:.3f},v={var_pct[i]:.1f}%)"
        for i in range(N_PC)
    ]
    im = ax.imshow(corr, aspect='auto', cmap='RdBu_r', vmin=-0.6, vmax=0.6,
                   interpolation='nearest')
    plt.colorbar(im, ax=ax, label='Spearman r', shrink=0.4)
    # FDR-sig marker
    for i in range(N_PC):
        for j in range(3):
            if pval_fdr[i, j] < 0.05:
                ax.plot(j, i, 'k.', markersize=3)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(AVD_LABELS, fontsize=10)
    ax.set_yticks(np.arange(N_PC))
    ax.set_yticklabels(ylabels, fontsize=5)
    ax.set_title(f'{name}\nPC × A/V/D Spearman r\n(*=brain-pred, ·=FDR q<0.05)',
                 fontsize=11, fontweight='bold')

plt.tight_layout()
path = FIG_DIR / "dim_pc_avd_heatmap.png"
plt.savefig(path, dpi=200, bbox_inches='tight')
print(f"  Saved: {path}")
plt.close()

# ── Figure 2: Brain-pred vs unpred × A/V/D ───────────────────────────────────
print("Generating Figure 2: brain-pred vs unpred × A/V/D...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.patch.set_facecolor('white')

for col, (name, r2, corr, pred_mask) in enumerate([
    ('V-JEPA2', r2_vjepa, corr_vjepa_avd, pred_v),
    ('CLIP',    r2_clip,  corr_clip_avd,  pred_c),
]):
    # Top: bar chart — max|r| per A/V/D dimension
    ax = axes[0, col]
    pred_maxr   = np.max(np.abs(corr[pred_mask,  :]), axis=0) if pred_mask.sum() > 0 else np.zeros(3)
    unpred_maxr = np.max(np.abs(corr[~pred_mask, :]), axis=0)
    x = np.arange(3)
    ax.bar(x - 0.2, pred_maxr,   0.38,
           label=f'Brain-predictable (n={pred_mask.sum()})',   color='steelblue',  alpha=0.85)
    ax.bar(x + 0.2, unpred_maxr, 0.38,
           label=f'Brain-unpredictable (n={(~pred_mask).sum()})', color='lightcoral', alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(AVD_LABELS, fontsize=11)
    ax.set_ylabel('Max |Spearman r|', fontsize=10)
    ax.set_ylim(0, 0.7)
    ax.set_title(f'{name}: Brain-pred vs Unpred × A/V/D', fontsize=11, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)
    for xi, (pv, uv) in enumerate(zip(pred_maxr, unpred_maxr)):
        ax.text(xi - 0.2, pv + 0.01, f'{pv:.3f}', ha='center', va='bottom', fontsize=8, color='steelblue')
        ax.text(xi + 0.2, uv + 0.01, f'{uv:.3f}', ha='center', va='bottom', fontsize=8, color='lightcoral')

    # Bottom: scatter — R²(brain) vs |r|(A/V/D) per PC
    ax = axes[1, col]
    colors_avd = ['#e74c3c', '#2ecc71', '#3498db']
    for j, (lbl, color) in enumerate(zip(AVD_LABELS, colors_avd)):
        ax.scatter(r2, np.abs(corr[:, j]), alpha=0.4, s=20, color=color, label=lbl)
    # highlight brain-pred PCs
    for i in range(N_PC):
        if r2[i] > R2_THRESH:
            ax.scatter(r2[i], np.max(np.abs(corr[i, :])), s=100, color='black',
                       zorder=5, marker='*')
            ax.annotate(f'PC{i+1}', (r2[i], np.max(np.abs(corr[i, :]))),
                        textcoords='offset points', xytext=(5, 3), fontsize=8, color='black')
    ax.axvline(R2_THRESH, color='gray', linestyle=':', alpha=0.6)
    ax.set_xlabel('R² (brain → PC)', fontsize=10)
    ax.set_ylabel('|Spearman r| with A/V/D', fontsize=10)
    ax.set_title(f'{name}: Brain decodability vs A/V/D correlation\n(★=brain-pred PC)', fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

plt.suptitle('Brain-predictable PCs: A/V/D encoding', fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
path = FIG_DIR / "dim_brain_pred_avd.png"
plt.savefig(path, dpi=200, bbox_inches='tight')
print(f"  Saved: {path}")
plt.close()

# ── Figure 3: Brain → A/V/D direct R² (vs model R²) ─────────────────────────
print("Generating Figure 3: Brain → A/V/D direct prediction R²...")
fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor('white')

x = np.arange(3)
w = 0.25
ax.bar(x - w,   r2_brain_avd,      w, label='Brain (full 768-dim)',   color='#9b59b6', alpha=0.85)
ax.bar(x,       r2_vjepa_avd_k27,  w, label='V-JEPA2 (k=27)',         color='#e67e22', alpha=0.85)
ax.bar(x + w,   r2_clip_avd_k27,   w, label='CLIP (k=27)',            color='#1abc9c', alpha=0.85)

for xi in range(3):
    ax.text(xi - w,   r2_brain_avd[xi] + 0.003,     f'{r2_brain_avd[xi]:.3f}',     ha='center', fontsize=8)
    ax.text(xi,       r2_vjepa_avd_k27[xi] + 0.003, f'{r2_vjepa_avd_k27[xi]:.3f}', ha='center', fontsize=8)
    ax.text(xi + w,   r2_clip_avd_k27[xi] + 0.003,  f'{r2_clip_avd_k27[xi]:.3f}',  ha='center', fontsize=8)

ax.set_xticks(x)
ax.set_xticklabels(AVD_LABELS, fontsize=12)
ax.set_ylabel('R² (5-fold CV Ridge)', fontsize=11)
ax.set_title('Predicting Dimensional Emotion from Brain / Video Models\n(Ridge CV, k=27 for models)',
             fontsize=12, fontweight='bold')
ax.legend(fontsize=10)
ax.set_ylim(0, max(r2_brain_avd.max(), r2_vjepa_avd_k27.max(), r2_clip_avd_k27.max()) * 1.2 + 0.05)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
path = FIG_DIR / "dim_brain_avd_prediction.png"
plt.savefig(path, dpi=200, bbox_inches='tight')
print(f"  Saved: {path}")
plt.close()

# ── Figure 4: k-sweep — model/brain PCA k → A/V/D R² ─────────────────────────
print("Generating Figure 4: k-sweep A/V/D R²...")
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.patch.set_facecolor('white')
colors_model = {'V-JEPA2': '#e67e22', 'CLIP': '#1abc9c', 'Brain': '#9b59b6'}
k_arr = np.array(K_VALUES)
k27_idx = list(K_VALUES).index(27)

for j, dim_name in enumerate(AVD_LABELS):
    ax = axes[j]
    ax.plot(k_arr, r2_vjepa_k_avd[:, j],  'o-', color=colors_model['V-JEPA2'], label='V-JEPA2', linewidth=2)
    ax.plot(k_arr, r2_clip_k_avd[:, j],   's-', color=colors_model['CLIP'],    label='CLIP',    linewidth=2)
    ax.plot(k_arr, r2_brain_k_avd[:, j],  '^-', color=colors_model['Brain'],   label='Brain',   linewidth=2)
    ax.axvline(27, color='gray', linestyle='--', alpha=0.6, label='k=27')
    # annotate k=27 values
    ax.annotate(f'{r2_vjepa_k_avd[k27_idx,j]:.3f}',
                (27, r2_vjepa_k_avd[k27_idx,j]), textcoords='offset points',
                xytext=(5,3), fontsize=8, color=colors_model['V-JEPA2'])
    ax.annotate(f'{r2_clip_k_avd[k27_idx,j]:.3f}',
                (27, r2_clip_k_avd[k27_idx,j]), textcoords='offset points',
                xytext=(5,-10), fontsize=8, color=colors_model['CLIP'])
    ax.annotate(f'{r2_brain_k_avd[k27_idx,j]:.3f}',
                (27, r2_brain_k_avd[k27_idx,j]), textcoords='offset points',
                xytext=(5,3), fontsize=8, color=colors_model['Brain'])
    ax.set_xlabel('k (PCA dimensions)', fontsize=11)
    ax.set_ylabel('R² (5-fold CV Ridge)', fontsize=11)
    ax.set_title(f'{dim_name} prediction vs k', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_xscale('log')

plt.suptitle('Predicting Arousal / Valence / Dominance from PCA-reduced Embeddings',
             fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
path = FIG_DIR / "dim_avd_k_sweep.png"
plt.savefig(path, dpi=200, bbox_inches='tight')
print(f"  Saved: {path}")
plt.close()

# ── Print summary table ───────────────────────────────────────────────────────
print("\n=== SUMMARY TABLE: k-sweep R² ===")
print(f"{'k':>5}  {'vjepa_A':>8} {'vjepa_V':>8} {'vjepa_D':>8}  {'clip_A':>8} {'clip_V':>8} {'clip_D':>8}  {'brain_A':>8} {'brain_V':>8} {'brain_D':>8}")
for ki, k in enumerate(K_VALUES):
    print(f"{k:>5}  "
          f"{r2_vjepa_k_avd[ki,0]:>8.4f} {r2_vjepa_k_avd[ki,1]:>8.4f} {r2_vjepa_k_avd[ki,2]:>8.4f}  "
          f"{r2_clip_k_avd[ki,0]:>8.4f} {r2_clip_k_avd[ki,1]:>8.4f} {r2_clip_k_avd[ki,2]:>8.4f}  "
          f"{r2_brain_k_avd[ki,0]:>8.4f} {r2_brain_k_avd[ki,1]:>8.4f} {r2_brain_k_avd[ki,2]:>8.4f}")

print(f"\nBrain (full): A={r2_brain_avd[0]:.4f}  V={r2_brain_avd[1]:.4f}  D={r2_brain_avd[2]:.4f}")

# ── Save ──────────────────────────────────────────────────────────────────────
np.savez(
    OUTPUT_DIR / "dimensional_emotion_results.npz",
    corr_vjepa_avd       = corr_vjepa_avd,       # (100, 3)
    pval_vjepa_avd       = pval_vjepa_avd,
    pval_vjepa_avd_fdr   = pval_vjepa_avd_fdr,
    corr_clip_avd        = corr_clip_avd,
    pval_clip_avd        = pval_clip_avd,
    pval_clip_avd_fdr    = pval_clip_avd_fdr,
    r2_brain_avd         = r2_brain_avd,          # (3,) brain full → A/V/D
    r2_vjepa_avd_k27     = r2_vjepa_avd_k27,      # (3,) vjepa k=27 → A/V/D
    r2_clip_avd_k27      = r2_clip_avd_k27,
    r2_vjepa_k_avd       = r2_vjepa_k_avd,        # (14, 3) k-sweep
    r2_clip_k_avd        = r2_clip_k_avd,
    r2_brain_k_avd       = r2_brain_k_avd,
    k_values             = np.array(K_VALUES),
    avd_labels           = np.array(AVD_LABELS),
    r2_vjepa_per_dim     = r2_vjepa,
    r2_clip_per_dim      = r2_clip,
    brain_pred_mask_vjepa = pred_v.astype(np.int8),
    brain_pred_mask_clip  = pred_c.astype(np.int8),
    vjepa_var_ratio      = vjepa_pca.explained_variance_ratio_,
    clip_var_ratio       = clip_pca.explained_variance_ratio_,
)
print(f"\nSaved: {OUTPUT_DIR}/dimensional_emotion_results.npz")
print("\nDone.")
