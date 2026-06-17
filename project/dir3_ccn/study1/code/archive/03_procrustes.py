"""
CCN Analysis 03: Procrustes Alignment — Brain-JEPA vs Video Models

Purpose:
    Align Brain-JEPA and V-JEPA2/CLIP spaces via PCA + Procrustes.
    Quantify per-video and per-emotion alignment error (divergence).
    Divergence → Brain Tuning targets.

Default k = 27 (Cowen & Keltner 2017 reference).
Run 05_k_sweep.py to find optimal k, then re-run this script if needed.

Input:
    brain_embeddings/brain_jepa_embeddings.npy  (5, 2196, 768)
    video_embeddings/vjepa2_embeddings.npy       (2196, 1408)
    video_embeddings/clip_embeddings.npy          (2196, 512)
    metadata CSV

Output:
    CCN/results/procrustes_results.npz
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy.spatial import procrustes
from sklearn.decomposition import PCA
import time

# ── Paths ─────────────────────────────────────────────────────────────────────
BRAIN_EMB_PATH = Path("/pscratch/sd/s/sjmoon/EmoFM/brain_embeddings/brain_jepa_embeddings.npy")
VJEPA2_PATH    = Path("/pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy")
CLIP_PATH      = Path("/pscratch/sd/s/sjmoon/EmoFM/video_embeddings/clip_embeddings.npy")
META_PATH      = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
OUTPUT_DIR     = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results")

EMOTION_LABELS = [
    'Admiration','Adoration','Aesthetic appreciation','Amusement','Anger','Anxiety',
    'Awe','Awkwardness','Boredom','Calmness','Confusion','Contempt','Craving',
    'Disgust','Empathic pain','Entrancement','Excitement','Fear','Horror','Interest',
    'Joy','Nostalgia','Relief','Romance','Sadness','Satisfaction','Sexual desire',
    'Surprise','Sympathy','Triumph','Uncomfortable','Annoyance','Envy','Guilt'
]

# Check if k_sweep results available, else use k=27
K_SWEEP_PATH = OUTPUT_DIR / "k_sweep_results.npz"
if K_SWEEP_PATH.exists():
    ks = np.load(K_SWEEP_PATH)
    K_OPT = int(ks['k_elbow'])
    print(f"Using optimal k from k_sweep: k={K_OPT}")
else:
    K_OPT = 27
    print(f"k_sweep not yet run. Using default k={K_OPT} (Cowen & Keltner 2017)")

# ── Load data ─────────────────────────────────────────────────────────────────
print("\nLoading data...")
brain_emb  = np.load(BRAIN_EMB_PATH).astype(np.float64)  # (5, 2196, 768)
brain_mean = brain_emb.mean(axis=0)                       # (2196, 768)
vjepa2_emb = np.load(VJEPA2_PATH).astype(np.float64)
clip_emb   = np.load(CLIP_PATH).astype(np.float64)

meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

print(f"  Brain-JEPA mean: {brain_mean.shape}")
print(f"  V-JEPA2:         {vjepa2_emb.shape}")
print(f"  CLIP:            {clip_emb.shape}")

# ── Procrustes at multiple k values ──────────────────────────────────────────
def run_procrustes(brain, model_emb, k):
    brain_k = PCA(n_components=k).fit_transform(brain)
    model_k = PCA(n_components=k).fit_transform(model_emb)
    brain_std, model_aligned, disparity = procrustes(brain_k, model_k)
    error = np.linalg.norm(brain_std - model_aligned, axis=1)  # (2196,)
    return brain_std, model_aligned, disparity, error, brain_k, model_k

print(f"\n{'='*60}")
print(f"PROCRUSTES ALIGNMENT (k={K_OPT})")
print(f"{'='*60}")

t0 = time.time()
brain_std_v, vjepa_aligned, disp_v, err_v, brain_k, vjepa_k = run_procrustes(brain_mean, vjepa2_emb, K_OPT)
brain_std_c, clip_aligned,  disp_c, err_c, _,       clip_k  = run_procrustes(brain_mean, clip_emb,   K_OPT)
print(f"  [{time.time()-t0:.0f}s]")

print(f"\n  Procrustes disparity:")
print(f"    Brain-JEPA vs V-JEPA2: {disp_v:.4f}")
print(f"    Brain-JEPA vs CLIP:    {disp_c:.4f}")
print(f"    V-JEPA2 < CLIP: {disp_v < disp_c} (lower = better alignment with brain)")

print(f"\n  Per-video alignment error:")
print(f"    V-JEPA2: mean={err_v.mean():.4f}  std={err_v.std():.4f}  "
      f"min={err_v.min():.4f}  max={err_v.max():.4f}")
print(f"    CLIP:    mean={err_c.mean():.4f}  std={err_c.std():.4f}  "
      f"min={err_c.min():.4f}  max={err_c.max():.4f}")

# ── Per-emotion alignment error (score-weighted) ──────────────────────────────
emotion_err_v = np.zeros(34)
emotion_err_c = np.zeros(34)

for i in range(34):
    score_i = meta[f"score_{i}"].values.astype(np.float64)
    # Score-weighted average error (score as weight = how much each video represents emotion i)
    emotion_err_v[i] = np.average(err_v, weights=score_i)
    emotion_err_c[i] = np.average(err_c, weights=score_i)

print(f"\n  Per-emotion Procrustes error (V-JEPA2) — top 5 DIVERGENT (Brain Tuning targets):")
for idx in np.argsort(-emotion_err_v)[:5]:
    print(f"    {EMOTION_LABELS[idx]:<28}  V-JEPA2={emotion_err_v[idx]:.4f}  CLIP={emotion_err_c[idx]:.4f}")

print(f"\n  Per-emotion Procrustes error (V-JEPA2) — top 5 CONVERGENT:")
for idx in np.argsort(emotion_err_v)[:5]:
    print(f"    {EMOTION_LABELS[idx]:<28}  V-JEPA2={emotion_err_v[idx]:.4f}  CLIP={emotion_err_c[idx]:.4f}")

# ── Also run k=27 for reference if K_OPT != 27 ───────────────────────────────
extra = {}
if K_OPT != 27:
    print(f"\n  Also computing at k=27 for Cowen reference...")
    _, _, d27v, e27v, b27, v27 = run_procrustes(brain_mean, vjepa2_emb, 27)
    _, _, d27c, e27c, _,   c27 = run_procrustes(brain_mean, clip_emb,   27)
    print(f"    k=27: V-JEPA2={d27v:.4f}  CLIP={d27c:.4f}")
    extra = dict(brain_std_k27=b27, vjepa_aligned_k27=v27, clip_aligned_k27=c27,
                 disparity_vjepa_k27=d27v, disparity_clip_k27=d27c,
                 error_vjepa_k27=e27v, error_clip_k27=e27c)

# ── Save ──────────────────────────────────────────────────────────────────────
save_dict = dict(
    k_used=K_OPT,
    brain_std=brain_std_v,
    vjepa_aligned=vjepa_aligned,
    clip_aligned=clip_aligned,
    disparity_vjepa=disp_v,
    disparity_clip=disp_c,
    error_vjepa=err_v,
    error_clip=err_c,
    emotion_error_vjepa=emotion_err_v,
    emotion_error_clip=emotion_err_c,
    brain_k=brain_k,
    vjepa_k=vjepa_k,
    clip_k=clip_k,
    emotion_labels=np.array(EMOTION_LABELS),
    **extra
)
np.savez(OUTPUT_DIR / "procrustes_results.npz", **save_dict)
print(f"\nSaved: {OUTPUT_DIR}/procrustes_results.npz  (k={K_OPT})")
