"""
Phase 2 Architecture C — Stage 2: linear V/A probe on contrastive-aligned features.

Loads aligner from train_contrastive.py output, produces (brain_proj, video_proj) for all
samples, then fits a Phase 1-style ridge/logistic linear probe on
  (i)  brain_proj only
  (ii) concat(brain_proj, video_proj)

Output: results/phase2/C/probe_<input>_<task>.csv  per fold per seed rows in Phase 1 schema.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, "/pscratch/sd/s/sjmoon/FEELIN/project/dir2_multimodal/code/legacy_phase2")
sys.path.insert(0, "/pscratch/sd/s/sjmoon/FEELIN/project/dir2_multimodal/code/legacy_phase2/architectures")

from _lib import (TASKS, load_brain_embeddings, load_video_feature, load_task_labels,
                  get_fold_split, build_pooled_data, eval_metrics, val_score,
                  fit_standardizer, apply_standardizer,
                  DEFAULT_BRAIN, DEFAULT_BRAIN_INIT, DEFAULT_BRAIN_PAD, DEFAULT_VIDEO)
from arch_C_contrastive import ContrastiveAligner

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
ALIGNER_DIR = FEELIN / "project/shared/results/phase2/C"
OUT_DIR = FEELIN / "project/shared/results/phase2/C"

LINEAR_CS = [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]
RIDGE_ALPHAS = [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]


def project_features(aligner_ckpt, brain_raw, video_raw, device):
    """Pass raw (un-standardized) features through aligner's standardizer + projection.
    Returns (brain_proj_np, video_proj_np)."""
    state = aligner_ckpt["state_dict"]
    b_mu, b_std, v_mu, v_std = aligner_ckpt["standardizer"]
    model = ContrastiveAligner(brain_dim=brain_raw.shape[1], video_dim=video_raw.shape[1],
                               d_model=256, temperature=0.07).to(device)
    model.load_state_dict(state)
    model.eval()
    b_in = (brain_raw - b_mu) / b_std
    v_in = (video_raw - v_mu) / v_std
    with torch.no_grad():
        zb = model.encode_brain(torch.from_numpy(b_in.astype(np.float32)).to(device)).cpu().numpy()
        zv = model.encode_video(torch.from_numpy(v_in.astype(np.float32)).to(device)).cpu().numpy()
    return zb, zv


def linear_probe(data, task_type, seed):
    """Phase 1-style ridge / logistic with HP search on val fold.
    Supports binary, regression, multilabel, soft_dist."""
    Xtr, ytr = data["train"]["X"], data["train"]["label"]
    Xva, yva = data["val"]["X"],   data["val"]["label"]
    Xte, yte = data["test"]["X"],  data["test"]["label"]

    sc = StandardScaler().fit(Xtr)
    Xtr, Xva, Xte = sc.transform(Xtr), sc.transform(Xva), sc.transform(Xte)

    best_val, best_pred, best_prob = -np.inf, None, None
    best_hp = None
    if task_type == "binary":
        for C in LINEAR_CS:
            clf = LogisticRegression(C=C, max_iter=2000, random_state=seed)
            clf.fit(Xtr, ytr)
            prob_v = clf.predict_proba(Xva)[:, 1]
            pred_v = clf.predict(Xva)
            vs = val_score(task_type, yva, pred_v, prob_v)
            if vs > best_val:
                best_val = vs; best_hp = C
                clf_te = LogisticRegression(C=C, max_iter=2000, random_state=seed).fit(Xtr, ytr)
                best_prob = clf_te.predict_proba(Xte)[:, 1]
                best_pred = clf_te.predict(Xte)
        res = eval_metrics(task_type, yte, best_pred, best_prob)
        res["best_hp"] = f"C={best_hp}"
    elif task_type == "regression":
        y_mean = ytr.mean(); y_std = ytr.std() + 1e-8
        ytr_n = (ytr - y_mean) / y_std
        for alpha in RIDGE_ALPHAS:
            reg = Ridge(alpha=alpha)
            reg.fit(Xtr, ytr_n)
            pred_v = reg.predict(Xva) * y_std + y_mean
            vs = val_score(task_type, yva, pred_v)
            if vs > best_val:
                best_val = vs; best_hp = alpha
                reg_te = Ridge(alpha=alpha).fit(Xtr, ytr_n)
                best_pred = reg_te.predict(Xte) * y_std + y_mean
        res = eval_metrics(task_type, yte, best_pred)
        res["best_hp"] = f"alpha={best_hp}"
    elif task_type == "multilabel":
        from joblib import Parallel, delayed
        ytr_i = ytr.astype(int)
        yva_i = yva.astype(int)
        yte_i = yte.astype(int)
        n_cat = ytr.shape[1]
        def _fit(C, d):
            yt = ytr_i[:, d]
            if yt.sum() == 0 or yt.sum() == len(yt): return None
            return LogisticRegression(C=C, max_iter=500, class_weight="balanced",
                                      random_state=seed, n_jobs=1).fit(Xtr, yt)
        best_models = None
        for C in [1e-2, 1.0, 100.0]:
            mods = Parallel(n_jobs=8, backend="threading")(delayed(_fit)(C, d) for d in range(n_cat))
            prob_va = np.zeros_like(yva, dtype=float)
            for d, m in enumerate(mods):
                prob_va[:, d] = ytr_i[:, d].mean() if m is None else m.predict_proba(Xva)[:, 1]
            vs = val_score(task_type, yva_i, (prob_va >= 0.5).astype(int), prob_va)
            if vs > best_val:
                best_val = vs; best_hp = C; best_models = mods
        prob_te = np.zeros_like(yte, dtype=float)
        for d, m in enumerate(best_models):
            prob_te[:, d] = ytr_i[:, d].mean() if m is None else m.predict_proba(Xte)[:, 1]
        best_pred = (prob_te >= 0.5).astype(int); best_prob = prob_te
        res = eval_metrics(task_type, yte_i, best_pred, best_prob)
        res["best_hp"] = f"C={best_hp}"
    elif task_type == "soft_dist":
        from sklearn.multioutput import MultiOutputRegressor
        for alpha in RIDGE_ALPHAS:
            reg = MultiOutputRegressor(Ridge(alpha=alpha, random_state=seed), n_jobs=8).fit(Xtr, ytr)
            pred_va = reg.predict(Xva)
            pred_va = np.clip(pred_va, 0, None)
            pred_va = pred_va / np.clip(pred_va.sum(1, keepdims=True), 1e-8, None)
            vs = val_score(task_type, yva, pred_va)
            if vs > best_val:
                best_val = vs; best_hp = alpha
                pred_te = reg.predict(Xte)
                pred_te = np.clip(pred_te, 0, None)
                pred_te = pred_te / np.clip(pred_te.sum(1, keepdims=True), 1e-8, None)
                best_pred = pred_te
        res = eval_metrics(task_type, yte, best_pred)
        res["best_hp"] = f"alpha={best_hp}"
    else:
        raise ValueError(task_type)
    res["val_main"] = best_val
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=list(TASKS.keys()))
    ap.add_argument("--probe_input", required=True, choices=["brain_only", "joint"],
                    help="brain_only = brain_proj only, joint = concat(brain_proj, video_proj)")
    ap.add_argument("--brain_model", default=DEFAULT_BRAIN)
    ap.add_argument("--brain_init", default=DEFAULT_BRAIN_INIT)
    ap.add_argument("--brain_padding", default=DEFAULT_BRAIN_PAD)
    ap.add_argument("--video", default=DEFAULT_VIDEO)
    ap.add_argument("--seeds", default="0,1,2", help="aligner seeds to use")
    ap.add_argument("--folds", default="1,2,3,4,5")
    ap.add_argument("--aligner_dir", default=str(ALIGNER_DIR))
    ap.add_argument("--out_csv", default=None)
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    folds = [int(f) for f in args.folds.split(",")]
    out_csv = args.out_csv or str(OUT_DIR / f"probe_{args.probe_input}_{args.task}.csv")
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print(f"=== Phase 2 C probe ===")
    print(f"  task={args.task} probe_input={args.probe_input} seeds={seeds} folds={folds}")

    brain = load_brain_embeddings(args.brain_model, args.brain_init, args.brain_padding)
    video, vstim = load_video_feature(args.video)
    label_df, label_cols, ttype = load_task_labels(args.task)

    rows = []
    for fold in folds:
        split = get_fold_split(fold)
        # Reuse the same build_pooled_data, then project per row
        data_raw = build_pooled_data(brain, video, vstim, label_df, split, ttype, label_cols)
        for seed in seeds:
            ckpt_path = Path(args.aligner_dir) / f"aligner_fold{fold}_seed{seed}.pt"
            if not ckpt_path.exists():
                print(f"  [skip] aligner ckpt missing: {ckpt_path.name}")
                continue
            ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
            # Project all splits with the same aligner
            data_proj = {}
            for sp in ["train", "val", "test"]:
                zb, zv = project_features(ckpt, data_raw[sp]["brain"], data_raw[sp]["video"], device)
                if args.probe_input == "brain_only":
                    X = zb
                else:
                    X = np.concatenate([zb, zv], axis=-1)
                data_proj[sp] = {"X": X, "label": data_raw[sp]["label"]}
            res = linear_probe(data_proj, ttype, seed)
            row = {
                "feature": f"Phase2_C_{args.probe_input}",
                "dir_prefix": "n/a",
                "padding": "n/a",
                "init": "n/a",
                "task": args.task,
                "task_type": ttype,
                "main_metric": TASKS[args.task]["main_metric"],
                "head": "linear",
                "mode": "pooled",
                "subject": "pool",
                "fold": fold,
                "seed": seed,
                "n_train": data_raw["train"]["brain"].shape[0],
                "n_val": data_raw["val"]["brain"].shape[0],
                "n_test": data_raw["test"]["brain"].shape[0],
                "brain_model": args.brain_model, "brain_init": args.brain_init,
                "brain_padding": args.brain_padding, "video": args.video,
                "best_hp": res.pop("best_hp"),
                "val_main": res.pop("val_main"),
            }
            row.update(res)
            rows.append(row)
            print(f"  fold={fold} seed={seed} main={res['test_main']:.4f} hp={row['best_hp']}")

    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"\n[done] {len(rows)} rows → {out_csv}")


if __name__ == "__main__":
    main()
