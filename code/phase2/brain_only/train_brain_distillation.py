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

sys.path.insert(0, "/pscratch/sd/s/sjmoon/FEELIN/code/phase2")
sys.path.insert(0, "/pscratch/sd/s/sjmoon/FEELIN/code/phase2/brain_only")
from _lib import (TASKS, load_brain_embeddings, load_video_feature, load_task_labels,
                  get_fold_split, eval_metrics, val_score,
                  fit_standardizer, apply_standardizer,
                  DEFAULT_BRAIN, DEFAULT_BRAIN_INIT, DEFAULT_BRAIN_PAD, DEFAULT_VIDEO)
from train_brain_supervised import BrainMLP, build_brain_data

OUT_DIR = Path("/pscratch/sd/s/sjmoon/FEELIN/results/phase2/brain_only/II_distillation")

ALPHA_HARD = 0.5    # weight on hard label vs distillation
TEMP = 4.0          # distillation temperature


def build_teacher_predictions(brain_dict, video_feat, vstim, label_df, split_df,
                              task_type):
    """For each (subj, stim), get CLIP linear-probe teacher prediction (probability or value).

    Teacher = sklearn LogisticRegression / Ridge trained on train fold's video features.
    Returns dict {split: teacher_pred (N,)}. teacher_pred is prob (binary) or value (regression).
    """
    s2v = {int(s): i for i, s in enumerate(vstim)}
    # Build per-split (subject, stim) tuples preserving order
    label_df = label_df.merge(split_df, on="stimulus_num", how="inner")
    per_split = {sp: [] for sp in ["train", "val", "test"]}
    for subj, (emb, stim_arr) in brain_dict.items():
        s2b = {int(s): i for i, s in enumerate(stim_arr)}
        for _, row in label_df.iterrows():
            stim, sp = int(row["stimulus_num"]), row["split"]
            if stim not in s2b or stim not in s2v: continue
            per_split[sp].append({"stim": stim, "subj": subj, "video_idx": s2v[stim],
                                  "label": row["label"]})

    # CLIP video features for each row
    def get_X(split):
        return np.stack([video_feat[r["video_idx"]] for r in per_split[split]])
    def get_y(split):
        return np.asarray([r["label"] for r in per_split[split]],
                          dtype=np.int64 if task_type == "binary" else np.float32)

    Xtr, ytr = get_X("train"), get_y("train")
    Xva, yva = get_X("val"),   get_y("val")
    Xte, yte = get_X("test"),  get_y("test")

    sc = StandardScaler().fit(Xtr)
    Xtr, Xva, Xte = sc.transform(Xtr), sc.transform(Xva), sc.transform(Xte)

    if task_type == "binary":
        # Train teacher; pick C via val AUROC
        from sklearn.metrics import roc_auc_score
        best_C, best_val = None, -np.inf
        for C in [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]:
            clf = LogisticRegression(C=C, max_iter=2000, random_state=0).fit(Xtr, ytr)
            vs = roc_auc_score(yva, clf.predict_proba(Xva)[:, 1])
            if vs > best_val:
                best_val, best_C = vs, C
        teacher = LogisticRegression(C=best_C, max_iter=2000, random_state=0).fit(Xtr, ytr)
        return {
            "train": teacher.predict_proba(Xtr)[:, 1].astype(np.float32),
            "val":   teacher.predict_proba(Xva)[:, 1].astype(np.float32),
            "test":  teacher.predict_proba(Xte)[:, 1].astype(np.float32),
        }
    else:
        from scipy.stats import pearsonr
        y_mean, y_std = ytr.mean(), ytr.std() + 1e-8
        best_alpha, best_val = None, -np.inf
        for alpha in [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]:
            reg = Ridge(alpha=alpha).fit(Xtr, (ytr - y_mean) / y_std)
            pred_v = reg.predict(Xva) * y_std + y_mean
            r, _ = pearsonr(yva, pred_v)
            if r > best_val: best_val, best_alpha = r, alpha
        teacher = Ridge(alpha=best_alpha).fit(Xtr, (ytr - y_mean) / y_std)
        return {
            "train": (teacher.predict(Xtr) * y_std + y_mean).astype(np.float32),
            "val":   (teacher.predict(Xva) * y_std + y_mean).astype(np.float32),
            "test":  (teacher.predict(Xte) * y_std + y_mean).astype(np.float32),
        }


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
    if task_type == "regression":
        y_mean = float(label_train.mean()); y_std = float(label_train.std() + 1e-8)
        lt = (label_train - y_mean) / y_std
        teacher_n = (teacher_train - y_mean) / y_std
    else:
        y_mean, y_std = 0.0, 1.0
        lt = label_train
        teacher_n = teacher_train

    tr_ds = TensorDataset(torch.from_numpy(b_tr), torch.from_numpy(lt),
                          torch.from_numpy(teacher_n))
    tr_loader = DataLoader(tr_ds, batch_size=batch_size, shuffle=True)

    best_global = None
    for lr in lrs:
        torch.manual_seed(seed)
        model = BrainMLP(b_tr.shape[1], n_out, task_type).to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
        best_val, best_state, since, diverged = -np.inf, None, 0, False
        for epoch in range(epochs):
            model.train()
            for bb, yy, tt in tr_loader:
                bb, yy, tt = bb.to(device), yy.to(device), tt.to(device)
                opt.zero_grad()
                logits = model(bb)
                if task_type == "binary":
                    loss_hard = F.cross_entropy(logits, yy)
                    # teacher soft prob → distill via KL on softmax(logits/T)
                    student_log = F.log_softmax(logits / TEMP, dim=-1)
                    teacher_dist = torch.stack([1.0 - tt, tt], dim=-1).clamp(1e-6, 1 - 1e-6)
                    teacher_log = torch.log(teacher_dist)
                    loss_distill = F.kl_div(student_log, teacher_log, log_target=True,
                                            reduction="batchmean") * (TEMP ** 2)
                    loss = ALPHA_HARD * loss_hard + (1 - ALPHA_HARD) * loss_distill
                else:
                    pred_n = logits.squeeze(-1)
                    loss_hard = F.mse_loss(pred_n, yy)
                    loss_distill = F.mse_loss(pred_n, tt)
                    loss = ALPHA_HARD * loss_hard + (1 - ALPHA_HARD) * loss_distill
                if not torch.isfinite(loss): diverged = True; break
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
            if diverged: break
            model.eval()
            with torch.no_grad():
                logits_v = model(torch.from_numpy(b_va).to(device))
                if not torch.isfinite(logits_v).all(): diverged = True; break
                if task_type == "binary":
                    prob = F.softmax(logits_v, -1)[:, 1].cpu().numpy()
                    pred = logits_v.argmax(-1).cpu().numpy()
                    vs = val_score(task_type, label_val, pred, prob)
                else:
                    pred = logits_v.squeeze(-1).cpu().numpy() * y_std + y_mean
                    vs = val_score(task_type, label_val, pred)
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
    model = BrainMLP(b_tr.shape[1], n_out, task_type).to(device)
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        logits_t = model(torch.from_numpy(b_te).to(device))
        if task_type == "binary":
            prob = F.softmax(logits_t, -1)[:, 1].cpu().numpy()
            pred = logits_t.argmax(-1).cpu().numpy()
            res = eval_metrics(task_type, label_test, pred, prob)
        else:
            pred = logits_t.squeeze(-1).cpu().numpy() * y_std + y_mean
            res = eval_metrics(task_type, label_test, pred)
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
    label_df, ttype = load_task_labels(args.task)
    n_out = TASKS[args.task]["n_out"]

    rows = []
    for fold in folds:
        split = get_fold_split(fold)
        # Get teacher predictions (sklearn linear on CLIP, per-fold)
        teacher = build_teacher_predictions(brain, video, vstim, label_df, split, ttype)
        # Brain data (parallel order)
        data = build_brain_data(brain, label_df, split, ttype)
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
