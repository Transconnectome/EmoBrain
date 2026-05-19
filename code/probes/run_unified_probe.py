"""
Unified frozen-feature probe — Tier 1 (ROI mean) + Tier 2 (BFM embedding) 통합 평가.

각 feature source 는 동일 protocol:
  5 subject x 2185 stimulus x stimulus-stratified 80/10/10 split x 3 seed
  per-subject mode 와 pooled mode 둘 다
  Linear (Logistic L2 with class_weight=balanced) + MLP (SwiFT vendored head)

Feature source spec (FEATURES 리스트):
  name       : 출력 CSV 의 feature 식별자
  dir_prefix : output/embeddings/{dir_prefix}_{init}_pad-{padding}/sub-XX.pt 로 .pt 파일 찾음
  padding    : 'mean' (proper) | 'spatial_only' (legacy) | 'replicate' | 'zero' | 'cyclic_replicate' |
               'time_mean' (ROI 의 time-mean feature 의 경우)
  init       : 'resting' | 'scratch' | 'n/a' (ROI 등 init 개념 없는 경우)

Output:
  results/phase1/unified_probe.csv (per-seed row)
  results/phase1/unified_probe_summary.csv (cell mean ± std)

Run example (Phase 1 W2 default):
  python code/probes/run_unified_probe.py
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

# Reuse SwiftMLP head from analysis/_lib
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
from _lib.heads import SwiftMLP

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
EMB_ROOT = FEELIN / "output/embeddings"
DATA = FEELIN / "data"
OUT_DIR = FEELIN / "results/phase1"

# Feature source 정의 (name, dir_prefix, padding, init)
FEATURES = [
    # Tier 1: ROI mean (init 없음, padding 은 time-mean)
    ("ROI_Schaefer400Tian50", "roi_schaefer400tian50_mean", "time_mean", "n/a"),
    # Tier 2: BFM embeddings (proper mean padding, resting + scratch)
    ("SwiFT_NewE96",  "swift_NewE96_SL20", "mean", "resting"),
    ("SwiFT_NewE96",  "swift_NewE96_SL20", "mean", "scratch"),
    ("Brain-JEPA",    "brain_jepa",        "mean", "resting"),
    ("Brain-JEPA",    "brain_jepa",        "mean", "scratch"),
    ("NeuroSTORM",    "neurostorm",        "mean", "resting"),
    ("NeuroSTORM",    "neurostorm",        "mean", "scratch"),
]

ALL_SUBJECTS = ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05"]
TASKS = ["V_binary", "A_binary"]   # 추후 V_regression, A_regression, 6-class 확장
MODES = ["pooled", "per_subject"]
HEADS = ["linear", "mlp"]
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


def load_subject_emb(dir_prefix, padding, init, subject):
    """Load .pt embeddings. ROI 는 init=n/a 이므로 init 무시한 path 도 시도."""
    if init == "n/a":
        # ROI 의 경우 init 없는 단일 dir
        p = EMB_ROOT / dir_prefix / f"{subject}.pt"
    else:
        p = EMB_ROOT / f"{dir_prefix}_{init}_pad-{padding}" / f"{subject}.pt"
    d = torch.load(p, map_location="cpu", weights_only=False)
    emb = d["embeddings"].numpy().astype(np.float32)
    stim = d["stim_num"].numpy() if hasattr(d["stim_num"], "numpy") else np.asarray(d["stim_num"])
    return emb, stim


def _task_label_df(task):
    """task name -> (DataFrame, label_column_name)"""
    if task == "V_binary":
        return pd.read_csv(DATA / "horikawa_L0_V_binary_subset.csv"), "v_label"
    if task == "A_binary":
        return pd.read_csv(DATA / "horikawa_L0_A_binary_subset.csv"), "a_label"
    raise ValueError(f"unknown task {task}")


def build_task_data(dir_prefix, padding, init, task, subjects):
    bin_df, label_col = _task_label_df(task)
    split = pd.read_csv(DATA / "horikawa_split.csv")
    X_parts = {"train": [], "val": [], "test": []}
    y_parts = {"train": [], "val": [], "test": []}
    for subj in subjects:
        emb, stim_num = load_subject_emb(dir_prefix, padding, init, subj)
        split_s = split[split["subject"] == subj][["stimulus_num", "split"]]
        df = (bin_df[["stimulus_num", label_col]]
              .merge(split_s, on="stimulus_num", how="inner"))
        stim_to_idx = {int(s): i for i, s in enumerate(stim_num)}
        df["row"] = df["stimulus_num"].map(stim_to_idx)
        assert df["row"].notna().all(), f"stim_num mismatch for {subj} {dir_prefix}"
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
    ap.add_argument("--out_csv", default=str(OUT_DIR / "unified_probe.csv"))
    ap.add_argument("--summary_csv", default=str(OUT_DIR / "unified_probe_summary.csv"))
    ap.add_argument("--skip_mlp", action="store_true",
                    help="Linear probe 만 빠르게 실행 (Tier 1 floor 검증용)")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {dev}, skip_mlp={args.skip_mlp}")
    print(f"Feature sources: {len(FEATURES)}")
    heads_to_run = ["linear"] if args.skip_mlp else HEADS

    rows = []
    for feat_name, dir_prefix, padding, init in FEATURES:
        cell_label = f"{feat_name}/{init}/{padding}"
        print(f"\n{'='*70}\nFEATURE: {cell_label}  (dir: {dir_prefix})\n{'='*70}")
        for task in TASKS:
            for mode in MODES:
                if mode == "pooled":
                    groups = [("pool", list(ALL_SUBJECTS))]
                else:
                    groups = [(s, [s]) for s in ALL_SUBJECTS]
                for subj_label, subj_list in groups:
                    try:
                        data = build_task_data(dir_prefix, padding, init, task, subj_list)
                    except FileNotFoundError as e:
                        print(f"  [skip] missing: {e}")
                        continue
                    ntr, nva, nte = len(data["y_train"]), len(data["y_val"]), len(data["y_test"])
                    for head_name in heads_to_run:
                        for seed in SEEDS:
                            if head_name == "linear":
                                res = linear_probe(data, seed)
                            else:
                                res = mlp_probe(data, seed, dev)
                            row = {
                                "feature": feat_name,
                                "dir_prefix": dir_prefix,
                                "padding": padding,
                                "init": init,
                                "task": task,
                                "head": head_name,
                                "mode": mode,
                                "subject": subj_label,
                                "seed": seed,
                                "n_train": ntr, "n_val": nva, "n_test": nte,
                                "best_hp": res["best_hp"],
                                "val_auroc": res["val_auroc"],
                                "test_auroc": res["auroc"],
                                "test_auprc": res["auprc"],
                                "test_bal_acc": res["bal_acc"],
                            }
                            rows.append(row)
                            print(f"  [{feat_name:24s} {init:7s} {task:9s} {head_name:6s} "
                                  f"{mode:11s} {subj_label:6s} s{seed}] "
                                  f"AUC={res['auroc']:.3f} AUPRC={res['auprc']:.3f}")

    df = pd.DataFrame(rows)
    df.to_csv(args.out_csv, index=False)
    print(f"\n[done] {args.out_csv}  ({len(df)} rows)")

    grp = ["feature", "init", "padding", "task", "head", "mode", "subject"]
    metrics = ["test_auroc", "test_auprc", "test_bal_acc"]
    agg = df.groupby(grp)[metrics].agg(["mean", "std"])
    agg.columns = [f"{m}_{stat}" for m, stat in agg.columns]
    agg = agg.reset_index()
    agg.to_csv(args.summary_csv, index=False)
    print(f"[done] {args.summary_csv}  ({len(agg)} cells)")

    print("\n=== Aggregate test AUROC per (feature, init, head, mode) ===")
    print(df.groupby(["feature", "init", "head", "mode"])["test_auroc"].agg(["mean", "std"]).round(4))


if __name__ == "__main__":
    main()
