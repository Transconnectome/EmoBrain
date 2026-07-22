"""
CCN Analysis 12: Brain-Predictable Subspace — Category vs Dimension 설명력 비교

핵심 질문:
  Brain-predictable subspace (3~6개 PC)가 설명하는 것은
  고차원 감정 카테고리(34개)인가, 아니면 A/V/D로 환원되는 저차원 affective dimension인가?

Analysis:
  1. Brain-pred subspace → 34 categories + A/V/D 각각 Ridge CV R²
  2. Mean R²(categories) vs Mean R²(dimensions) 직접 비교
  3. Baseline: unpredictable subspace & full 100 PC subspace와 비교
  4. Efficiency = R²(pred) / R²(all): 3~6개 PC가 전체의 몇 %를 커버하는가

Input:
  video_embeddings/vjepa2_embeddings.npy     (2196, 1408)
  video_embeddings/clip_embeddings.npy       (2196, 512)
  CCN/results/pc_emotion_correlation.npz     (brain_pred_mask, r2_per_dim)
  metadata CSV                               (34 emotion scores + A/V/D)

Output:
  CCN/results/brain_pred_subspace_prediction.npz
  CCN/figures/brain_pred_subspace_r2_all.png   — Figure A: cat + dim R² bar (pred subspace)
  CCN/figures/brain_pred_subspace_scatter.png  — Figure B: pred vs all scatter
  CCN/figures/brain_pred_efficiency.png        — Figure C: efficiency bar
"""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE       = Path("/pscratch/sd/s/sjmoon/EmoFM")
VJEPA_PATH = BASE / "video_embeddings/vjepa2_embeddings.npy"
CLIP_PATH  = BASE / "video_embeddings/clip_embeddings.npy"
META_PATH  = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
PC_EMO_PATH = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results/pc_emotion_correlation.npz")
OUTPUT_DIR = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/results")
FIG_DIR    = Path("/pscratch/sd/s/sjmoon/EmoFM/CCN/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

N_PC      = 100
R2_THRESH = 0.01
CV        = 5

EMOTION_LABELS = [
    'Admiration', 'Adoration', 'Aesthetic appreciation', 'Amusement', 'Anger',
    'Anxiety', 'Awe', 'Awkwardness', 'Boredom', 'Calmness', 'Confusion',
    'Contempt', 'Craving', 'Disgust', 'Empathic pain', 'Entrancement',
    'Excitement', 'Fear', 'Horror', 'Interest', 'Joy', 'Nostalgia', 'Relief',
    'Romance', 'Sadness', 'Satisfaction', 'Sexual desire', 'Surprise',
    'Sympathy', 'Triumph', 'Uncomfortable', 'Annoyance', 'Envy', 'Guilt'
]
DIM_LABELS = ['Arousal', 'Valence', 'Dominance']

# ── Load ───────────────────────────────────────────────────────────────────────
print("Loading data...")
vjepa     = np.load(VJEPA_PATH).astype(np.float64)
clip_emb  = np.load(CLIP_PATH).astype(np.float64)

meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

emotion_scores = meta[[f"score_{i}" for i in range(34)]].values.astype(np.float64)  # (2196, 34)
avd_scores     = meta[['arousal_score', 'valence_score', 'dominance_score']].values.astype(np.float64)  # (2196, 3)

# brain-pred masks from Exp 11
pc_data = np.load(PC_EMO_PATH, allow_pickle=True)
r2_vjepa     = pc_data['r2_vjepa']
r2_clip      = pc_data['r2_clip']
pred_v       = r2_vjepa > R2_THRESH
pred_c       = r2_clip  > R2_THRESH

pred_idx_v   = np.where(pred_v)[0]
pred_idx_c   = np.where(pred_c)[0]
unpred_idx_v = np.where(~pred_v)[0]
unpred_idx_c = np.where(~pred_c)[0]

print(f"  V-JEPA2 brain-pred PCs: {pred_idx_v + 1} (n={len(pred_idx_v)})")
print(f"  CLIP    brain-pred PCs: {pred_idx_c + 1} (n={len(pred_idx_c)})")

# ── PCA ────────────────────────────────────────────────────────────────────────
print("\nFitting PCA (100 components)...")
vjepa_pca = PCA(n_components=N_PC, random_state=42)
vjepa_pcs = vjepa_pca.fit_transform(vjepa)   # (2196, 100)

clip_pca  = PCA(n_components=N_PC, random_state=42)
clip_pcs  = clip_pca.fit_transform(clip_emb) # (2196, 100)

# subspace slices
X = {
    'vjepa': {
        'pred':   vjepa_pcs[:, pred_idx_v],
        'unpred': vjepa_pcs[:, unpred_idx_v],
        'all':    vjepa_pcs,
    },
    'clip': {
        'pred':   clip_pcs[:, pred_idx_c],
        'unpred': clip_pcs[:, unpred_idx_c],
        'all':    clip_pcs,
    },
}

# ── Ridge CV helper ────────────────────────────────────────────────────────────
pipe = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])

def ridge_r2(features, target):
    return max(cross_val_score(pipe, features, target, cv=CV, scoring='r2').mean(), 0)

# ── Analysis 1~3: pred / unpred / all → each target ───────────────────────────
# targets: 34 emotions + 3 dimensions = 37 total
target_names  = EMOTION_LABELS + DIM_LABELS
target_matrix = np.hstack([emotion_scores, avd_scores])   # (2196, 37)
is_dim        = [False] * 34 + [True] * 3                 # flag for cat vs dim

results = {}   # results[model][subspace][target_name] = R²

for model_name in ['vjepa', 'clip']:
    results[model_name] = {k: {} for k in ['pred', 'unpred', 'all']}
    n_pred = X[model_name]['pred'].shape[1]
    print(f"\nComputing {model_name} (pred n={n_pred})...")
    for subspace in ['pred', 'unpred', 'all']:
        feats = X[model_name][subspace]
        print(f"  [{subspace}, {feats.shape[1]} PCs]")
        for ti, tname in enumerate(target_names):
            r2 = ridge_r2(feats, target_matrix[:, ti])
            results[model_name][subspace][tname] = r2
        # summary print
        cat_mean = np.mean([results[model_name][subspace][e] for e in EMOTION_LABELS])
        dim_mean = np.mean([results[model_name][subspace][d] for d in DIM_LABELS])
        print(f"    mean R² cat={cat_mean:.4f}  dim={dim_mean:.4f}  ratio(cat/dim)={cat_mean/max(dim_mean,1e-10):.2f}")

# ── Print detailed summary ─────────────────────────────────────────────────────
for model_name, mkey, pred_idx in [('V-JEPA2', 'vjepa', pred_idx_v), ('CLIP', 'clip', pred_idx_c)]:
    r = results[mkey]
    cat_r2_pred = [r['pred'][e] for e in EMOTION_LABELS]
    dim_r2_pred = [r['pred'][d] for d in DIM_LABELS]
    cat_r2_all  = [r['all'][e]  for e in EMOTION_LABELS]
    dim_r2_all  = [r['all'][d]  for d in DIM_LABELS]

    print(f"\n{'='*60}")
    print(f"=== {model_name}: Brain-pred subspace (PC {list(pred_idx+1)}) ===")
    print(f"{'='*60}")
    print(f"Mean R²(34 categories) from pred:  {np.mean(cat_r2_pred):.4f}")
    print(f"Mean R²(34 categories) from all:   {np.mean(cat_r2_all):.4f}")
    print(f"Mean R²(A/V/D)         from pred:  {np.mean(dim_r2_pred):.4f}")
    print(f"Mean R²(A/V/D)         from all:   {np.mean(dim_r2_all):.4f}")
    print(f"Ratio cat/dim (pred subspace):     {np.mean(cat_r2_pred)/max(np.mean(dim_r2_pred),1e-10):.3f}")
    print()
    print("Top 10 emotions (pred subspace R²):")
    sorted_emo = sorted(zip(EMOTION_LABELS, cat_r2_pred), key=lambda x: x[1], reverse=True)
    for name, rv in sorted_emo[:10]:
        ra = r['all'][name]
        eff = rv / max(ra, 1e-10)
        print(f"  {name:30s}: pred R²={rv:.4f}  all R²={ra:.4f}  eff={eff:.1%}")
    print()
    print("Bottom 5 emotions (pred subspace R²):")
    for name, rv in sorted_emo[-5:]:
        ra = r['all'][name]
        eff = rv / max(ra, 1e-10)
        print(f"  {name:30s}: pred R²={rv:.4f}  all R²={ra:.4f}  eff={eff:.1%}")
    print()
    print("Affective Dimensions (A/V/D):")
    for dname in DIM_LABELS:
        rv = r['pred'][dname]
        ra = r['all'][dname]
        eff = rv / max(ra, 1e-10)
        print(f"  {dname:30s}: pred R²={rv:.4f}  all R²={ra:.4f}  eff={eff:.1%}")

# ── Figure A: bar chart — pred subspace R² for all 37 targets ─────────────────
print("\nGenerating Figure A...")
fig, axes = plt.subplots(2, 1, figsize=(18, 10))
fig.patch.set_facecolor('white')

for ax, model_name in [(axes[0], 'vjepa'), (axes[1], 'clip')]:
    r = results[model_name]
    label = 'V-JEPA2' if model_name == 'vjepa' else 'CLIP'
    pred_idx_local = pred_idx_v if model_name == 'vjepa' else pred_idx_c

    # sort emotions by pred R²
    emo_pairs = sorted(zip(EMOTION_LABELS, [r['pred'][e] for e in EMOTION_LABELS]),
                       key=lambda x: x[1], reverse=True)
    dim_pairs = [(d, r['pred'][d]) for d in DIM_LABELS]

    names  = [p[0] for p in emo_pairs] + [''] + [p[0] for p in dim_pairs]
    vals_pred   = [p[1] for p in emo_pairs] + [0] + [p[1] for p in dim_pairs]
    vals_all    = [r['all'][p[0]] for p in emo_pairs] + [0] + [r['all'][p[0]] for p in dim_pairs]
    colors_bar  = ['steelblue'] * 34 + ['white'] + ['tomato'] * 3

    x = np.arange(len(names))
    ax.bar(x, vals_all,  color='lightgray', alpha=0.6, label='All 100 PCs')
    ax.bar(x, vals_pred, color=colors_bar,  alpha=0.85,
           label=f'Brain-pred subspace (n={len(pred_idx_local)} PCs)')

    mean_cat = np.mean([p[1] for p in emo_pairs])
    mean_dim = np.mean([p[1] for p in dim_pairs])
    ax.axhline(mean_cat, color='steelblue', linestyle='--', alpha=0.7,
               label=f'mean cat R²={mean_cat:.3f}')
    ax.axhline(mean_dim, color='tomato', linestyle='--', alpha=0.7,
               label=f'mean dim R²={mean_dim:.3f}')

    # divider between emotions and dimensions
    ax.axvline(33.5, color='black', linestyle=':', alpha=0.5)
    ax.text(33.7, ax.get_ylim()[1] * 0.95 if ax.get_ylim()[1] > 0 else 0.05,
            'A/V/D →', fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=90, fontsize=7)
    ax.set_ylabel('R² (5-fold CV Ridge)', fontsize=10)
    ax.set_title(
        f'{label}: Brain-predictable subspace ({len(pred_idx_local)} PCs) prediction R²\n'
        f'(gray = all 100 PCs, colored = pred subspace only | cat/dim ratio={mean_cat/max(mean_dim,1e-10):.2f})',
        fontsize=11, fontweight='bold')
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
path = FIG_DIR / "brain_pred_subspace_r2_all.png"
plt.savefig(path, dpi=200, bbox_inches='tight')
print(f"  Saved: {path}")
plt.close()

# ── Figure B: scatter — R²(pred subspace) vs R²(all 100 PCs) ──────────────────
print("Generating Figure B: scatter pred vs all...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor('white')

for ax, model_name in [(axes[0], 'vjepa'), (axes[1], 'clip')]:
    r = results[model_name]
    label = 'V-JEPA2' if model_name == 'vjepa' else 'CLIP'
    pred_idx_local = pred_idx_v if model_name == 'vjepa' else pred_idx_c

    # emotions
    x_cat = [r['all'][e]  for e in EMOTION_LABELS]
    y_cat = [r['pred'][e] for e in EMOTION_LABELS]
    ax.scatter(x_cat, y_cat, color='steelblue', alpha=0.7, s=50, label='34 Emotions', zorder=3)
    for i, name in enumerate(EMOTION_LABELS):
        if y_cat[i] > 0.05 or x_cat[i] > 0.1:
            ax.annotate(name, (x_cat[i], y_cat[i]), fontsize=6,
                        textcoords='offset points', xytext=(3, 2))

    # dimensions
    x_dim = [r['all'][d]  for d in DIM_LABELS]
    y_dim = [r['pred'][d] for d in DIM_LABELS]
    ax.scatter(x_dim, y_dim, color='tomato', alpha=0.9, s=120, marker='D',
               label='A/V/D', zorder=4)
    for i, name in enumerate(DIM_LABELS):
        ax.annotate(name, (x_dim[i], y_dim[i]), fontsize=9, fontweight='bold',
                    textcoords='offset points', xytext=(4, 3), color='tomato')

    # diagonal
    lim = max(max(x_cat + x_dim), max(y_cat + y_dim)) * 1.05
    ax.plot([0, lim], [0, lim], 'k--', alpha=0.3, linewidth=1, label='y=x (perfect)')
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel(f'R² from all 100 PCs', fontsize=11)
    ax.set_ylabel(f'R² from brain-pred {len(pred_idx_local)} PCs', fontsize=11)
    ax.set_title(f'{label}: Pred subspace vs Full subspace\n(above diagonal = pred captures most info)',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

plt.suptitle('Does brain-predictable subspace efficiently capture emotional information?',
             fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
path = FIG_DIR / "brain_pred_subspace_scatter.png"
plt.savefig(path, dpi=200, bbox_inches='tight')
print(f"  Saved: {path}")
plt.close()

# ── Figure C: efficiency = R²(pred) / R²(all) ─────────────────────────────────
print("Generating Figure C: efficiency bar...")
fig, axes = plt.subplots(2, 1, figsize=(18, 9))
fig.patch.set_facecolor('white')

for ax, model_name in [(axes[0], 'vjepa'), (axes[1], 'clip')]:
    r = results[model_name]
    label = 'V-JEPA2' if model_name == 'vjepa' else 'CLIP'
    pred_idx_local = pred_idx_v if model_name == 'vjepa' else pred_idx_c

    emo_pairs = sorted(zip(EMOTION_LABELS, [r['pred'][e] for e in EMOTION_LABELS]),
                       key=lambda x: x[1], reverse=True)
    dim_pairs = [(d, r['pred'][d]) for d in DIM_LABELS]

    names  = [p[0] for p in emo_pairs] + [''] + [p[0] for p in dim_pairs]
    # efficiency: R²(pred) / R²(all), cap at 1
    eff_cat = [min(r['pred'][p[0]] / max(r['all'][p[0]], 1e-6), 1.0) for p in emo_pairs]
    eff_dim = [min(r['pred'][d] / max(r['all'][d], 1e-6), 1.0) for d in DIM_LABELS]
    eff_all = eff_cat + [0] + eff_dim
    colors_bar = ['steelblue'] * 34 + ['white'] + ['tomato'] * 3

    x = np.arange(len(names))
    bars = ax.bar(x, eff_all, color=colors_bar, alpha=0.85)
    ax.axvline(33.5, color='black', linestyle=':', alpha=0.5)
    ax.axhline(1.0, color='gray', linestyle='--', alpha=0.4)

    mean_eff_cat = np.mean(eff_cat)
    mean_eff_dim = np.mean(eff_dim)
    ax.axhline(mean_eff_cat, color='steelblue', linestyle='--', alpha=0.7,
               label=f'mean eff cat={mean_eff_cat:.2f}')
    ax.axhline(mean_eff_dim, color='tomato', linestyle='--', alpha=0.7,
               label=f'mean eff dim={mean_eff_dim:.2f}')

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=90, fontsize=7)
    ax.set_ylabel('Efficiency: R²(pred) / R²(all)', fontsize=10)
    ax.set_ylim(0, 1.1)
    ax.set_title(
        f'{label}: How much does brain-pred subspace ({len(pred_idx_local)} PCs) capture vs full 100 PCs?\n'
        f'mean cat eff={mean_eff_cat:.2f}  mean dim eff={mean_eff_dim:.2f}',
        fontsize=11, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
path = FIG_DIR / "brain_pred_efficiency.png"
plt.savefig(path, dpi=200, bbox_inches='tight')
print(f"  Saved: {path}")
plt.close()

# ── Save ───────────────────────────────────────────────────────────────────────
# flatten results to arrays for npz
def results_to_arrays(r, tnames):
    return {
        'pred':   np.array([r['pred'][t]   for t in tnames]),
        'unpred': np.array([r['unpred'][t] for t in tnames]),
        'all':    np.array([r['all'][t]    for t in tnames]),
    }

rv = results_to_arrays(results['vjepa'], target_names)
rc = results_to_arrays(results['clip'],  target_names)

np.savez(
    OUTPUT_DIR / "brain_pred_subspace_prediction.npz",
    target_names         = np.array(target_names),
    emotion_labels       = np.array(EMOTION_LABELS),
    dim_labels           = np.array(DIM_LABELS),
    # V-JEPA2
    r2_pred_vjepa        = rv['pred'],    # (37,)
    r2_unpred_vjepa      = rv['unpred'],
    r2_all_vjepa         = rv['all'],
    pred_idx_vjepa       = pred_idx_v,
    # CLIP
    r2_pred_clip         = rc['pred'],
    r2_unpred_clip       = rc['unpred'],
    r2_all_clip          = rc['all'],
    pred_idx_clip        = pred_idx_c,
)
print(f"\nSaved: {OUTPUT_DIR}/brain_pred_subspace_prediction.npz")
print("\nDone.")
