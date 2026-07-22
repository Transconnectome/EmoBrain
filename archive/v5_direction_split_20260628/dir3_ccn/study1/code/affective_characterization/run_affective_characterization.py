"""
Affective-characterization module for video-model dimensions.

For a given video model PC, measure how well it encodes emotion ratings:
  - Continuous regression on 34 category scores + arousal + valence
    Multi-metric: R² (raw + clipped), Pearson r, Spearman r, MAE, RMSE, explained_variance
  - Categorical decoding on per-stimulus top-rated category (>=10 samples)
    Multi-metric: top-1 acc, top-5 acc, ROC-AUC (OvR + OvO), macro F1, weighted F1,
                  Cohen's kappa, Matthews correlation coefficient

Stimulus: 2185 canonical.

Usage:
  python run_affective_characterization.py --model vjepa2_pretrained
  python run_affective_characterization.py --model clip_pretrained
  ...
"""

import argparse
import warnings
import numpy as np
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.metrics import (
    roc_auc_score, accuracy_score, top_k_accuracy_score,
    f1_score, cohen_kappa_score, matthews_corrcoef,
    mean_absolute_error, mean_squared_error, explained_variance_score, r2_score,
)
from sklearn.decomposition import PCA
import scipy.io as sio
from scipy.stats import pearsonr, spearmanr
from pathlib import Path

warnings.filterwarnings('ignore', category=UserWarning)

# ── Constants ─────────────────────────────────────────────────────────────────
N_STIM = 2185
N_PC = 100
SEED = 42

def find_project_root():
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "CLAUDE.md").is_file() and (candidate / "study1").is_dir():
            return candidate
    raise RuntimeError("Could not locate the CCN project root")


def load_feature(root, name):
    obj = sio.loadmat(
        root / "data/raw/feature" / f"{name}.mat",
        squeeze_me=True,
        struct_as_record=False,
    )["L"]
    values = np.asarray(obj.feat, dtype=np.float64)[:N_STIM]
    labels = [str(label).replace("_", " ") for label in np.asarray(obj.featname).tolist()]
    return values, labels


ROOT = find_project_root()
EMBED_DIR = ROOT / "data/raw/video_embeddings"
OUTPUT_DIR = ROOT / "study1/data/affective_characterization"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATHS = {
    'vjepa2_pretrained':  'emovis_vjepa2_pretrained.npy',
    'vjepa2_scratch':     'emovis_vjepa2_scratch.npy',
    'clip_pretrained':    'emovis_clip_pretrained.npy',
    'clip_scratch':       'emovis_clip_scratch.npy',
    'dinov2_pretrained':  'emovis_dinov2_pretrained.npy',
    'dinov2_scratch':     'emovis_dinov2_scratch.npy',
    'videomae_pretrained':'emovis_videomae_pretrained.npy',
    'videomae_scratch':   'emovis_videomae_scratch.npy',
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True, choices=list(MODEL_PATHS.keys()))
    args = ap.parse_args()

    print(f"=== Affective characterization: model={args.model}, n_stim={N_STIM}, n_pc={N_PC} ===\n")

    # Load
    print("Loading data...")
    embed = np.load(EMBED_DIR / MODEL_PATHS[args.model]).astype(np.float64)
    emotion_scores, emotion_labels = load_feature(ROOT, "categcontinuous")
    dimensions, dimension_labels = load_feature(ROOT, "dimension")
    dimension_lookup = {name.lower(): i for i, name in enumerate(dimension_labels)}
    arousal = dimensions[:, dimension_lookup["arousal"]]
    valence = dimensions[:, dimension_lookup["valence"]]

    # Slice to 2185 canonical
    if embed.shape[0] > N_STIM:
        embed = embed[:N_STIM]
    emotion_scores = emotion_scores[:N_STIM]
    arousal = arousal[:N_STIM]
    valence = valence[:N_STIM]
    top_category = np.argmax(emotion_scores, axis=1)
    print(f"  Embed: {embed.shape}, emotion: {emotion_scores.shape}")

    # PCA
    print(f"\nFitting PCA ({N_PC} components)...")
    pca = PCA(n_components=N_PC, random_state=SEED)
    pcs = pca.fit_transform(embed)
    print(f"  Cumulative variance: {pca.explained_variance_ratio_.cumsum()[-1]:.4f}")

    # ── Continuous regression ────────────────────────────────────────────────
    print("\n[M2-cont] Per-PC continuous regression (multi-metric)...")
    ridge = Pipeline([('scaler', StandardScaler()), ('ridge', Ridge(alpha=1.0))])
    cv = KFold(n_splits=5, shuffle=True, random_state=SEED)
    n_targets = 36
    all_targets = np.column_stack([emotion_scores, arousal, valence])
    target_names = emotion_labels + ['Arousal', 'Valence']

    cont = {k: np.zeros((N_PC, n_targets)) for k in
            ['r2_raw', 'r2_clipped', 'pearson_r', 'spearman_r', 'mae', 'rmse', 'explained_variance']}

    for k in range(N_PC):
        X = pcs[:, k:k+1]
        for t in range(n_targets):
            y = all_targets[:, t]
            y_pred = np.zeros_like(y)
            r2_folds = []
            for train_idx, test_idx in cv.split(X):
                ridge.fit(X[train_idx], y[train_idx])
                y_pred[test_idx] = ridge.predict(X[test_idx])
                r2_folds.append(r2_score(y[test_idx], y_pred[test_idx]))
            r2_mean = float(np.mean(r2_folds))
            cont['r2_raw'][k, t] = r2_mean
            cont['r2_clipped'][k, t] = max(r2_mean, 0.0)
            cont['pearson_r'][k, t] = pearsonr(y, y_pred)[0]
            cont['spearman_r'][k, t] = spearmanr(y, y_pred)[0]
            cont['mae'][k, t] = mean_absolute_error(y, y_pred)
            cont['rmse'][k, t] = np.sqrt(mean_squared_error(y, y_pred))
            cont['explained_variance'][k, t] = explained_variance_score(y, y_pred)
        if (k+1) % 10 == 0 or k < 5:
            cr = cont['r2_clipped'][k, :34].mean()
            ar = cont['r2_clipped'][k, 34:].mean()
            cp = cont['pearson_r'][k, :34].mean()
            print(f"  PC{k+1}: cat R²={cr:.4f} (Pearson={cp:.4f}), AV R²={ar:.4f}")

    # Save intermediate
    np.savez(OUTPUT_DIR / f'continuous_metrics_{args.model}.npz', **cont)
    print(f"  Intermediate continuous saved.")

    # ── Categorical decoding ─────────────────────────────────────────────────
    print("\n[M2-cat] Per-PC categorical decoding (multi-metric)...")
    unique_labels, label_counts = np.unique(top_category, return_counts=True)
    valid_label_mask = label_counts >= 10
    valid_labels = unique_labels[valid_label_mask]
    keep_idx = np.isin(top_category, valid_labels)
    top_cat_sub = top_category[keep_idx]
    print(f"  Valid categories (>=10 samples): {len(valid_labels)} / {len(unique_labels)}")
    print(f"  Samples used: {keep_idx.sum()} / {len(top_category)}")

    cat = {k: np.zeros(N_PC) for k in
           ['top1_acc', 'top5_acc', 'auc_ovr_macro', 'auc_ovo_macro',
            'f1_macro', 'f1_weighted', 'cohen_kappa', 'matthews_corr']}

    clf = Pipeline([
        ('scaler', StandardScaler()),
        ('logreg', LogisticRegression(max_iter=2000, random_state=SEED))
    ])
    cv_strat = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    for k in range(N_PC):
        X = pcs[keep_idx, k:k+1]
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

        cat['top1_acc'][k] = accuracy_score(y, y_pred_all)
        try: cat['top5_acc'][k] = top_k_accuracy_score(y, y_proba_all, k=5, labels=valid_labels)
        except Exception: cat['top5_acc'][k] = np.nan
        try: cat['auc_ovr_macro'][k] = roc_auc_score(y, y_proba_all, multi_class='ovr', labels=valid_labels, average='macro')
        except Exception: cat['auc_ovr_macro'][k] = np.nan
        try: cat['auc_ovo_macro'][k] = roc_auc_score(y, y_proba_all, multi_class='ovo', labels=valid_labels, average='macro')
        except Exception: cat['auc_ovo_macro'][k] = np.nan
        cat['f1_macro'][k] = f1_score(y, y_pred_all, average='macro', zero_division=0)
        cat['f1_weighted'][k] = f1_score(y, y_pred_all, average='weighted', zero_division=0)
        cat['cohen_kappa'][k] = cohen_kappa_score(y, y_pred_all)
        cat['matthews_corr'][k] = matthews_corrcoef(y, y_pred_all)

        if (k+1) % 10 == 0 or k < 5:
            print(f"  PC{k+1}: top1={cat['top1_acc'][k]:.3f}, "
                  f"top5={cat['top5_acc'][k]:.3f}, AUC-OvR={cat['auc_ovr_macro'][k]:.3f}, "
                  f"F1={cat['f1_macro'][k]:.3f}, kappa={cat['cohen_kappa'][k]:.3f}")

    # ── Rankings ─────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("Top 10 PCs per metric")
    print("="*70)
    cat_mean_r2 = cont['r2_clipped'][:, :34].mean(axis=1)
    av_mean_r2 = cont['r2_clipped'][:, 34:].mean(axis=1)
    rankings = {
        'cat_mean_r2': cat_mean_r2,
        'av_mean_r2': av_mean_r2,
        'top1_acc': cat['top1_acc'],
        'auc_ovr': cat['auc_ovr_macro'],
        'f1_macro': cat['f1_macro'],
    }
    for name, scores in rankings.items():
        top = np.argsort(-scores)[:10]
        print(f"  {name}: top10 PCs = {[int(p)+1 for p in top]}, scores = {[f'{scores[p]:.4f}' for p in top]}")

    # ── Save ─────────────────────────────────────────────────────────────────
    save_dict = {
        'model_name': args.model,
        'n_stim': N_STIM,
        'n_pc': N_PC,
        **{f'cont_{k}': v for k, v in cont.items()},
        **{f'cat_{k}': v for k, v in cat.items()},
        'target_names': np.array(target_names),
        'cat_mean_r2': cat_mean_r2,
        'av_mean_r2': av_mean_r2,
        'valid_labels': valid_labels,
        'cumulative_variance': pca.explained_variance_ratio_.cumsum(),
        'pcs': pcs,
    }
    out_path = OUTPUT_DIR / f'affective_characterization_{args.model}.npz'
    np.savez(out_path, **save_dict)
    print(f"\nSaved → {out_path}\nDone.")

if __name__ == '__main__':
    main()
