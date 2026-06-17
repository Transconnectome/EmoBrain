"""
Phase 2 Direction 2 — Brain → video feature encoding.

For each stimulus, train a ridge regression that maps brain BFM embedding
(per-subject, frozen) → video feature (frozen). Evaluate on held-out fold by
Pearson r of (predicted, actual) per-feature-dim, averaged.

This measures how much video-relevant information the brain encoder carries
about the stimulus, independent of any emotion label.

Same 5-fold stim-stratified CV as Phase 1.

Output: results/phase2/encoding/<video>_<brain>.csv
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

sys.path.insert(0, "/pscratch/sd/s/sjmoon/EmoBrain/project/dir2_multimodal/code/legacy_phase2")

from _lib import (load_brain_embeddings, load_video_feature, get_fold_split,
                  DEFAULT_BRAIN, DEFAULT_BRAIN_INIT, DEFAULT_BRAIN_PAD, DEFAULT_VIDEO,
                  ALL_SUBJECTS)

EmoBrain = Path("/pscratch/sd/s/sjmoon/EmoBrain")
OUT_DIR = EmoBrain / "project/shared/results/phase2/encoding"

RIDGE_ALPHAS = [1e-2, 1e-1, 1.0, 10.0, 100.0, 1e3]


def build_xy(brain_dict, video_feat, vstim, stim_set):
    """For each stim in stim_set, for each subject, make (brain, video) pair.
    Returns X (N, D_brain), Y (N, D_video)."""
    stim_to_video = {int(s): i for i, s in enumerate(vstim)}
    X_list, Y_list = [], []
    for subj, (emb, stim_arr) in brain_dict.items():
        s2b = {int(s): i for i, s in enumerate(stim_arr)}
        for stim in stim_set:
            if stim not in s2b or stim not in stim_to_video:
                continue
            X_list.append(emb[s2b[stim]])
            Y_list.append(video_feat[stim_to_video[stim]])
    return np.stack(X_list, axis=0), np.stack(Y_list, axis=0)


def evaluate(y_true, y_pred):
    """Per-dim Pearson r → mean. Also report MAE / MSE averaged."""
    rs = []
    for d in range(y_true.shape[1]):
        if y_pred[:, d].std() < 1e-10:
            rs.append(0.0)
        else:
            r, _ = pearsonr(y_true[:, d], y_pred[:, d])
            rs.append(0.0 if np.isnan(r) else r)
    return {
        "test_pearson_r_mean": float(np.mean(rs)),
        "test_pearson_r_median": float(np.median(rs)),
        "test_pearson_r_std": float(np.std(rs)),
        "test_mae_mean": float(mean_absolute_error(y_true, y_pred)),
        "test_mse_mean": float(mean_squared_error(y_true, y_pred)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brain_model", default=DEFAULT_BRAIN)
    ap.add_argument("--brain_init", default=DEFAULT_BRAIN_INIT)
    ap.add_argument("--brain_padding", default=DEFAULT_BRAIN_PAD)
    ap.add_argument("--video", default=DEFAULT_VIDEO)
    ap.add_argument("--folds", default="1,2,3,4,5")
    ap.add_argument("--seeds", default="0",
                    help="Deterministic ridge; 1 seed enough.")
    ap.add_argument("--out_csv", default=None)
    args = ap.parse_args()

    folds = [int(f) for f in args.folds.split(",")]
    seeds = [int(s) for s in args.seeds.split(",")]
    out_csv = args.out_csv or str(OUT_DIR / f"{args.video}__{args.brain_model}_{args.brain_init}_{args.brain_padding}.csv")
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)

    print(f"=== Phase 2 Direction 2: Brain → video encoding ===")
    print(f"  brain={args.brain_model}/{args.brain_init}/{args.brain_padding} video={args.video}")

    brain = load_brain_embeddings(args.brain_model, args.brain_init, args.brain_padding)
    video, vstim = load_video_feature(args.video)

    rows = []
    for fold in folds:
        split = get_fold_split(fold)
        for seed in seeds:
            train_stim = split[split["split"] == "train"]["stimulus_num"].tolist()
            val_stim = split[split["split"] == "val"]["stimulus_num"].tolist()
            test_stim = split[split["split"] == "test"]["stimulus_num"].tolist()

            X_tr, Y_tr = build_xy(brain, video, vstim, train_stim)
            X_va, Y_va = build_xy(brain, video, vstim, val_stim)
            X_te, Y_te = build_xy(brain, video, vstim, test_stim)

            scX = StandardScaler().fit(X_tr)
            X_tr, X_va, X_te = scX.transform(X_tr), scX.transform(X_va), scX.transform(X_te)
            scY = StandardScaler().fit(Y_tr)
            Y_tr_n = scY.transform(Y_tr); Y_va_n = scY.transform(Y_va); Y_te_n = scY.transform(Y_te)

            best_val, best_alpha = -np.inf, None
            for alpha in RIDGE_ALPHAS:
                reg = Ridge(alpha=alpha)
                reg.fit(X_tr, Y_tr_n)
                pred_va = reg.predict(X_va)
                # Score val by mean Pearson r across video dims (recall un-standardized space ok)
                pred_va_orig = pred_va * scY.scale_ + scY.mean_
                m = evaluate(Y_va, pred_va_orig)["test_pearson_r_mean"]
                if m > best_val:
                    best_val, best_alpha = m, alpha
            reg = Ridge(alpha=best_alpha).fit(X_tr, Y_tr_n)
            pred_te = reg.predict(X_te) * scY.scale_ + scY.mean_
            res = evaluate(Y_te, pred_te)

            row = {
                "feature": f"Phase2_encoding_{args.video}",
                "task": "brain_to_video_encoding",
                "head": "ridge",
                "mode": "pooled",
                "subject": "pool",
                "fold": fold, "seed": seed,
                "n_train": X_tr.shape[0], "n_val": X_va.shape[0], "n_test": X_te.shape[0],
                "video_dim": Y_tr.shape[1],
                "brain_model": args.brain_model, "brain_init": args.brain_init,
                "brain_padding": args.brain_padding, "video": args.video,
                "best_alpha": best_alpha,
                "val_pearson_r_mean": best_val,
            }
            row.update(res)
            rows.append(row)
            print(f"  fold={fold} mean_r={res['test_pearson_r_mean']:.4f} (median={res['test_pearson_r_median']:.4f}) alpha={best_alpha}")

    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"\n[done] {len(rows)} rows → {out_csv}")


if __name__ == "__main__":
    main()
