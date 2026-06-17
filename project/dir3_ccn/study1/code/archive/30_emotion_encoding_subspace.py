"""
Exp 30: Emotion-encoding subspace of V-JEPA2 (M2 of the M1/M2/M3 framework).

For each V-JEPA2 PC (1..100), measure how well it encodes emotion ratings,
using ALL applicable metrics (multi-metric collection rule).

Continuous regression targets: 34 category mean rater scores + arousal + valence
  Metrics: R², Pearson r, Spearman r, MAE, RMSE, explained variance

Categorical decoding target: per-stimulus top-rated category (filtered to cats with >=10 samples)
  Metrics: top-1 acc, top-5 acc, ROC-AUC (OvR + OvO), macro F1, weighted F1,
           Cohen's kappa, Matthews correlation coefficient

Output: per-PC table with all metrics, used by Exp 32 (M3 overlap analysis).
"""

import numpy as np
import warnings
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, KFold, StratifiedKFold
from sklearn.metrics import (
    roc_auc_score, accuracy_score, top_k_accuracy_score,
    f1_score, cohen_kappa_score, matthews_corrcoef,
    mean_absolute_error, mean_squared_error, explained_variance_score,
)
from sklearn.decomposition import PCA
from scipy.stats import pearsonr, spearmanr
import pandas as pd
from pathlib import Path

warnings.filterwarnings('ignore', category=UserWarning)

# ── Paths ─────────────────────────────────────────────────────────────────────
VJEPA_PATH = Path("/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/data/raw/video_embeddings/vjepa2_embeddings.npy")
META_PATH  = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv")
OUTPUT_DIR = Path("/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/study1/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EMOTION_LABELS = [
    'Admiration', 'Adoration', 'Aesthetic appreciation', 'Amusement', 'Anger',
    'Anxiety', 'Awe', 'Awkwardness', 'Boredom', 'Calmness', 'Confusion',
    'Contempt', 'Craving', 'Disgust', 'Empathic pain', 'Entrancement',
    'Excitement', 'Fear', 'Horror', 'Interest', 'Joy', 'Nostalgia', 'Relief',
    'Romance', 'Sadness', 'Satisfaction', 'Sexual desire', 'Surprise',
    'Sympathy', 'Triumph', 'Uncomfortable', 'Annoyance', 'Envy', 'Guilt'
]

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading data...")
vjepa = np.load(VJEPA_PATH).astype(np.float64)
meta = pd.read_csv(META_PATH)
meta['stim_idx'] = meta['stimulus_num'].str.extract(r'(\d+)').astype(int) - 1
meta = meta.sort_values('stim_idx').reset_index(drop=True)

score_cols = [f"score_{i}" for i in range(34)]
emotion_scores = meta[score_cols].values.astype(np.float64)
arousal = meta['arousal_score'].values.astype(np.float64)
valence = meta['valence_score'].values.astype(np.float64)

top_category = np.argmax(emotion_scores, axis=1)

print(f"  V-JEPA2: {vjepa.shape}")
print(f"  Emotion scores: {emotion_scores.shape}")

# ── PCA on V-JEPA2 ────────────────────────────────────────────────────────────
N_PC = 100
print(f"\nFitting PCA ({N_PC} components)...")
pca = PCA(n_components=N_PC, random_state=42)
vjepa_pcs = pca.fit_transform(vjepa)
print(f"  Cumulative variance: {pca.explained_variance_ratio_.cumsum()[-1]:.4f}")

# ── Continuous regression — per PC × per target × per metric ─────────────────
print("\n[M2-cont] Per-PC continuous regression (multi-metric)...")
ridge = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])
cv = KFold(n_splits=5, shuffle=True, random_state=42)

n_targets = 36
all_targets = np.column_stack([emotion_scores, arousal, valence])
target_names = EMOTION_LABELS + ['Arousal', 'Valence']

# Initialize metric containers
cont_metrics = {
    'r2': np.zeros((N_PC, n_targets)),
    'r2_clipped': np.zeros((N_PC, n_targets)),
    'pearson_r': np.zeros((N_PC, n_targets)),
    'spearman_r': np.zeros((N_PC, n_targets)),
    'mae': np.zeros((N_PC, n_targets)),
    'rmse': np.zeros((N_PC, n_targets)),
    'explained_variance': np.zeros((N_PC, n_targets)),
}

for k in range(N_PC):
    X = vjepa_pcs[:, k:k+1]
    for t in range(n_targets):
        y = all_targets[:, t]
        # CV predictions for non-R² metrics
        y_pred = np.zeros_like(y)
        r2_folds = []
        for train_idx, test_idx in cv.split(X):
            ridge.fit(X[train_idx], y[train_idx])
            y_pred[test_idx] = ridge.predict(X[test_idx])
            # per-fold R²
            from sklearn.metrics import r2_score
            r2_folds.append(r2_score(y[test_idx], y_pred[test_idx]))
        r2_mean = float(np.mean(r2_folds))
        cont_metrics['r2'][k, t] = r2_mean
        cont_metrics['r2_clipped'][k, t] = max(r2_mean, 0.0)
        cont_metrics['pearson_r'][k, t] = pearsonr(y, y_pred)[0]
        cont_metrics['spearman_r'][k, t] = spearmanr(y, y_pred)[0]
        cont_metrics['mae'][k, t] = mean_absolute_error(y, y_pred)
        cont_metrics['rmse'][k, t] = np.sqrt(mean_squared_error(y, y_pred))
        cont_metrics['explained_variance'][k, t] = explained_variance_score(y, y_pred)
    if (k + 1) % 10 == 0 or k < 5:
        cat_r2 = cont_metrics['r2_clipped'][k, :34].mean()
        av_r2 = cont_metrics['r2_clipped'][k, 34:].mean()
        cat_pearson = cont_metrics['pearson_r'][k, :34].mean()
        av_pearson = cont_metrics['pearson_r'][k, 34:].mean()
        print(f"  PC{k+1}: cat R²={cat_r2:.4f} (Pearson={cat_pearson:.4f}), AV R²={av_r2:.4f} (Pearson={av_pearson:.4f})")

# Save intermediate (in case categorical step crashes again)
np.savez(OUTPUT_DIR / 'exp30_cont_intermediate.npz',
         **cont_metrics,
         target_names=np.array(target_names))
print(f"\nIntermediate continuous results saved.")

# ── Categorical decoding — per PC × multiple metrics ─────────────────────────
print("\n[M2-cat] Per-PC categorical decoding (multi-metric)...")

# Filter to categories with >= 10 samples
unique_labels, label_counts = np.unique(top_category, return_counts=True)
valid_label_mask = label_counts >= 10
valid_labels = unique_labels[valid_label_mask]
print(f"  Valid categories (>=10 samples): {len(valid_labels)} / {len(unique_labels)}")

keep_idx = np.isin(top_category, valid_labels)
top_cat_sub = top_category[keep_idx]
print(f"  Samples used: {keep_idx.sum()} / {len(top_category)}")

cat_metrics = {
    'top1_acc': np.zeros(N_PC),
    'top5_acc': np.zeros(N_PC),
    'auc_ovr_macro': np.zeros(N_PC),
    'auc_ovo_macro': np.zeros(N_PC),
    'f1_macro': np.zeros(N_PC),
    'f1_weighted': np.zeros(N_PC),
    'cohen_kappa': np.zeros(N_PC),
    'matthews_corr': np.zeros(N_PC),
}

clf = Pipeline([
    ('scaler', StandardScaler()),
    ('logreg', LogisticRegression(max_iter=2000, random_state=42))
])
cv_strat = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for k in range(N_PC):
    X = vjepa_pcs[keep_idx, k:k+1]
    y = top_cat_sub

    y_pred_all = np.zeros(len(y), dtype=int)
    y_proba_all = np.zeros((len(y), len(valid_labels)))

    for train_idx, test_idx in cv_strat.split(X, y):
        clf.fit(X[train_idx], y[train_idx])
        y_pred_all[test_idx] = clf.predict(X[test_idx])
        proba = clf.predict_proba(X[test_idx])
        classes = clf.named_steps['logreg'].classes_
        for j, c in enumerate(classes):
            col_idx = np.where(valid_labels == c)[0]
            if len(col_idx) > 0:
                y_proba_all[test_idx, col_idx[0]] = proba[:, j]

    cat_metrics['top1_acc'][k] = accuracy_score(y, y_pred_all)
    try:
        cat_metrics['top5_acc'][k] = top_k_accuracy_score(y, y_proba_all, k=5, labels=valid_labels)
    except Exception:
        cat_metrics['top5_acc'][k] = np.nan
    try:
        cat_metrics['auc_ovr_macro'][k] = roc_auc_score(y, y_proba_all, multi_class='ovr',
                                                        labels=valid_labels, average='macro')
    except Exception:
        cat_metrics['auc_ovr_macro'][k] = np.nan
    try:
        cat_metrics['auc_ovo_macro'][k] = roc_auc_score(y, y_proba_all, multi_class='ovo',
                                                        labels=valid_labels, average='macro')
    except Exception:
        cat_metrics['auc_ovo_macro'][k] = np.nan
    cat_metrics['f1_macro'][k] = f1_score(y, y_pred_all, average='macro', zero_division=0)
    cat_metrics['f1_weighted'][k] = f1_score(y, y_pred_all, average='weighted', zero_division=0)
    cat_metrics['cohen_kappa'][k] = cohen_kappa_score(y, y_pred_all)
    cat_metrics['matthews_corr'][k] = matthews_corrcoef(y, y_pred_all)

    if (k + 1) % 10 == 0 or k < 5:
        print(f"  PC{k+1}: top1={cat_metrics['top1_acc'][k]:.3f}, "
              f"top5={cat_metrics['top5_acc'][k]:.3f}, "
              f"AUC-OvR={cat_metrics['auc_ovr_macro'][k]:.3f}, "
              f"F1-macro={cat_metrics['f1_macro'][k]:.3f}, "
              f"kappa={cat_metrics['cohen_kappa'][k]:.3f}")

# ── Summary: ranking per metric ───────────────────────────────────────────────
print("\n" + "=" * 70)
print("Top 10 PCs by each metric")
print("=" * 70)

# Continuous: mean over 34 categories
cat_mean_r2 = cont_metrics['r2_clipped'][:, :34].mean(axis=1)
cat_mean_pearson = cont_metrics['pearson_r'][:, :34].mean(axis=1)
av_mean_r2 = cont_metrics['r2_clipped'][:, 34:].mean(axis=1)

rankings = {
    'cat_mean_r2': cat_mean_r2,
    'cat_mean_pearson': cat_mean_pearson,
    'av_mean_r2': av_mean_r2,
    'top1_acc': cat_metrics['top1_acc'],
    'top5_acc': cat_metrics['top5_acc'],
    'auc_ovr': cat_metrics['auc_ovr_macro'],
    'f1_macro': cat_metrics['f1_macro'],
}

for name, scores in rankings.items():
    top_pcs = np.argsort(-scores)[:10]
    print(f"\n  {name}:")
    print(f"    Top 10 PCs: {[int(pc)+1 for pc in top_pcs]}")
    print(f"    Scores: {[f'{scores[pc]:.4f}' for pc in top_pcs]}")

# ── Save ──────────────────────────────────────────────────────────────────────
save_dict = {
    **{f'cont_{k}': v for k, v in cont_metrics.items()},
    **{f'cat_{k}': v for k, v in cat_metrics.items()},
    'target_names': np.array(target_names),
    'cat_mean_r2': cat_mean_r2,
    'cat_mean_pearson': cat_mean_pearson,
    'av_mean_r2': av_mean_r2,
    'valid_labels': valid_labels,
    'cumulative_variance': pca.explained_variance_ratio_.cumsum(),
}
out_path = OUTPUT_DIR / 'exp30_emotion_encoding_subspace.npz'
np.savez(out_path, **save_dict)
print(f"\nSaved → {out_path}")
print("\nMulti-metric collected. Next: Exp 32 M3 overlap analysis (uses these rankings).")
print("Done.")
