"""
CCN Analysis 11: Brain-Predictable PC × Emotion Correlation

목적:
  Script 10 (Exp 3)에서 brain이 V-JEPA2 PC1~3, CLIP PC1~5만 decode한다는 결과가 나왔다.
  이 PC들이 감정 관련 차원인지 확인 → paper의 main claim 결정.

  시나리오 A: brain-predictable PC ↔ high emotion correlation
    → "Brain selectively reads the affective subspace of video representations"
  시나리오 B: mixed
    → "Brain-model alignment captures both affective and perceptual dimensions"
  시나리오 C: brain-predictable PC ↔ low emotion correlation
    → "Brain-model alignment is driven by perceptual, not affective, structure"

Input:
  video_embeddings/vjepa2_embeddings.npy    (2196, 1408)
  video_embeddings/clip_embeddings.npy      (2196, 512)
  brain_embeddings/brain_jepa_embeddings.npy  (5, 2196, 768)
  metadata CSV
  CCN/results/brain_predictable_dims.npz    (Script 10 Exp 3 결과)

Output:
  CCN/results/pc_emotion_correlation.npz
  CCN/figures/pc_emotion_heatmap.png
  CCN/figures/pc_brain_pred_emotion.png
  CCN/figures/pc_r2_vs_emotion_scatter.png
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.decomposition import PCA
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

EMOTION_LABELS = [
    'Admiration', 'Adoration', 'Aesthetic appreciation', 'Amusement', 'Anger',
    'Anxiety', 'Awe', 'Awkwardness', 'Boredom', 'Calmness', 'Confusion',
    'Contempt', 'Craving', 'Disgust', 'Empathic pain', 'Entrancement',
    'Excitement', 'Fear', 'Horror', 'Interest', 'Joy', 'Nostalgia', 'Relief',
    'Romance', 'Sadness', 'Satisfaction', 'Sexual desire', 'Surprise',
    'Sympathy', 'Triumph', 'Uncomfortable', 'Annoyance', 'Envy', 'Guilt'
]
N_PC      = 100
R2_THRESH = 0.01    # brain-predictable threshold

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
vjepa      = np.load(VJEPA_PATH).astype(np.float64)
clip_emb   = np.load(CLIP_PATH).astype(np.float64)
brain_raw  = np.load(BRAIN_PATH).astype(np.float64)   # (5, 2196, 768)
brain_mean = brain_raw.mean(axis=0)                    # (2196, 768)

meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

score_cols = [f"score_{i}" for i in range(34)]
emotion_scores = meta[score_cols].values.astype(np.float64)   # (2196, 34)
arousal    = meta['arousal_score'].values.astype(np.float64)
valence    = meta['valence_score'].values.astype(np.float64)
dominance  = meta['dominance_score'].values.astype(np.float64)

# Script 10 Exp 3 결과 로드
pred_data = np.load(PRED_PATH)
r2_vjepa  = pred_data['r2_vjepa_per_dim']   # (100,)
r2_clip   = pred_data['r2_clip_per_dim']    # (100,)

print(f"  vjepa: {vjepa.shape}, clip: {clip_emb.shape}, brain_mean: {brain_mean.shape}")
print(f"  emotion_scores: {emotion_scores.shape}")
print(f"  r2_vjepa: {r2_vjepa[:5].round(4)}, r2_clip: {r2_clip[:5].round(4)}")

# ── Step 1: PCA ───────────────────────────────────────────────────────────────
print("\nFitting PCA (100 components)...")
vjepa_pca  = PCA(n_components=N_PC, random_state=42)
vjepa_pcs  = vjepa_pca.fit_transform(vjepa)    # (2196, 100)

clip_pca   = PCA(n_components=N_PC, random_state=42)
clip_pcs   = clip_pca.fit_transform(clip_emb)  # (2196, 100)

print(f"  V-JEPA2 explained var (top 10): {vjepa_pca.explained_variance_ratio_[:10].round(4)}")
print(f"  CLIP    explained var (top 10): {clip_pca.explained_variance_ratio_[:10].round(4)}")

# ── Step 2: Spearman r (PC × emotion + A/V/D) ────────────────────────────────
print("\nComputing Spearman correlations (PC × emotion)...")

def compute_corr_matrix(pcs, scores, n_pc=N_PC):
    """pcs: (N, n_pc), scores: (N, n_targets) → corr (n_pc, n_targets), pval (n_pc, n_targets)"""
    n_targets = scores.shape[1]
    corr = np.zeros((n_pc, n_targets))
    pval = np.zeros((n_pc, n_targets))
    for i in range(n_pc):
        for j in range(n_targets):
            r, p = spearmanr(pcs[:, i], scores[:, j])
            corr[i, j] = r
            pval[i, j] = p
        if (i + 1) % 10 == 0:
            print(f"    PC {i+1}/{n_pc} done")
    return corr, pval

print("  V-JEPA2 PC × 34 emotions...")
corr_vjepa_emo, pval_vjepa_emo = compute_corr_matrix(vjepa_pcs, emotion_scores)

print("  CLIP PC × 34 emotions...")
corr_clip_emo, pval_clip_emo = compute_corr_matrix(clip_pcs, emotion_scores)

# Arousal / Valence / Dominance
print("  PC × A/V/D...")
avd_scores = np.stack([arousal, valence, dominance], axis=1)  # (2196, 3)
corr_vjepa_avd, pval_vjepa_avd = compute_corr_matrix(vjepa_pcs, avd_scores)
corr_clip_avd, pval_clip_avd   = compute_corr_matrix(clip_pcs,  avd_scores)
avd_labels = ['Arousal', 'Valence', 'Dominance']

# ── Step 3: FDR correction ────────────────────────────────────────────────────
print("\nApplying FDR correction (Benjamini-Hochberg)...")

def fdr_correct(pval_mat):
    """Benjamini-Hochberg FDR correction (scipy-only implementation)."""
    shape = pval_mat.shape
    flat  = pval_mat.flatten()
    n     = len(flat)
    order = np.argsort(flat)
    ranked_pvals = flat[order]
    # BH adjusted p-values: p_adj[i] = p[i] * n / rank(i)
    adjusted = ranked_pvals * n / (np.arange(1, n + 1))
    # Enforce monotonicity from the right
    for i in range(n - 2, -1, -1):
        adjusted[i] = min(adjusted[i], adjusted[i + 1])
    adjusted = np.clip(adjusted, 0, 1)
    result = np.empty(n)
    result[order] = adjusted
    return result.reshape(shape)

pval_vjepa_emo_fdr = fdr_correct(pval_vjepa_emo)
pval_clip_emo_fdr  = fdr_correct(pval_clip_emo)
pval_vjepa_avd_fdr = fdr_correct(pval_vjepa_avd)
pval_clip_avd_fdr  = fdr_correct(pval_clip_avd)

# ── Step 4: Brain-predictable mask ───────────────────────────────────────────
brain_pred_vjepa   = r2_vjepa > R2_THRESH
brain_unpred_vjepa = ~brain_pred_vjepa
brain_pred_clip    = r2_clip  > R2_THRESH
brain_unpred_clip  = ~brain_pred_clip

print(f"\nBrain-predictable PCs (R² > {R2_THRESH}):")
print(f"  V-JEPA2: {np.where(brain_pred_vjepa)[0] + 1} (n={brain_pred_vjepa.sum()})")
print(f"  CLIP:    {np.where(brain_pred_clip)[0] + 1} (n={brain_pred_clip.sum()})")

# ── Step 5: Print summary ─────────────────────────────────────────────────────
print("\n=== V-JEPA2: Brain-predictable PCs ===")
for i in range(N_PC):
    if r2_vjepa[i] > R2_THRESH:
        top3_idx = np.argsort(np.abs(corr_vjepa_emo[i]))[-3:][::-1]
        top3     = [(EMOTION_LABELS[j], f"{corr_vjepa_emo[i,j]:+.3f}") for j in top3_idx]
        sig_mask = pval_vjepa_emo_fdr[i] < 0.05
        sig_emos = [EMOTION_LABELS[j] for j in range(34) if sig_mask[j]]
        var_exp  = vjepa_pca.explained_variance_ratio_[i] * 100
        print(f"  PC{i+1} (R²={r2_vjepa[i]:.4f}, var={var_exp:.1f}%): "
              f"top3 = {top3}, FDR-sig n={sig_mask.sum()} emotions")
        if sig_emos:
            print(f"    FDR-sig emotions: {sig_emos}")
        # AVD
        avd_str = [f"{avd_labels[k]}={corr_vjepa_avd[i,k]:+.3f}" for k in range(3)]
        print(f"    A/V/D: {', '.join(avd_str)}")

print("\n=== CLIP: Brain-predictable PCs ===")
for i in range(N_PC):
    if r2_clip[i] > R2_THRESH:
        top3_idx = np.argsort(np.abs(corr_clip_emo[i]))[-3:][::-1]
        top3     = [(EMOTION_LABELS[j], f"{corr_clip_emo[i,j]:+.3f}") for j in top3_idx]
        sig_mask = pval_clip_emo_fdr[i] < 0.05
        sig_emos = [EMOTION_LABELS[j] for j in range(34) if sig_mask[j]]
        var_exp  = clip_pca.explained_variance_ratio_[i] * 100
        print(f"  PC{i+1} (R²={r2_clip[i]:.4f}, var={var_exp:.1f}%): "
              f"top3 = {top3}, FDR-sig n={sig_mask.sum()} emotions")
        if sig_emos:
            print(f"    FDR-sig emotions: {sig_emos}")
        avd_str = [f"{avd_labels[k]}={corr_clip_avd[i,k]:+.3f}" for k in range(3)]
        print(f"    A/V/D: {', '.join(avd_str)}")

# max |r| comparison: brain-pred vs unpred
for model_name, r2, corr, pred_mask, unpred_mask in [
    ('V-JEPA2', r2_vjepa, corr_vjepa_emo, brain_pred_vjepa, brain_unpred_vjepa),
    ('CLIP',    r2_clip,  corr_clip_emo,  brain_pred_clip,  brain_unpred_clip),
]:
    max_corr_pred   = np.max(np.abs(corr[pred_mask,   :]), axis=0) if pred_mask.sum() > 0 else np.zeros(34)
    max_corr_unpred = np.max(np.abs(corr[unpred_mask, :]), axis=0) if unpred_mask.sum() > 0 else np.zeros(34)
    print(f"\n{model_name} — mean max|r| brain-predictable PCs: {max_corr_pred.mean():.4f}")
    print(f"{model_name} — mean max|r| brain-unpredictable PCs: {max_corr_unpred.mean():.4f}")
    diff = max_corr_pred.mean() - max_corr_unpred.mean()
    print(f"  Δ = {diff:+.4f} ({'pred > unpred' if diff > 0 else 'pred < unpred'})")

# ── Figure A: Heatmap (top 20 PCs × 34 emotions, annotated by R²) ─────────────
print("\nGenerating Figure A: Heatmap...")
N_SHOW = 20  # 상위 20 PC

fig, axes = plt.subplots(2, 1, figsize=(22, 14))
fig.patch.set_facecolor('white')

for ax, name, corr, pval_fdr, r2, pca_obj, pred_mask in [
    (axes[0], 'V-JEPA2', corr_vjepa_emo, pval_vjepa_emo_fdr, r2_vjepa, vjepa_pca, brain_pred_vjepa),
    (axes[1], 'CLIP',    corr_clip_emo,  pval_clip_emo_fdr,  r2_clip,  clip_pca,  brain_pred_clip),
]:
    var_pct = pca_obj.explained_variance_ratio_[:N_SHOW] * 100
    ylabels = [
        f"{'*' if pred_mask[i] else ' '}PC{i+1} (R2={r2[i]:.3f}, var={var_pct[i]:.1f}%)"
        for i in range(N_SHOW)
    ]
    data = corr[:N_SHOW, :]
    im = ax.imshow(data, aspect='auto', cmap='RdBu_r', vmin=-0.4, vmax=0.4,
                   interpolation='nearest')
    plt.colorbar(im, ax=ax, label='Spearman r', shrink=0.8)
    # FDR-significant cells: white dot
    for i in range(N_SHOW):
        for j in range(34):
            if pval_fdr[i, j] < 0.05:
                ax.plot(j, i, 'k.', markersize=3)
    ax.set_xticks(np.arange(34))
    ax.set_xticklabels(EMOTION_LABELS, rotation=90, fontsize=7)
    ax.set_yticks(np.arange(N_SHOW))
    ax.set_yticklabels(ylabels, fontsize=7)
    ax.set_title(f'{name}: PC x Emotion Spearman r  (* = brain-predictable, dot = FDR q<0.05)',
                 fontsize=12, fontweight='bold')
    ax.set_xlabel('Emotion', fontsize=10)
    ax.set_ylabel('PC', fontsize=10)

plt.tight_layout()
fig_a_path = FIG_DIR / "pc_emotion_heatmap.png"
plt.savefig(fig_a_path, dpi=200, bbox_inches='tight')
print(f"  Saved: {fig_a_path}")
plt.close()

# ── Figure B: Brain-pred vs unpred max |r| bar chart ──────────────────────────
print("Generating Figure B: Brain-pred vs unpred emotion correlation...")
fig, axes = plt.subplots(1, 2, figsize=(20, 6))
fig.patch.set_facecolor('white')

for ax, model_name, r2, corr, pred_mask, unpred_mask in [
    (axes[0], 'V-JEPA2', r2_vjepa, corr_vjepa_emo, brain_pred_vjepa, brain_unpred_vjepa),
    (axes[1], 'CLIP',    r2_clip,  corr_clip_emo,  brain_pred_clip,  brain_unpred_clip),
]:
    max_pred   = np.max(np.abs(corr[pred_mask,   :]), axis=0) if pred_mask.sum() > 0 else np.zeros(34)
    max_unpred = np.max(np.abs(corr[unpred_mask, :]), axis=0) if unpred_mask.sum() > 0 else np.zeros(34)

    x = np.arange(34)
    w = 0.38
    bars1 = ax.bar(x - w/2, max_pred,   w, label=f'Brain-predictable (n={pred_mask.sum()})',
                   color='steelblue', alpha=0.85)
    bars2 = ax.bar(x + w/2, max_unpred, w, label=f'Brain-unpredictable (n={unpred_mask.sum()})',
                   color='lightcoral', alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(EMOTION_LABELS, rotation=90, fontsize=7)
    ax.set_ylabel('Max |Spearman r| with emotion', fontsize=10)
    ax.set_title(
        f'{model_name}: Brain-predictable vs Unpredictable PCs × Emotion\n'
        f'Mean pred={max_pred.mean():.3f}, unpred={max_unpred.mean():.3f}  '
        f'(Δ={max_pred.mean()-max_unpred.mean():+.3f})',
        fontsize=11, fontweight='bold'
    )
    ax.axhline(max_pred.mean(),   color='steelblue',  linestyle='--', alpha=0.5, linewidth=1)
    ax.axhline(max_unpred.mean(), color='lightcoral', linestyle='--', alpha=0.5, linewidth=1)
    ax.legend(fontsize=9)
    ax.set_ylim(0, 0.7)
    ax.grid(axis='y', alpha=0.3)

plt.suptitle('Brain-predictable PCs: Do they encode emotion?', fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
fig_b_path = FIG_DIR / "pc_brain_pred_emotion.png"
plt.savefig(fig_b_path, dpi=200, bbox_inches='tight')
print(f"  Saved: {fig_b_path}")
plt.close()

# ── Figure C: Scatter — R²(brain) vs max emotion |r| ─────────────────────────
print("Generating Figure C: R²(brain) vs max emotion correlation scatter...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor('white')

for ax, name, r2, corr, pca_obj in [
    (axes[0], 'V-JEPA2', r2_vjepa, corr_vjepa_emo, vjepa_pca),
    (axes[1], 'CLIP',    r2_clip,  corr_clip_emo,  clip_pca),
]:
    max_emo_corr = np.max(np.abs(corr), axis=1)   # (100,) 각 PC의 최대 감정 상관
    var_pct      = pca_obj.explained_variance_ratio_ * 100
    sizes        = (var_pct / var_pct.max()) * 200 + 20

    sc = ax.scatter(r2, max_emo_corr, c=var_pct, cmap='viridis', s=sizes, alpha=0.7)
    plt.colorbar(sc, ax=ax, label='Explained variance (%)')

    # Label brain-predictable PCs
    for i in range(N_PC):
        if r2[i] > R2_THRESH:
            ax.annotate(
                f'PC{i+1}',
                (r2[i], max_emo_corr[i]),
                textcoords='offset points', xytext=(5, 3),
                fontsize=9, color='red', fontweight='bold'
            )

    # Regression line (all PCs)
    from numpy.polynomial.polynomial import polyfit
    if r2.std() > 0:
        c0, c1 = polyfit(r2, max_emo_corr, 1)
        xline = np.linspace(r2.min(), r2.max(), 100)
        ax.plot(xline, c0 + c1 * xline, 'r--', alpha=0.5, linewidth=1.2, label='trend')

    ax.axvline(R2_THRESH, color='gray', linestyle=':', alpha=0.6, label=f'R²={R2_THRESH} threshold')
    ax.set_xlabel('R² (brain → PC)', fontsize=11)
    ax.set_ylabel('Max |Spearman r| with any emotion', fontsize=11)
    ax.set_title(f'{name}: Brain decodability vs Emotion correlation\n(dot size ∝ explained variance)',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

plt.tight_layout()
fig_c_path = FIG_DIR / "pc_r2_vs_emotion_scatter.png"
plt.savefig(fig_c_path, dpi=200, bbox_inches='tight')
print(f"  Saved: {fig_c_path}")
plt.close()

# ── Figure D: AVD heatmap (top 20 PCs × Arousal/Valence/Dominance) ───────────
print("Generating Figure D: AVD heatmap...")
fig, axes = plt.subplots(1, 2, figsize=(10, 10))
fig.patch.set_facecolor('white')

for ax, name, corr_avd, pval_avd_fdr, r2, pca_obj, pred_mask in [
    (axes[0], 'V-JEPA2', corr_vjepa_avd, pval_vjepa_avd_fdr, r2_vjepa, vjepa_pca, brain_pred_vjepa),
    (axes[1], 'CLIP',    corr_clip_avd,  pval_clip_avd_fdr,  r2_clip,  clip_pca,  brain_pred_clip),
]:
    var_pct = pca_obj.explained_variance_ratio_[:N_SHOW] * 100
    ylabels = [
        f"{'*' if pred_mask[i] else ' '}PC{i+1} (R2={r2[i]:.3f})"
        for i in range(N_SHOW)
    ]
    data = corr_avd[:N_SHOW, :]
    im = ax.imshow(data, aspect='auto', cmap='RdBu_r', vmin=-0.6, vmax=0.6,
                   interpolation='nearest')
    plt.colorbar(im, ax=ax, label='Spearman r', shrink=0.5)
    # Annotate cell values and FDR significance
    for i in range(N_SHOW):
        for j in range(3):
            sig = '*' if pval_avd_fdr[i, j] < 0.05 else ''
            ax.text(j, i, f"{data[i,j]:.2f}{sig}", ha='center', va='center',
                    fontsize=7, color='black')
    ax.set_xticks(np.arange(3))
    ax.set_xticklabels(avd_labels, fontsize=9)
    ax.set_yticks(np.arange(N_SHOW))
    ax.set_yticklabels(ylabels, fontsize=7)
    ax.set_title(f'{name}: PC x A/V/D (*=brain-pred, cell*=FDR q<0.05)', fontsize=11, fontweight='bold')

plt.tight_layout()
fig_d_path = FIG_DIR / "pc_avd_heatmap.png"
plt.savefig(fig_d_path, dpi=200, bbox_inches='tight')
print(f"  Saved: {fig_d_path}")
plt.close()

# ── Save results ──────────────────────────────────────────────────────────────
np.savez(
    OUTPUT_DIR / "pc_emotion_correlation.npz",
    corr_vjepa_emo    = corr_vjepa_emo,        # (100, 34)
    pval_vjepa_emo    = pval_vjepa_emo,
    pval_vjepa_emo_fdr= pval_vjepa_emo_fdr,
    corr_clip_emo     = corr_clip_emo,
    pval_clip_emo     = pval_clip_emo,
    pval_clip_emo_fdr = pval_clip_emo_fdr,
    corr_vjepa_avd    = corr_vjepa_avd,        # (100, 3)
    pval_vjepa_avd_fdr= pval_vjepa_avd_fdr,
    corr_clip_avd     = corr_clip_avd,
    pval_clip_avd_fdr = pval_clip_avd_fdr,
    emotion_labels    = np.array(EMOTION_LABELS),
    avd_labels        = np.array(avd_labels),
    r2_vjepa          = r2_vjepa,
    r2_clip           = r2_clip,
    brain_pred_mask_vjepa = brain_pred_vjepa.astype(np.int8),
    brain_pred_mask_clip  = brain_pred_clip.astype(np.int8),
    vjepa_var_ratio   = vjepa_pca.explained_variance_ratio_,
    clip_var_ratio    = clip_pca.explained_variance_ratio_,
)
print(f"\nSaved: {OUTPUT_DIR}/pc_emotion_correlation.npz")
print("\nDone.")
