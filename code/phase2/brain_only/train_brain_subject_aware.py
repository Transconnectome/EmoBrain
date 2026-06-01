"""
Brain-only Approach IV — Subject-aware brain MLP.

Train: BrainMLP that takes brain feature + subject embedding (5-way).
       Subject embedding learned (16-dim) and concatenated with brain feature.
Test: Brain + subject ID (known at test time).

Hypothesis: 5 subj 의 brain response 분포가 다른 점을 명시적으로 condition 해주면
common-vs-subject-specific 신호 분리 가능, V/A 예측 향상.

Output: results/phase2/brain_only/IV_subject_aware/<task>.csv
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

sys.path.insert(0, "/pscratch/sd/s/sjmoon/FEELIN/code/phase2")
from _lib import (TASKS, load_brain_embeddings, load_task_labels, get_fold_split,
                  eval_metrics, val_score, fit_standardizer, apply_standardizer,
                  ALL_SUBJECTS,
                  DEFAULT_BRAIN, DEFAULT_BRAIN_INIT, DEFAULT_BRAIN_PAD)

OUT_DIR = Path("/pscratch/sd/s/sjmoon/FEELIN/results/phase2/brain_only/IV_subject_aware")


class BrainSubjMLP(nn.Module):
    def __init__(self, brain_dim, n_subj, n_out, task_type, hidden=256, subj_dim=16, dropout=0.3):
        super().__init__()
        self.task_type = task_type
        self.subj_emb = nn.Embedding(n_subj, subj_dim)
        nn.init.trunc_normal_(self.subj_emb.weight, std=0.02)
        self.net = nn.Sequential(
            nn.Linear(brain_dim + subj_dim, hidden), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(hidden, hidden), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(hidden, n_out if task_type == "binary" else 1),
        )

    def forward(self, brain, subj_ids):
        s = self.subj_emb(subj_ids)
        x = torch.cat([brain, s], dim=-1)
        return self.net(x)


def build_brain_subj_data(brain_dict, label_df, split_df, task_type):
    """Each (subj, stim) → (brain, subj_id, label)."""
    subj_to_id = {s: i for i, s in enumerate(ALL_SUBJECTS)}
    label_df = label_df.merge(split_df, on="stimulus_num", how="inner")
    out = {sp: {"brain": [], "subj_id": [], "label": []} for sp in ["train", "val", "test"]}
    for subj, (emb, stim_arr) in brain_dict.items():
        sid = subj_to_id[subj]
        s2b = {int(s): i for i, s in enumerate(stim_arr)}
        for _, row in label_df.iterrows():
            stim, sp, lab = int(row["stimulus_num"]), row["split"], row["label"]
            if stim not in s2b: continue
            out[sp]["brain"].append(emb[s2b[stim]])
            out[sp]["subj_id"].append(sid)
            out[sp]["label"].append(lab)
    for sp in out:
        out[sp]["brain"] = np.stack(out[sp]["brain"]).astype(np.float32)
        out[sp]["subj_id"] = np.asarray(out[sp]["subj_id"], dtype=np.int64)
        if task_type == "binary":
            out[sp]["label"] = np.asarray(out[sp]["label"], dtype=np.int64)
        else:
            out[sp]["label"] = np.asarray(out[sp]["label"], dtype=np.float32)
    return out


def train_one_subj(brain_train, subj_train, label_train,
                   brain_val, subj_val, label_val,
                   brain_test, subj_test, label_test,
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
    else:
        y_mean, y_std = 0.0, 1.0
        lt = label_train

    tr_ds = TensorDataset(torch.from_numpy(b_tr), torch.from_numpy(subj_train),
                          torch.from_numpy(lt))
    tr_loader = DataLoader(tr_ds, batch_size=batch_size, shuffle=True)

    best_global = None
    n_subj = len(ALL_SUBJECTS)
    for lr in lrs:
        torch.manual_seed(seed)
        model = BrainSubjMLP(b_tr.shape[1], n_subj, n_out, task_type).to(device)
        opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
        best_val, best_state, since, diverged = -np.inf, None, 0, False
        for epoch in range(epochs):
            model.train()
            for bb, ss, yy in tr_loader:
                bb, ss, yy = bb.to(device), ss.to(device), yy.to(device)
                opt.zero_grad()
                logits = model(bb, ss)
                if task_type == "binary":
                    loss = F.cross_entropy(logits, yy)
                else:
                    loss = F.mse_loss(logits.squeeze(-1), yy)
                if not torch.isfinite(loss): diverged = True; break
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
            if diverged: break
            model.eval()
            with torch.no_grad():
                logits_v = model(torch.from_numpy(b_va).to(device),
                                  torch.from_numpy(subj_val).to(device))
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
    model = BrainSubjMLP(b_tr.shape[1], n_subj, n_out, task_type).to(device)
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        logits_t = model(torch.from_numpy(b_te).to(device),
                          torch.from_numpy(subj_test).to(device))
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
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--folds", default="1,2,3,4,5")
    ap.add_argument("--out_csv", default=None)
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    folds = [int(f) for f in args.folds.split(",")]
    out_csv = args.out_csv or str(OUT_DIR / f"{args.task}.csv")
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"=== Brain-only IV (subject-aware) task={args.task} ===")

    brain = load_brain_embeddings(args.brain_model, args.brain_init, args.brain_padding)
    label_df, ttype = load_task_labels(args.task)
    n_out = TASKS[args.task]["n_out"]

    rows = []
    for fold in folds:
        split = get_fold_split(fold)
        data = build_brain_subj_data(brain, label_df, split, ttype)
        for seed in seeds:
            t0 = time.time()
            res = train_one_subj(
                data["train"]["brain"], data["train"]["subj_id"], data["train"]["label"],
                data["val"]["brain"],   data["val"]["subj_id"],   data["val"]["label"],
                data["test"]["brain"],  data["test"]["subj_id"],  data["test"]["label"],
                ttype, n_out, seed, device,
            )
            elapsed = time.time() - t0
            row = {
                "feature": "Phase2_BrainOnly_IV_subject_aware",
                "method": "IV_subject_aware",
                "task": args.task, "task_type": ttype,
                "main_metric": TASKS[args.task]["main_metric"],
                "head": "mlp_subj_emb", "mode": "pooled", "subject": "pool",
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
