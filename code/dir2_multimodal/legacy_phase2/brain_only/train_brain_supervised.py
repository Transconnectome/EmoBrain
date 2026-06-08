"""
Brain-only Approach I — Supervised MLP head on frozen BJ.

Baseline beyond Phase 1 frozen linear probe: train a small MLP on BJ frozen features
with proper PyTorch trainer (AdamW + early stop). Tests whether a deeper head than
sklearn linear can extract more emotion signal from brain alone.

Comparison reference: Phase 1 frozen BJ linear V_binary = 0.74.

Output: results/phase2/brain_only/I_supervised/<task>.csv
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

sys.path.insert(0, "/pscratch/sd/s/sjmoon/FEELIN/code/dir2_multimodal/legacy_phase2")
from _lib import (TASKS, load_brain_embeddings, load_task_labels, get_fold_split,
                  eval_metrics, val_score, fit_standardizer, apply_standardizer,
                  DEFAULT_BRAIN, DEFAULT_BRAIN_INIT, DEFAULT_BRAIN_PAD,
                  output_dim_for, compute_loss, predict_from_logits, is_multi_target)

OUT_DIR = Path("/pscratch/sd/s/sjmoon/FEELIN/results/phase2/brain_only/I_supervised")


class BrainMLP(nn.Module):
    def __init__(self, brain_dim, out_dim, hidden=256, dropout=0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(brain_dim, hidden), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(hidden, hidden), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, brain):
        return self.net(brain)


def build_brain_data(brain_dict, label_df, split_df, task_type, label_cols="label"):
    """Pooled brain-only data. Supports both single-target (label_cols='label') and
    multi-target (label_cols=list of cat columns) tasks."""
    is_multi = isinstance(label_cols, list)
    label_df = label_df.merge(split_df, on="stimulus_num", how="inner")
    out = {sp: {"brain": [], "label": []} for sp in ["train", "val", "test"]}
    for subj, (emb, stim_arr) in brain_dict.items():
        s2b = {int(s): i for i, s in enumerate(stim_arr)}
        for _, row in label_df.iterrows():
            stim, sp = int(row["stimulus_num"]), row["split"]
            if stim not in s2b:
                continue
            out[sp]["brain"].append(emb[s2b[stim]])
            if is_multi:
                out[sp]["label"].append(np.asarray([row[c] for c in label_cols], dtype=np.float32))
            else:
                out[sp]["label"].append(row[label_cols])
    for sp in out:
        out[sp]["brain"] = np.stack(out[sp]["brain"]).astype(np.float32)
        if is_multi:
            out[sp]["label"] = np.stack(out[sp]["label"], axis=0).astype(np.float32)
        elif task_type == "binary":
            out[sp]["label"] = np.asarray(out[sp]["label"], dtype=np.int64)
        else:
            out[sp]["label"] = np.asarray(out[sp]["label"], dtype=np.float32)
    return out


def train_one(brain_train, label_train, brain_val, label_val, brain_test, label_test,
              task_type, n_out, seed, device,
              lrs=(1e-4, 3e-4, 1e-3, 3e-3), epochs=60, batch_size=128, patience=10,
              weight_decay=1e-4):
    torch.manual_seed(seed); np.random.seed(seed)
    b_mu, b_std = fit_standardizer(brain_train)
    b_tr = apply_standardizer(brain_train, b_mu, b_std)
    b_va = apply_standardizer(brain_val, b_mu, b_std)
    b_te = apply_standardizer(brain_test, b_mu, b_std)

    out_dim = output_dim_for(task_type, n_out)
    if task_type == "regression":
        y_mean = float(label_train.mean()); y_std = float(label_train.std() + 1e-8)
        lt = (label_train - y_mean) / y_std
    else:
        y_mean, y_std = 0.0, 1.0
        lt = label_train

    # Convert label dtype per task type for tensor packing.
    if task_type == "binary":
        lt_t = torch.from_numpy(lt.astype(np.int64))
    else:
        lt_t = torch.from_numpy(lt.astype(np.float32))
    tr_ds = TensorDataset(torch.from_numpy(b_tr), lt_t)
    tr_loader = DataLoader(tr_ds, batch_size=batch_size, shuffle=True)

    best_global = None
    for lr in lrs:
        torch.manual_seed(seed)
        model = BrainMLP(b_tr.shape[1], out_dim).to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
        best_val, best_state, since, diverged = -np.inf, None, 0, False
        for epoch in range(epochs):
            model.train()
            for bb, yy in tr_loader:
                bb, yy = bb.to(device), yy.to(device)
                opt.zero_grad()
                logits = model(bb)
                loss = compute_loss(task_type, logits, yy, y_mean, y_std)
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
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--folds", default="1,2,3,4,5")
    ap.add_argument("--out_csv", default=None)
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    folds = [int(f) for f in args.folds.split(",")]
    out_csv = args.out_csv or str(OUT_DIR / f"{args.task}.csv")
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"=== Brain-only I (supervised MLP) task={args.task} ===")

    brain = load_brain_embeddings(args.brain_model, args.brain_init, args.brain_padding)
    label_df, label_cols, ttype = load_task_labels(args.task)
    n_out = TASKS[args.task]["n_out"]

    rows = []
    for fold in folds:
        split = get_fold_split(fold)
        data = build_brain_data(brain, label_df, split, ttype, label_cols)
        for seed in seeds:
            t0 = time.time()
            res = train_one(
                data["train"]["brain"], data["train"]["label"],
                data["val"]["brain"],   data["val"]["label"],
                data["test"]["brain"],  data["test"]["label"],
                ttype, n_out, seed, device,
            )
            elapsed = time.time() - t0
            row = {
                "feature": "Phase2_BrainOnly_I_supervised",
                "method": "I_supervised",
                "task": args.task, "task_type": ttype,
                "main_metric": TASKS[args.task]["main_metric"],
                "head": "mlp_trained", "mode": "pooled", "subject": "pool",
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
