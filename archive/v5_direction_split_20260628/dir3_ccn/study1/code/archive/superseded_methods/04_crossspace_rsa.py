"""
CCN Analysis 04: Cross-space RSA — Per-emotion alignment between Brain-JEPA and models

For each emotion i:
    E_i[j,k] = score_i[j] * score_i[k]   (rank-1 emotion kernel)

    rsa_brain_i  = Spearman(rsm_brain_mean, E_i)
    rsa_vjepa_i  = Spearman(rsm_vjepa2,     E_i)
    rsa_clip_i   = Spearman(rsm_clip,        E_i)

    alignment_i  = min(rsa_brain_i, rsa_vjepa_i)     both encode emotion i
    divergence_i = |rsa_brain_i - rsa_vjepa_i|        how much they differ

Divergence → Brain Tuning target emotions

Input:
    cka_results/rsm_brain.npy    (2196, 2196)  Brain-JEPA mean RSM (already exists)
    cka_results/rsm_vjepa2.npy
    cka_results/rsm_clip.npy
    metadata CSV

Output:
    CCN/results/crossspace_rsa_results.npz
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import spearmanr
import time

# ── Paths ─────────────────────────────────────────────────────────────────────
BRAIN_RSM_PATH  = Path("/pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_brain.npy")
VJEPA2_RSM_PATH = Path("/pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_vjepa2.npy")
CLIP_RSM_PATH   = Path("/pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_clip.npy")
META_PATH       = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
OUTPUT_DIR      = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results")

EMOTION_LABELS = [
    'Admiration','Adoration','Aesthetic appreciation','Amusement','Anger','Anxiety',
    'Awe','Awkwardness','Boredom','Calmness','Confusion','Contempt','Craving',
    'Disgust','Empathic pain','Entrancement','Excitement','Fear','Horror','Interest',
    'Joy','Nostalgia','Relief','Romance','Sadness','Satisfaction','Sexual desire',
    'Surprise','Sympathy','Triumph','Uncomfortable','Annoyance','Envy','Guilt'
]
N_EMO = 34
N     = 2196

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading RSMs...")
rsm_brain  = np.load(BRAIN_RSM_PATH).astype(np.float64)
rsm_vjepa2 = np.load(VJEPA2_RSM_PATH).astype(np.float64)
rsm_clip   = np.load(CLIP_RSM_PATH).astype(np.float64)

meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

# Upper triangle (shared)
idx_upper  = np.triu_indices(N, k=1)
brain_tri  = rsm_brain[idx_upper]
vjepa2_tri = rsm_vjepa2[idx_upper]
clip_tri   = rsm_clip[idx_upper]
print(f"  Upper triangle pairs: {len(brain_tri):,}")

# ── Per-emotion RSA ───────────────────────────────────────────────────────────
print(f"\n{'='*75}")
print("PER-EMOTION CROSS-SPACE RSA  (Spearman r)")
print(f"{'='*75}")
print(f"{'#':>3}  {'Emotion':<28}  {'Brain':>7}  {'V-JEPA2':>8}  {'CLIP':>7}  {'Align':>7}  {'Diverg':>7}")

rsa_brain  = np.zeros(N_EMO)
rsa_vjepa2 = np.zeros(N_EMO)
rsa_clip   = np.zeros(N_EMO)
alignment  = np.zeros(N_EMO)
divergence = np.zeros(N_EMO)

t_total = time.time()

for i in range(N_EMO):
    t0 = time.time()
    score_i = meta[f"score_{i}"].values.astype(np.float64)
    E_i_tri = np.outer(score_i, score_i)[idx_upper]

    rsa_brain[i]  = spearmanr(brain_tri,  E_i_tri).statistic
    rsa_vjepa2[i] = spearmanr(vjepa2_tri, E_i_tri).statistic
    rsa_clip[i]   = spearmanr(clip_tri,   E_i_tri).statistic

    alignment[i]  = min(rsa_brain[i], rsa_vjepa2[i])
    divergence[i] = abs(rsa_brain[i] - rsa_vjepa2[i])

    print(f"[{i:2d}] {EMOTION_LABELS[i]:<28}  "
          f"{rsa_brain[i]:>7.4f}  {rsa_vjepa2[i]:>8.4f}  {rsa_clip[i]:>7.4f}  "
          f"{alignment[i]:>7.4f}  {divergence[i]:>7.4f}  [{time.time()-t0:.0f}s]")

print(f"\nTotal: {(time.time()-t_total)/60:.1f} min")

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'='*75}")
print("SUMMARY")
print(f"{'='*75}")

print(f"\nMean RSA across 34 emotions:")
print(f"  Brain-JEPA: {rsa_brain.mean():.4f} ± {rsa_brain.std():.4f}")
print(f"  V-JEPA2:    {rsa_vjepa2.mean():.4f} ± {rsa_vjepa2.std():.4f}")
print(f"  CLIP:       {rsa_clip.mean():.4f} ± {rsa_clip.std():.4f}")

print(f"\nTop 5 CONVERGENT emotions (alignment = min(Brain, V-JEPA2) highest):")
for idx_e in np.argsort(-alignment)[:5]:
    print(f"  {EMOTION_LABELS[idx_e]:<28}  Brain={rsa_brain[idx_e]:.4f}  "
          f"V-JEPA2={rsa_vjepa2[idx_e]:.4f}  align={alignment[idx_e]:.4f}")

print(f"\nTop 5 DIVERGENT emotions (|Brain - V-JEPA2| highest) — Brain Tuning targets:")
for idx_e in np.argsort(-divergence)[:5]:
    print(f"  {EMOTION_LABELS[idx_e]:<28}  Brain={rsa_brain[idx_e]:.4f}  "
          f"V-JEPA2={rsa_vjepa2[idx_e]:.4f}  diverge={divergence[idx_e]:.4f}")

print(f"\nEmotions where Brain > V-JEPA2:")
brain_gt_v = rsa_brain > rsa_vjepa2
print(f"  Count: {brain_gt_v.sum()}/34")
for idx_e in np.where(brain_gt_v)[0]:
    print(f"  {EMOTION_LABELS[idx_e]:<28}  Brain={rsa_brain[idx_e]:.4f}  V-JEPA2={rsa_vjepa2[idx_e]:.4f}")

print(f"\nEmotions where V-JEPA2 > Brain:")
print(f"  Count: {(~brain_gt_v).sum()}/34")

# ── Save ──────────────────────────────────────────────────────────────────────
np.savez(OUTPUT_DIR / "crossspace_rsa_results.npz",
         emotion_labels=np.array(EMOTION_LABELS),
         rsa_brain=rsa_brain,
         rsa_vjepa2=rsa_vjepa2,
         rsa_clip=rsa_clip,
         alignment=alignment,
         divergence=divergence)

print(f"\nSaved: {OUTPUT_DIR}/crossspace_rsa_results.npz")
