"""
Phase 2 supervised trainer for architectures D / A / B.

Loads frozen brain BFM + frozen video features, builds 5-fold split, trains a small
fusion head on a single (V/A) task with proper val-set HP selection.

D = late fusion (linear concat, deterministic): 1 seed
A = token transformer (stochastic): 3 seeds
B = cross-attention (stochastic): 3 seeds

Output: results/phase2/<arch>/<task>.csv  per-fold per-seed rows in Phase 1 schema.
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

sys.path.insert(0, "/pscratch/sd/s/sjmoon/FEELIN/project/dir2_multimodal/code/legacy_phase2")
sys.path.insert(0, "/pscratch/sd/s/sjmoon/FEELIN/project/dir2_multimodal/code/legacy_phase2/architectures")

from _lib import (TASKS, load_brain_embeddings, load_video_feature, load_task_labels,
                  get_fold_split, build_pooled_data, eval_metrics, val_score,
                  fit_standardizer, apply_standardizer,
                  DEFAULT_BRAIN, DEFAULT_BRAIN_INIT, DEFAULT_BRAIN_PAD, DEFAULT_VIDEO,
                  output_dim_for, compute_loss, predict_from_logits, is_multi_target)

from arch_D_late_fusion import LateFusion
from arch_A_token_transformer import TokenTransformer
from arch_B_cross_attention import CrossAttention

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
OUT_DIR = FEELIN / "project/shared/results/phase2"

ARCHS = {"D": LateFusion, "A": TokenTransformer, "B": CrossAttention}

LR_GRID = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
DEFAULT_EPOCHS = 50
PATIENCE = 8


def train_one_run(arch_cls, brain_train, video_train, label_train,
                  brain_val, video_val, label_val,
                  brain_test, video_test, label_test,
                  task_type, n_out, seed, device, lr=None,
                  epochs=DEFAULT_EPOCHS, batch_size=128, weight_decay=1e-4):
    torch.manual_seed(seed)
    np.random.seed(seed)

    out_dim = output_dim_for(task_type, n_out)

    # Standardize features (fit on train only)
    b_mu, b_std = fit_standardizer(brain_train)
    v_mu, v_std = fit_standardizer(video_train)
    b_tr = apply_standardizer(brain_train, b_mu, b_std)
    v_tr = apply_standardizer(video_train, v_mu, v_std)
    b_va = apply_standardizer(brain_val, b_mu, b_std)
    v_va = apply_standardizer(video_val, v_mu, v_std)
    b_te = apply_standardizer(brain_test, b_mu, b_std)
    v_te = apply_standardizer(video_test, v_mu, v_std)

    # Standardize regression label
    y_mean, y_std = 0.0, 1.0
    if task_type == "regression":
        y_mean = float(label_train.mean())
        y_std = float(label_train.std() + 1e-8)
        lt = (label_train - y_mean) / y_std
    else:
        lt = label_train

    if task_type == "binary":
        lt_t = torch.from_numpy(lt.astype(np.int64))
    else:
        lt_t = torch.from_numpy(lt.astype(np.float32))

    tr_ds = TensorDataset(torch.from_numpy(b_tr), torch.from_numpy(v_tr), lt_t)
    tr_loader = DataLoader(tr_ds, batch_size=batch_size, shuffle=True, drop_last=False)

    # HP search if lr is None
    lr_options = LR_GRID if lr is None else [lr]

    best_global = None
    for trial_lr in lr_options:
        torch.manual_seed(seed)
        model = arch_cls(brain_dim=brain_train.shape[1], video_dim=video_train.shape[1],
                         out_dim=out_dim).to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=trial_lr, weight_decay=weight_decay)
        best_val, best_state, since = -np.inf, None, 0
        diverged = False
        for epoch in range(epochs):
            model.train()
            for bb, vv, yy in tr_loader:
                bb, vv, yy = bb.to(device), vv.to(device), yy.to(device)
                opt.zero_grad()
                logits = model(bb, vv)
                loss = compute_loss(task_type, logits, yy, y_mean, y_std)
                if not torch.isfinite(loss):
                    diverged = True
                    break
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                opt.step()
            if diverged:
                break
            model.eval()
            with torch.no_grad():
                logits_v = model(torch.from_numpy(b_va).to(device),
                                  torch.from_numpy(v_va).to(device))
                if not torch.isfinite(logits_v).all():
                    diverged = True
                    break
                logits_v_np = logits_v.cpu().numpy()
                pred_v, prob_v = predict_from_logits(task_type, logits_v_np, y_mean, y_std)
                vs = val_score(task_type, label_val, pred_v, prob_v)
            if vs > best_val:
                best_val = vs
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
                since = 0
            else:
                since += 1
                if since >= PATIENCE:
                    break
        if diverged or best_state is None:
            continue
        if best_state is not None and (best_global is None or best_val > best_global[0]):
            best_global = (best_val, trial_lr, best_state)

    if best_global is None:
        return {"test_main": float("nan"), "best_lr": "diverged", "best_val": float("nan")}
    _, best_lr, best_state = best_global
    final_model = arch_cls(brain_dim=brain_train.shape[1], video_dim=video_train.shape[1],
                           out_dim=out_dim).to(device)
    final_model.load_state_dict(best_state)
    final_model.eval()
    with torch.no_grad():
        logits_t = final_model(torch.from_numpy(b_te).to(device),
                                torch.from_numpy(v_te).to(device)).cpu().numpy()
        pred_t, prob_t = predict_from_logits(task_type, logits_t, y_mean, y_std)
        res = eval_metrics(task_type, label_test, pred_t, prob_t)
    res["best_lr"] = best_lr
    res["best_val"] = best_global[0]
    return res


def train_one_run_sklearn(brain_train, video_train, label_train,
                          brain_val, video_val, label_val,
                          brain_test, video_test, label_test,
                          task_type, seed):
    """Sklearn-based linear probe for Architecture D (concat + linear).
    Matches Phase 1 frozen probe convention (LogisticRegression / Ridge with HP search).
    """
    from sklearn.linear_model import Ridge, LogisticRegression
    from sklearn.preprocessing import StandardScaler

    Xtr = np.concatenate([brain_train, video_train], axis=-1)
    Xva = np.concatenate([brain_val, video_val], axis=-1)
    Xte = np.concatenate([brain_test, video_test], axis=-1)
    sc = StandardScaler().fit(Xtr)
    Xtr, Xva, Xte = sc.transform(Xtr), sc.transform(Xva), sc.transform(Xte)

    LINEAR_CS = [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]
    RIDGE_ALPHAS = [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]

    best_val, best_hp = -np.inf, None
    best_pred, best_prob = None, None
    if task_type == "binary":
        for C in LINEAR_CS:
            clf = LogisticRegression(C=C, max_iter=2000, random_state=seed)
            clf.fit(Xtr, label_train)
            prob_v = clf.predict_proba(Xva)[:, 1]
            pred_v = clf.predict(Xva)
            vs = val_score(task_type, label_val, pred_v, prob_v)
            if vs > best_val:
                best_val, best_hp = vs, C
                clf_te = LogisticRegression(C=C, max_iter=2000, random_state=seed).fit(Xtr, label_train)
                best_prob = clf_te.predict_proba(Xte)[:, 1]
                best_pred = clf_te.predict(Xte)
        res = eval_metrics(task_type, label_test, best_pred, best_prob)
        res["best_lr"] = f"C={best_hp}"
    elif task_type == "regression":
        y_mean, y_std = label_train.mean(), label_train.std() + 1e-8
        ytr_n = (label_train - y_mean) / y_std
        for alpha in RIDGE_ALPHAS:
            reg = Ridge(alpha=alpha).fit(Xtr, ytr_n)
            pred_v = reg.predict(Xva) * y_std + y_mean
            vs = val_score(task_type, label_val, pred_v)
            if vs > best_val:
                best_val, best_hp = vs, alpha
                reg_te = Ridge(alpha=alpha).fit(Xtr, ytr_n)
                best_pred = reg_te.predict(Xte) * y_std + y_mean
        res = eval_metrics(task_type, label_test, best_pred)
        res["best_lr"] = f"alpha={best_hp}"
    elif task_type == "multilabel":
        from joblib import Parallel, delayed
        ytr_i = label_train.astype(int)
        yva_i = label_val.astype(int)
        yte_i = label_test.astype(int)
        n_cat = ytr_i.shape[1]
        def _fit(C, d):
            yt = ytr_i[:, d]
            if yt.sum() == 0 or yt.sum() == len(yt): return None
            return LogisticRegression(C=C, max_iter=500, class_weight="balanced",
                                      random_state=seed, n_jobs=1).fit(Xtr, yt)
        best_models = None
        for C in [1e-2, 1.0, 100.0]:
            mods = Parallel(n_jobs=8, backend="threading")(delayed(_fit)(C, d) for d in range(n_cat))
            prob_va = np.zeros_like(label_val, dtype=float)
            for d, m in enumerate(mods):
                prob_va[:, d] = ytr_i[:, d].mean() if m is None else m.predict_proba(Xva)[:, 1]
            vs = val_score(task_type, yva_i, (prob_va >= 0.5).astype(int), prob_va)
            if vs > best_val:
                best_val, best_hp = vs, C; best_models = mods
        prob_te = np.zeros_like(label_test, dtype=float)
        for d, m in enumerate(best_models):
            prob_te[:, d] = ytr_i[:, d].mean() if m is None else m.predict_proba(Xte)[:, 1]
        best_pred = (prob_te >= 0.5).astype(int); best_prob = prob_te
        res = eval_metrics(task_type, yte_i, best_pred, best_prob)
        res["best_lr"] = f"C={best_hp}"
    elif task_type == "soft_dist":
        from sklearn.multioutput import MultiOutputRegressor
        for alpha in RIDGE_ALPHAS:
            reg = MultiOutputRegressor(Ridge(alpha=alpha, random_state=seed), n_jobs=8).fit(Xtr, label_train)
            pred_va = reg.predict(Xva)
            pred_va = np.clip(pred_va, 0, None)
            pred_va = pred_va / np.clip(pred_va.sum(1, keepdims=True), 1e-8, None)
            vs = val_score(task_type, label_val, pred_va)
            if vs > best_val:
                best_val, best_hp = vs, alpha
                pred_te = reg.predict(Xte)
                pred_te = np.clip(pred_te, 0, None)
                pred_te = pred_te / np.clip(pred_te.sum(1, keepdims=True), 1e-8, None)
                best_pred = pred_te
        res = eval_metrics(task_type, label_test, best_pred)
        res["best_lr"] = f"alpha={best_hp}"
    else:
        raise ValueError(task_type)
    res["best_val"] = best_val
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", required=True, choices=["D", "A", "B"])
    ap.add_argument("--task", required=True, choices=list(TASKS.keys()))
    ap.add_argument("--brain_model", default=DEFAULT_BRAIN)
    ap.add_argument("--brain_init", default=DEFAULT_BRAIN_INIT)
    ap.add_argument("--brain_padding", default=DEFAULT_BRAIN_PAD)
    ap.add_argument("--video", default=DEFAULT_VIDEO)
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--folds", default="1,2,3,4,5")
    ap.add_argument("--out_csv", default=None)
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    folds = [int(f) for f in args.folds.split(",")]
    # D is deterministic — single seed
    if args.arch == "D":
        seeds = [seeds[0]]

    out_csv = args.out_csv
    if out_csv is None:
        out_csv = str(OUT_DIR / args.arch / f"{args.task}.csv")
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"=== Phase 2 supervised training ===")
    print(f"  arch={args.arch} task={args.task} brain={args.brain_model}/{args.brain_init}/"
          f"{args.brain_padding} video={args.video} seeds={seeds} folds={folds} device={device}")

    # Load once
    t0 = time.time()
    brain = load_brain_embeddings(args.brain_model, args.brain_init, args.brain_padding)
    video, vstim = load_video_feature(args.video)
    label_df, label_cols, ttype = load_task_labels(args.task)
    n_out = TASKS[args.task]["n_out"]
    print(f"  load t={time.time()-t0:.1f}s | brain D={list(brain.values())[0][0].shape[1]} "
          f"video D={video.shape[1]} task_type={ttype}")

    arch_cls = ARCHS[args.arch]
    rows = []
    for fold in folds:
        split = get_fold_split(fold)
        data = build_pooled_data(brain, video, vstim, label_df, split, ttype, label_cols)
        for seed in seeds:
            t1 = time.time()
            if args.arch == "D":
                # Use sklearn-based linear probe for fair comparison with Phase 1 frozen probe
                res = train_one_run_sklearn(
                    data["train"]["brain"], data["train"]["video"], data["train"]["label"],
                    data["val"]["brain"],   data["val"]["video"],   data["val"]["label"],
                    data["test"]["brain"],  data["test"]["video"],  data["test"]["label"],
                    ttype, seed,
                )
            else:
                res = train_one_run(
                    arch_cls,
                    data["train"]["brain"], data["train"]["video"], data["train"]["label"],
                    data["val"]["brain"],   data["val"]["video"],   data["val"]["label"],
                    data["test"]["brain"],  data["test"]["video"],  data["test"]["label"],
                    ttype, n_out, seed, device,
                )
            elapsed = time.time() - t1
            row = {
                "feature": f"Phase2_{args.arch}",
                "dir_prefix": "n/a",
                "padding": "n/a",
                "init": "n/a",
                "task": args.task,
                "task_type": ttype,
                "main_metric": TASKS[args.task]["main_metric"],
                "head": "trained",
                "mode": "pooled",
                "subject": "pool",
                "fold": fold,
                "seed": seed,
                "n_train": data["train"]["brain"].shape[0],
                "n_val": data["val"]["brain"].shape[0],
                "n_test": data["test"]["brain"].shape[0],
                "brain_model": args.brain_model,
                "brain_init": args.brain_init,
                "brain_padding": args.brain_padding,
                "video": args.video,
                "best_lr": res.pop("best_lr"),
                "val_main": res.pop("best_val"),
            }
            row.update(res)
            rows.append(row)
            print(f"  [arch={args.arch} task={args.task} fold={fold} seed={seed}] "
                  f"main={res['test_main']:.4f} hp={row['best_lr']} t={elapsed:.1f}s")

    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"\n[done] wrote {len(df)} rows to {out_csv}")


if __name__ == "__main__":
    main()
