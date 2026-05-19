"""
Multi-BFM probe — compare 3 BFMs on V/A binary decoding.

Models (all with padding=mean, sub-01..05, both init):
  - SwiFT NewE96 (ver11, 768-dim)
  - Brain-JEPA  (ViT-Base, 768-dim)
  - NeuroSTORM  (mae_ratio0.5, embed_dim from .pt)

For each (model, init, task, head, mode, subject, seed):
  - 2 init (resting / scratch)
  - 2 task (V, A)
  - 2 head (linear, mlp)
  - 2 mode (pooled / per_subject)
  - 3 seed (0, 1, 2)

Outputs:
  results/main_grid_3bfm/probe_full.csv     (per-seed rows)
  results/main_grid_3bfm/probe_summary.csv  (mean ± std per cell)

NOTE: padding=mean is the spatial-only control (T=20 all frames = avg of original T).
      This is documented in SLIDES.txt as a baseline, not a true padding mode.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, balanced_accuracy_score,
                             roc_auc_score)
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.heads import SwiftMLP

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
EMB_ROOT = FEELIN / "output/embeddings"
DATA = FEELIN / "data"
OUT_DIR = FEELIN / "results/main_grid_3bfm"

# (display_name, dir_prefix)
# SwiFT_NewE96 결과는 이미 results/padding_ablation/allsubj_{pooled,persubj}_swift_probe.csv 에 있음.
# 합칠 때 그 CSV 와 이 결과 join.
MODELS = [
    ("Brain-JEPA",   "brain_jepa"),
    ("NeuroSTORM",   "neurostorm"),
]
ALL_SUBJECTS = ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05"]
INITS = ["resting", "scratch"]
PADDING = "mean"   # locked: only mean padding extracted for BJ+NS
TASKS = ["V", "A"]
MODES = ["pooled", "per_subject"]
SEEDS = [0, 1, 2]

LINEAR_CS = [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]
MLP_LRS = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
MLP_BATCH = 8
MLP_EPOCHS = 40
MLP_PATIENCE = 10
MLP_WD = 1e-4
MLP_NUM_BLOCKS = 2
MLP_RATIO = 4.0
MLP_DROP = 0.3


def load_subject_emb(model_prefix, init, subject):
    p = EMB_ROOT / f"{model_prefix}_{init}_pad-{PADDING}" / f"{subject}.pt"
    d = torch.load(p, map_location="cpu", weights_only=False)
    emb = d["embeddings"].numpy().astype(np.float32)
    stim = d["stim_num"].numpy() if hasattr(d["stim_num"], "numpy") else np.asarray(d["stim_num"])
    return emb, stim


def _task_label_df(task):
    if task == "V":
        return pd.read_csv(DATA / "horikawa_L0_V_binary_subset.csv"), "v_label"
    return pd.read_csv(DATA / "horikawa_L0_A_binary_subset.csv"), "a_label"


def build_task_data(model_prefix, init, task, subjects):
    bin_df, label_col = _task_label_df(task)
    split = pd.read_csv(DATA / "horikawa_split.csv")
    X_parts = {"train": [], "val": [], "test": []}
    y_parts = {"train": [], "val": [], "test": []}
    for subj in subjects:
        emb, stim_num = load_subject_emb(model_prefix, init, subj)
        split_s = split[split["subject"] == subj][["stimulus_num", "split"]]
        df = (bin_df[["stimulus_num", label_col]]
              .merge(split_s, on="stimulus_num", how="inner"))
        stim_to_idx = {int(s): i for i, s in enumerate(stim_num)}
        df["row"] = df["stimulus_num"].map(stim_to_idx)
        assert df["row"].notna().all(), f"stim_num mismatch for {subj}"
        for sp in ["train", "val", "test"]:
            sub = df[df["split"] == sp]
            rows = sub["row"].astype(int).values
            X_parts[sp].append(emb[rows])
            y_parts[sp].append(sub[label_col].astype(int).values)
    out = {}
    for sp in ["train", "val", "test"]:
        out[f"X_{sp}"] = np.concatenate(X_parts[sp], axis=0)
        out[f"y_{sp}"] = np.concatenate(y_parts[sp], axis=0)
    scaler = StandardScaler().fit(out["X_train"])
    for k in ["X_train", "X_val", "X_test"]:
        out[k] = scaler.transform(out[k])
    return out


def eval_metrics(y_true, prob, pred):
    return {
        "auroc": float(roc_auc_score(y_true, prob)),
        "auprc": float(average_precision_score(y_true, prob)),
        "bal_acc": float(balanced_accuracy_score(y_true, pred)),
    }


def linear_probe(data, seed):
    best_c, best_val_auc, best_model = None, -1, None
    for C in LINEAR_CS:
        clf = LogisticRegression(C=C, penalty="l2", solver="lbfgs",
                                 max_iter=5000, class_weight="balanced",
                                 random_state=seed, n_jobs=1)
        clf.fit(data["X_train"], data["y_train"])
        val_prob = clf.predict_proba(data["X_val"])[:, 1]
        val_auc = roc_auc_score(data["y_val"], val_prob)
        if val_auc > best_val_auc:
            best_val_auc, best_c, best_model = val_auc, C, clf
    test_prob = best_model.predict_proba(data["X_test"])[:, 1]
    test_pred = best_model.predict(data["X_test"])
    m = eval_metrics(data["y_test"], test_prob, test_pred)
    m["val_auroc"] = float(best_val_auc)
    m["best_hp"] = f"C={best_c}"
    return m


def _train_one_mlp(data, seed, lr, dev):
    torch.manual_seed(seed); np.random.seed(seed)
    in_dim = data["X_train"].shape[1]
    Xtr = torch.from_numpy(data["X_train"]).float().to(dev)
    ytr = torch.from_numpy(data["y_train"]).long().to(dev)
    Xva = torch.from_numpy(data["X_val"]).float().to(dev)
    Xte = torch.from_numpy(data["X_test"]).float().to(dev)
    ytr_np = data["y_train"]
    n_train = len(ytr_np)
    class_count = np.bincount(ytr_np)
    sample_w = 1.0 / class_count[ytr_np]
    sample_w = sample_w / sample_w.sum()

    model = SwiftMLP(num_classes=2, num_blocks=MLP_NUM_BLOCKS, hidden_dim=in_dim,
                     mlp_ratio=MLP_RATIO, drop_rate=MLP_DROP,
                     already_pooled=True).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=MLP_WD)
    loss_fn = nn.CrossEntropyLoss()
    rng = np.random.default_rng(seed)

    best_val_auc, best_state, stale, best_epoch = -1, None, 0, 0
    for epoch in range(MLP_EPOCHS):
        model.train()
        idx_all = rng.choice(n_train, size=n_train, replace=True, p=sample_w)
        idx_all = torch.from_numpy(idx_all).long().to(dev)
        for s in range(0, n_train, MLP_BATCH):
            idx = idx_all[s:s + MLP_BATCH]
            opt.zero_grad()
            logits = model(Xtr[idx])
            loss = loss_fn(logits, ytr[idx])
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            val_prob = torch.softmax(model(Xva), dim=1)[:, 1].cpu().numpy()
        val_auc = roc_auc_score(data["y_val"], val_prob)
        if val_auc > best_val_auc:
            best_val_auc = val_auc
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            best_epoch = epoch + 1; stale = 0
        else:
            stale += 1
            if stale >= MLP_PATIENCE:
                break

    model.load_state_dict(best_state); model.eval()
    with torch.no_grad():
        test_prob = torch.softmax(model(Xte), dim=1)[:, 1].cpu().numpy()
    test_pred = (test_prob >= 0.5).astype(int)
    m = eval_metrics(data["y_test"], test_prob, test_pred)
    return best_val_auc, m, best_epoch


def mlp_probe(data, seed, dev):
    best_lr, best_val_auc, best_test, best_epoch = None, -1, None, 0
    for lr in MLP_LRS:
        val_auc, test_m, ep = _train_one_mlp(data, seed, lr, dev)
        if val_auc > best_val_auc:
            best_val_auc, best_lr, best_test, best_epoch = val_auc, lr, test_m, ep
    m = dict(best_test)
    m["val_auroc"] = float(best_val_auc)
    m["best_hp"] = f"lr={best_lr},ep={best_epoch}"
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_csv", default=str(OUT_DIR / "probe_full.csv"))
    ap.add_argument("--summary_csv", default=str(OUT_DIR / "probe_summary.csv"))
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {dev}")
    print(f"Models: {[m[0] for m in MODELS]}")
    print(f"Cells per model: 2 init x 2 task x 2 head x 2 mode x 3 seed = 96")
    print(f"  pooled mode = 1 row, per_subject mode = 5 rows")
    print(f"Total estimated rows: 3 model x 2 init x 2 task x 2 head x 3 seed x (1 pooled + 5 per_subj)")
    print(f"                     = 3 x 2 x 2 x 2 x 3 x 6 = 432 rows\n")

    rows = []
    for model_name, model_prefix in MODELS:
        print(f"\n{'='*60}\nMODEL: {model_name}  ({model_prefix})\n{'='*60}")
        for init in INITS:
            for task in TASKS:
                for mode in MODES:
                    if mode == "pooled":
                        groups = [("pool", list(ALL_SUBJECTS))]
                    else:
                        groups = [(s, [s]) for s in ALL_SUBJECTS]
                    for subj_label, subj_list in groups:
                        try:
                            data = build_task_data(model_prefix, init, task, subj_list)
                        except FileNotFoundError as e:
                            print(f"  [skip] missing data: {e}")
                            continue
                        ntr, nva, nte = len(data["y_train"]), len(data["y_val"]), len(data["y_test"])
                        for head_name in ["linear", "mlp"]:
                            for seed in SEEDS:
                                if head_name == "linear":
                                    res = linear_probe(data, seed)
                                else:
                                    res = mlp_probe(data, seed, dev)
                                row = {
                                    "model": model_name, "init": init, "task": task,
                                    "head": head_name, "mode": mode, "subject": subj_label,
                                    "seed": seed,
                                    "n_train": ntr, "n_val": nva, "n_test": nte,
                                    "best_hp": res["best_hp"],
                                    "val_auroc": res["val_auroc"],
                                    "test_auroc": res["auroc"],
                                    "test_auprc": res["auprc"],
                                    "test_bal_acc": res["bal_acc"],
                                }
                                rows.append(row)
                                print(f"  [{model_name:13s} {init:7s} {task} {head_name:6s} "
                                      f"{mode:11s} {subj_label:6s} s{seed}] "
                                      f"AUC={res['auroc']:.3f} AUPRC={res['auprc']:.3f}")

    df = pd.DataFrame(rows)
    df.to_csv(args.out_csv, index=False)
    print(f"\n[done] {args.out_csv}  ({len(df)} rows)")

    grp = ["model", "init", "task", "head", "mode", "subject"]
    metrics = ["test_auroc", "test_auprc", "test_bal_acc"]
    agg = df.groupby(grp)[metrics].agg(["mean", "std"])
    agg.columns = [f"{m}_{stat}" for m, stat in agg.columns]
    agg = agg.reset_index()
    agg.to_csv(args.summary_csv, index=False)
    print(f"[done] {args.summary_csv}  ({len(agg)} cells)")

    print("\n=== Aggregate test AUROC per (model, head, mode) ===")
    print(df.groupby(["model", "head", "mode"])["test_auroc"].agg(["mean", "std"]).round(4))


if __name__ == "__main__":
    main()
