"""
Brain-only Approach II — CLIP → brain distillation.

Train: BrainMLP supervised on V/A + KL distillation from frozen CLIP teacher logits.
Test: Brain only.

Teacher: CLIP linear probe (sklearn LogisticRegression) trained on train fold (per-fold).
Student: BrainMLP. Loss = alpha * CE(student, label) + (1-alpha) * T^2 * KL(student/T, teacher/T).

For regression: student MSE + alpha * mse(student_pred, teacher_pred).

Output: results/phase2/brain_only/II_distillation/<task>.csv
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, "/pscratch/sd/s/sjmoon/EmoBrain/project/dir2_multimodal/code/legacy_phase2")
sys.path.insert(0, "/pscratch/sd/s/sjmoon/EmoBrain/project/dir2_multimodal/code/legacy_phase2/brain_only")
from _lib import (TASKS, load_brain_embeddings, load_video_feature, load_task_labels,
                  get_fold_split, eval_metrics, val_score,
                  fit_standardizer, apply_standardizer,
                  DEFAULT_BRAIN, DEFAULT_BRAIN_INIT, DEFAULT_BRAIN_PAD, DEFAULT_VIDEO,
                  output_dim_for, compute_loss, predict_from_logits, is_multi_target)
from train_brain_supervised import BrainMLP, build_brain_data

OUT_DIR = Path("/pscratch/sd/s/sjmoon/EmoBrain/archive/v4_results/phase2/brain_only/II_distillation")

ALPHA_HARD = 0.5    # weight on hard label vs distillation
TEMP = 4.0          # distillation temperature


def build_teacher_predictions(brain_dict, video_feat, vstim, label_df, split_df,
                              task_type, label_cols="label"):
    """For each (subj, stim), get CLIP teacher prediction.
    - binary: shape (N,) probability of positive class
    - regression: shape (N,) value
    - multilabel: shape (N, 34) probability per cat
    - soft_dist: shape (N, 34) probability distribution
    """
    s2v = {int(s): i for i, s in enumerate(vstim)}
    is_multi = isinstance(label_cols, list)
    label_df = label_df.merge(split_df, on="stimulus_num", how="inner")
    per_split = {sp: [] for sp in ["train", "val", "test"]}
    for subj, (emb, stim_arr) in brain_dict.items():
        s2b = {int(s): i for i, s in enumerate(stim_arr)}
        for _, row in label_df.iterrows():
            stim, sp = int(row["stimulus_num"]), row["split"]
            if stim not in s2b or stim not in s2v: continue
            if is_multi:
                lab = np.asarray([row[c] for c in label_cols], dtype=np.float32)
            else:
                lab = row[label_cols]
            per_split[sp].append({"stim": stim, "video_idx": s2v[stim], "label": lab})

    def get_X(split):
        return np.stack([video_feat[r["video_idx"]] for r in per_split[split]])
    def get_y(split):
        ys = [r["label"] for r in per_split[split]]
        if is_multi:
            return np.stack(ys, axis=0).astype(np.float32)
        return np.asarray(ys, dtype=np.int64 if task_type == "binary" else np.float32)

    Xtr, ytr = get_X("train"), get_y("train")
    Xva, yva = get_X("val"),   get_y("val")
    Xte, yte = get_X("test"),  get_y("test")

    sc = StandardScaler().fit(Xtr)
    Xtr, Xva, Xte = sc.transform(Xtr), sc.transform(Xva), sc.transform(Xte)

    if task_type == "binary":
        from sklearn.metrics import roc_auc_score
        best_C, best_val = None, -np.inf
        for C in [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]:
            clf = LogisticRegression(C=C, max_iter=2000, random_state=0).fit(Xtr, ytr)
            vs = roc_auc_score(yva, clf.predict_proba(Xva)[:, 1])
            if vs > best_val: best_val, best_C = vs, C
        teacher = LogisticRegression(C=best_C, max_iter=2000, random_state=0).fit(Xtr, ytr)
        return {sp: teacher.predict_proba(X)[:, 1].astype(np.float32)
                for sp, X in [("train", Xtr), ("val", Xva), ("test", Xte)]}
    if task_type == "regression":
        from scipy.stats import pearsonr
        y_mean, y_std = ytr.mean(), ytr.std() + 1e-8
        best_alpha, best_val = None, -np.inf
        for alpha in [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]:
            reg = Ridge(alpha=alpha).fit(Xtr, (ytr - y_mean) / y_std)
            pred_v = reg.predict(Xva) * y_std + y_mean
            r, _ = pearsonr(yva, pred_v)
            if r > best_val: best_val, best_alpha = r, alpha
        teacher = Ridge(alpha=best_alpha).fit(Xtr, (ytr - y_mean) / y_std)
        return {sp: (teacher.predict(X) * y_std + y_mean).astype(np.float32)
                for sp, X in [("train", Xtr), ("val", Xva), ("test", Xte)]}
    if task_type == "multilabel":
        from sklearn.metrics import roc_auc_score
        from joblib import Parallel, delayed
        n_cat = ytr.shape[1]
        def _fit(C, d):
            yt = ytr[:, d].astype(int)
            if yt.sum() == 0 or yt.sum() == len(yt): return None
            return LogisticRegression(C=C, max_iter=500, class_weight="balanced",
                                      random_state=0, n_jobs=1).fit(Xtr, yt)
        best_C, best_val, best_models = None, -np.inf, None
        for C in [1e-2, 1.0, 100.0]:
            mods = Parallel(n_jobs=8, backend="threading")(delayed(_fit)(C, d) for d in range(n_cat))
            prob_va = np.zeros_like(yva)
            for d, m in enumerate(mods):
                prob_va[:, d] = ytr[:, d].mean() if m is None else m.predict_proba(Xva)[:, 1]
            aurocs = []
            for d in range(n_cat):
                yt = yva[:, d].astype(int)
                if yt.sum() == 0 or yt.sum() == len(yt): continue
                aurocs.append(roc_auc_score(yt, prob_va[:, d]))
            vs = float(np.mean(aurocs)) if aurocs else 0.0
            if vs > best_val: best_val, best_C, best_models = vs, C, mods
        out = {}
        for sp, X in [("train", Xtr), ("val", Xva), ("test", Xte)]:
            prob = np.zeros((X.shape[0], n_cat), dtype=np.float32)
            for d, m in enumerate(best_models):
                prob[:, d] = ytr[:, d].mean() if m is None else m.predict_proba(X)[:, 1]
            out[sp] = prob
        return out
    if task_type == "soft_dist":
        from sklearn.multioutput import MultiOutputRegressor
        from scipy.stats import pearsonr
        best_alpha, best_val, best_model = None, -np.inf, None
        for alpha in [1e-2, 1.0, 100.0]:
            reg = MultiOutputRegressor(Ridge(alpha=alpha, random_state=0), n_jobs=8).fit(Xtr, ytr)
            pred_va = reg.predict(Xva)
            pred_va = np.clip(pred_va, 0, None)
            pred_va = pred_va / np.clip(pred_va.sum(1, keepdims=True), 1e-8, None)
            rs = []
            for d in range(ytr.shape[1]):
                yt, yp = yva[:, d], pred_va[:, d]
                if yt.std() < 1e-8 or yp.std() < 1e-8: continue
                rs.append(pearsonr(yt, yp)[0])
            vs = float(np.mean(rs)) if rs else 0.0
            if vs > best_val: best_val, best_alpha, best_model = vs, alpha, reg
        out = {}
        for sp, X in [("train", Xtr), ("val", Xva), ("test", Xte)]:
            pred = best_model.predict(X)
            pred = np.clip(pred, 0, None)
            pred = pred / np.clip(pred.sum(1, keepdims=True), 1e-8, None)
            out[sp] = pred.astype(np.float32)
        return out
    raise ValueError(task_type)


def distill_loss(task_type, logits, teacher_target, temp=4.0):
    """Distillation loss given student logits and teacher target.
    - binary: teacher_target shape (B,) prob of positive. Use KL between student/T softmax
              and teacher_dist=[1-p, p].
    - regression: teacher_target shape (B,) standardized predicted value. Use MSE.
    - multilabel: teacher_target shape (B, K) prob per cat. Use BCE.
    - soft_dist: teacher_target shape (B, K) prob distribution. Use KL.
    """
    import torch
    import torch.nn.functional as F
    if task_type == "binary":
        student_log = F.log_softmax(logits / temp, dim=-1)
        teacher_dist = torch.stack([1.0 - teacher_target, teacher_target], dim=-1).clamp(1e-6, 1 - 1e-6)
        teacher_log = torch.log(teacher_dist)
        return F.kl_div(student_log, teacher_log, log_target=True, reduction="batchmean") * (temp ** 2)
    if task_type == "regression":
        return F.mse_loss(logits.squeeze(-1), teacher_target)
    if task_type == "multilabel":
        # Soft BCE: minimise BCE(student sigmoid, teacher prob)
        return F.binary_cross_entropy_with_logits(logits, teacher_target)
    if task_type == "soft_dist":
        return F.kl_div(F.log_softmax(logits, dim=-1), teacher_target, reduction="batchmean")
    raise ValueError(task_type)


def train_one_distill(brain_train, label_train, teacher_train,
                      brain_val, label_val,
                      brain_test, label_test,
                      task_type, n_out, seed, device,
                      lrs=(1e-4, 3e-4, 1e-3, 3e-3), epochs=60, batch_size=128,
                      patience=10, weight_decay=1e-4):
    torch.manual_seed(seed); np.random.seed(seed)
    b_mu, b_std = fit_standardizer(brain_train)
    b_tr = apply_standardizer(brain_train, b_mu, b_std)
    b_va = apply_standardizer(brain_val, b_mu, b_std)
    b_te = apply_standardizer(brain_test, b_mu, b_std)
    out_dim = output_dim_for(task_type, n_out)

    if task_type == "regression":
        y_mean = float(label_train.mean()); y_std = float(label_train.std() + 1e-8)
        lt = (label_train - y_mean) / y_std
        teacher_n = (teacher_train - y_mean) / y_std
    else:
        y_mean, y_std = 0.0, 1.0
        lt = label_train
        teacher_n = teacher_train

    # Tensor dtype per task
    if task_type == "binary":
        lt_t = torch.from_numpy(lt.astype(np.int64))
    else:
        lt_t = torch.from_numpy(lt.astype(np.float32))
    teacher_t = torch.from_numpy(teacher_n.astype(np.float32))

    tr_ds = TensorDataset(torch.from_numpy(b_tr), lt_t, teacher_t)
    tr_loader = DataLoader(tr_ds, batch_size=batch_size, shuffle=True)

    best_global = None
    for lr in lrs:
        torch.manual_seed(seed)
        model = BrainMLP(b_tr.shape[1], out_dim).to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
        best_val, best_state, since, diverged = -np.inf, None, 0, False
        for epoch in range(epochs):
            model.train()
            for bb, yy, tt in tr_loader:
                bb, yy, tt = bb.to(device), yy.to(device), tt.to(device)
                opt.zero_grad()
                logits = model(bb)
                loss_hard = compute_loss(task_type, logits, yy, y_mean, y_std)
                loss_distil = distill_loss(task_type, logits, tt, temp=TEMP)
                loss = ALPHA_HARD * loss_hard + (1 - ALPHA_HARD) * loss_distil
                if not torch.isfinite(loss): diverged = True; break
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
            if diverged: break
            model.eval()
            with torch.no_grad():
                logits_v = model(torch.from_numpy(b_va).to(device))
                if not torch.isfinite(logits_v).all(): diverged = True; break
                logits_v_np = logits_v.cpu().numpy()
                pred_v, prob_v = predict_from_logits(task_type, logits_v_np, y_mean, y_std)
                vs = val_score(task_type, label_val, pred_v, prob_v)
            if vs > best_val:
                best_val = vs
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
                since = 0
            else:
                since += 1
                if since >= patience: break
        if best_state is not None and (best_global is None or best_val > best_global[0]):
            best_global = (best_val, lr, best_state)

    if best_global is None:
        return {"test_main": float("nan"), "best_lr": "diverged", "best_val": float("nan")}
    _, best_lr, best_state = best_global
    model = BrainMLP(b_tr.shape[1], out_dim).to(device)
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        logits_t = model(torch.from_numpy(b_te).to(device)).cpu().numpy()
        pred_t, prob_t = predict_from_logits(task_type, logits_t, y_mean, y_std)
        res = eval_metrics(task_type, label_test, pred_t, prob_t)
    res["best_lr"] = best_lr
    res["best_val"] = best_global[0]
    return res


def main():
    ap = argparse.ArgumentParser()
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
    out_csv = args.out_csv or str(OUT_DIR / f"{args.task}.csv")
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"=== Brain-only II (distillation from {args.video}) task={args.task} ===")

    brain = load_brain_embeddings(args.brain_model, args.brain_init, args.brain_padding)
    video, vstim = load_video_feature(args.video)
    label_df, label_cols, ttype = load_task_labels(args.task)
    n_out = TASKS[args.task]["n_out"]

    rows = []
    for fold in folds:
        split = get_fold_split(fold)
        # Get teacher predictions (sklearn linear on CLIP, per-fold)
        teacher = build_teacher_predictions(brain, video, vstim, label_df, split, ttype, label_cols)
        # Brain data (parallel order)
        data = build_brain_data(brain, label_df, split, ttype, label_cols)
        # Sanity: brain count = teacher count
        for sp in ["train", "val", "test"]:
            assert data[sp]["brain"].shape[0] == teacher[sp].shape[0], \
                f"size mismatch {sp}: brain {data[sp]['brain'].shape[0]} vs teacher {teacher[sp].shape[0]}"
        for seed in seeds:
            t0 = time.time()
            res = train_one_distill(
                data["train"]["brain"], data["train"]["label"], teacher["train"],
                data["val"]["brain"],   data["val"]["label"],
                data["test"]["brain"],  data["test"]["label"],
                ttype, n_out, seed, device,
            )
            elapsed = time.time() - t0
            row = {
                "feature": "Phase2_BrainOnly_II_distillation",
                "method": "II_distillation", "teacher_video": args.video,
                "task": args.task, "task_type": ttype,
                "main_metric": TASKS[args.task]["main_metric"],
                "head": "mlp_distilled", "mode": "pooled", "subject": "pool",
                "fold": fold, "seed": seed,
                "n_train": data["train"]["brain"].shape[0],
                "n_val": data["val"]["brain"].shape[0],
                "n_test": data["test"]["brain"].shape[0],
                "brain_model": args.brain_model,
                "best_lr": res.pop("best_lr"),
                "val_main": res.pop("best_val"),
            }
            row.update(res)
            rows.append(row)
            print(f"  fold={fold} seed={seed} main={res['test_main']:.4f} t={elapsed:.1f}s")

    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"\n[done] {len(rows)} rows → {out_csv}")


if __name__ == "__main__":
    main()
