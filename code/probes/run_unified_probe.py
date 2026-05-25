"""
Unified frozen-feature probe — 6 task 전부 평가.

Feature source spec (FEATURES 리스트):
  Tier 1: ROI mean (Schaefer 400 + Tian 50 = 450 dim)
  Tier 2: BFM embedding (SwiFT NewE96, Brain-JEPA, NeuroSTORM, resting + scratch)

Tasks (6 종):
  1. V_binary    : Valence Q4 vs Q1 (binary classification)
  2. A_binary    : Arousal Q4 vs Q1 (binary classification)
  3. V_reg       : Valence continuous (regression)
  4. A_reg       : Arousal continuous (regression)
  5. Cat34_top1  : Cowen 34-emotion category top-1 (multinomial)
  6. Dim14_multi : 14 affective dimensions multi-output regression

Heads:
  - linear: scikit-learn (Logistic L2 / Ridge / MultinomialLogistic / MultiOutputRidge)
  - mlp   : SwiFT vendored head (output_dim 과 loss 는 task 별 dispatch)

Protocol:
  5 subject x 2185 stim x stim-stratified 80/10/10 split x 3 seed
  pooled mode + per_subject mode
  Per-task 적절한 metric 측정

Output:
  results/phase1/unified_probe.csv (per-seed row, NaN-filled metric columns)
  results/phase1/unified_probe_summary.csv

Note:
  - Binary task 는 horikawa_L0_{V,A}_binary_subset.csv 사용 (Q4 vs Q1 subset)
  - Regression / multinomial / multi-output 은 cowen_horikawa_labels.csv 사용 (전체 2185)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (average_precision_score, balanced_accuracy_score,
                             f1_score, mean_absolute_error, mean_squared_error,
                             roc_auc_score)
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
from _lib.heads import SwiftMLP

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
EMB_ROOT = FEELIN / "output/embeddings"
DATA = FEELIN / "data"
OUT_DIR = FEELIN / "results/phase1"

# Feature source 정의
FEATURES = [
    ("ROI_Schaefer400Tian50", "roi_schaefer400tian50_mean", "time_mean", "n/a"),
    ("SwiFT_NewE96",  "swift_NewE96_SL20", "mean", "resting"),
    ("SwiFT_NewE96",  "swift_NewE96_SL20", "mean", "scratch"),
    ("Brain-JEPA",    "brain_jepa",        "mean", "resting"),
    ("Brain-JEPA",    "brain_jepa",        "mean", "scratch"),
    ("NeuroSTORM",    "neurostorm",        "mean", "resting"),
    ("NeuroSTORM",    "neurostorm",        "mean", "scratch"),
]

ALL_SUBJECTS = ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05"]
MODES = ["pooled", "per_subject"]
HEADS = ["linear", "mlp"]
SEEDS = [0]  # default screening: 1 seed. Final paper 직전에 --seeds 0,1,2 로 늘리기.

# 14 affective dimensions (Cowen 14-dim)
DIM14_COLS = ["arousal_score", "dominance_score", "valence_score", "approach_score",
              "attention_score", "certainty_score", "commitment_score", "control_score",
              "effort_score", "fairness_score", "identity_score", "obstruction_score",
              "safety_score", "upswing_score"]

# Task definition (type 으로 dispatch)
TASKS = {
    "V_binary":   {"type": "binary",      "n_out": 2,  "main_metric": "AUROC"},
    "A_binary":   {"type": "binary",      "n_out": 2,  "main_metric": "AUROC"},
    "V_reg":      {"type": "regression",  "n_out": 1,  "main_metric": "pearson_r"},
    "A_reg":      {"type": "regression",  "n_out": 1,  "main_metric": "pearson_r"},
    "Cat34_top1": {"type": "multinomial", "n_out": 34, "main_metric": "bal_acc"},
    "Dim14_multi":{"type": "multi_reg",   "n_out": 14, "main_metric": "mean_pearson_r"},
}

LINEAR_CS = [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]
RIDGE_ALPHAS = [1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]
MLP_LRS = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2]
MLP_BATCH = 8
MLP_EPOCHS = 40
MLP_PATIENCE = 10
MLP_WD = 1e-4
MLP_NUM_BLOCKS = 2
MLP_RATIO = 4.0
MLP_DROP = 0.3


# ============================================================
# Data loading
# ============================================================

def load_subject_emb(dir_prefix, padding, init, subject):
    if init == "n/a":
        p = EMB_ROOT / dir_prefix / f"{subject}.pt"
    else:
        p = EMB_ROOT / f"{dir_prefix}_{init}_pad-{padding}" / f"{subject}.pt"
    d = torch.load(p, map_location="cpu", weights_only=False)
    emb = d["embeddings"].numpy().astype(np.float32)
    stim = d["stim_num"].numpy() if hasattr(d["stim_num"], "numpy") else np.asarray(d["stim_num"])
    return emb, stim


def _load_task_labels(task):
    """Return (label_df with stimulus_num + label cols, label_col_or_list, task_type)."""
    cfg = TASKS[task]
    ttype = cfg["type"]

    if task == "V_binary":
        df = pd.read_csv(DATA / "horikawa_L0_V_binary_subset.csv")
        return df[["stimulus_num", "v_label"]], "v_label", ttype
    if task == "A_binary":
        df = pd.read_csv(DATA / "horikawa_L0_A_binary_subset.csv")
        return df[["stimulus_num", "a_label"]], "a_label", ttype

    # 나머지 task 는 전체 2185 stim 사용 (cowen_horikawa_labels.csv)
    # 주의: 이 CSV 에서 'stimulus_num' 컬럼은 "stimulus_1" 같은 string 이고
    #       int 인 stim_num 은 'stim_num_int' 컬럼. horikawa_split 의 'stimulus_num' (int) 과 맞추려고
    #       stim_num_int 를 'stimulus_num' 으로 rename.
    df = pd.read_csv(DATA / "cowen_horikawa_labels.csv")
    df = df.rename(columns={"stimulus_num": "stimulus_name_str", "stim_num_int": "stimulus_num"})
    if task == "V_reg":
        return df[["stimulus_num", "valence_score"]], "valence_score", ttype
    if task == "A_reg":
        return df[["stimulus_num", "arousal_score"]], "arousal_score", ttype
    if task == "Cat34_top1":
        score_cols = [f"score_{i}" for i in range(34)]
        df["cat34_top1"] = df[score_cols].values.argmax(axis=1)
        return df[["stimulus_num", "cat34_top1"]], "cat34_top1", ttype
    if task == "Dim14_multi":
        return df[["stimulus_num"] + DIM14_COLS], DIM14_COLS, ttype
    raise ValueError(f"unknown task {task}")


def build_task_data(dir_prefix, padding, init, task, subjects):
    label_df, label_col, ttype = _load_task_labels(task)
    split = pd.read_csv(DATA / "horikawa_split.csv")

    X_parts = {"train": [], "val": [], "test": []}
    y_parts = {"train": [], "val": [], "test": []}

    for subj in subjects:
        emb, stim_num = load_subject_emb(dir_prefix, padding, init, subj)
        split_s = split[split["subject"] == subj][["stimulus_num", "split"]]
        df = label_df.merge(split_s, on="stimulus_num", how="inner")
        stim_to_idx = {int(s): i for i, s in enumerate(stim_num)}
        df["row"] = df["stimulus_num"].map(stim_to_idx)
        assert df["row"].notna().all(), f"stim_num mismatch for {subj} {dir_prefix}"

        for sp in ["train", "val", "test"]:
            sub = df[df["split"] == sp]
            rows = sub["row"].astype(int).values
            X_parts[sp].append(emb[rows])
            if isinstance(label_col, list):
                y_parts[sp].append(sub[label_col].values.astype(np.float32))
            else:
                y_parts[sp].append(sub[label_col].values)

    out = {}
    for sp in ["train", "val", "test"]:
        out[f"X_{sp}"] = np.concatenate(X_parts[sp], axis=0)
        out[f"y_{sp}"] = np.concatenate(y_parts[sp], axis=0)

    # standardize X
    scaler = StandardScaler().fit(out["X_train"])
    for k in ["X_train", "X_val", "X_test"]:
        out[k] = scaler.transform(out[k])

    # for regression: also standardize y (helps MLP convergence)
    if ttype in ("regression", "multi_reg"):
        if ttype == "regression":
            y_mean = out["y_train"].mean()
            y_std = out["y_train"].std() + 1e-8
            out["y_mean"], out["y_std"] = float(y_mean), float(y_std)
        else:
            y_mean = out["y_train"].mean(axis=0)
            y_std = out["y_train"].std(axis=0) + 1e-8
            out["y_mean"], out["y_std"] = y_mean.astype(np.float32), y_std.astype(np.float32)
    else:
        out["y_mean"], out["y_std"] = 0.0, 1.0

    return out, ttype


# ============================================================
# Metrics (task-type aware)
# ============================================================

def eval_metrics(ttype, y_true, y_pred, y_prob=None):
    """y_pred = hard prediction (class label or regression value).
    y_prob = soft (probabilities or regression-as-is). For regression, y_prob == y_pred."""
    out = {}
    if ttype == "binary":
        out["test_auroc"]   = float(roc_auc_score(y_true, y_prob))
        out["test_auprc"]   = float(average_precision_score(y_true, y_prob))
        out["test_bal_acc"] = float(balanced_accuracy_score(y_true, y_pred))
        out["test_main"]    = out["test_auroc"]
    elif ttype == "regression":
        r, _ = pearsonr(y_true, y_pred)
        out["test_pearson_r"] = float(r)
        out["test_mae"]       = float(mean_absolute_error(y_true, y_pred))
        out["test_mse"]       = float(mean_squared_error(y_true, y_pred))
        out["test_rmse"]      = float(np.sqrt(out["test_mse"]))
        out["test_main"]      = out["test_pearson_r"]
    elif ttype == "multinomial":
        out["test_bal_acc"]   = float(balanced_accuracy_score(y_true, y_pred))
        out["test_macro_f1"]  = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
        out["test_top1_acc"]  = float((y_true == y_pred).mean())
        out["test_main"]      = out["test_bal_acc"]
    elif ttype == "multi_reg":
        # per-dim Pearson r → mean
        rs = []
        for d in range(y_true.shape[1]):
            r, _ = pearsonr(y_true[:, d], y_pred[:, d])
            rs.append(float(r))
        out["test_pearson_r_per_dim"] = rs
        out["test_pearson_r_mean"]    = float(np.mean(rs))
        out["test_mae_mean"]           = float(mean_absolute_error(y_true, y_pred))
        out["test_mse_mean"]           = float(mean_squared_error(y_true, y_pred))
        out["test_rmse_mean"]          = float(np.sqrt(out["test_mse_mean"]))
        out["test_main"]               = out["test_pearson_r_mean"]
    return out


def val_score(ttype, y_true, y_pred, y_prob=None):
    """Single scalar for HP selection (always higher = better)."""
    if ttype == "binary":
        return float(roc_auc_score(y_true, y_prob))
    if ttype == "regression":
        r, _ = pearsonr(y_true, y_pred)
        return float(r)
    if ttype == "multinomial":
        return float(balanced_accuracy_score(y_true, y_pred))
    if ttype == "multi_reg":
        rs = [pearsonr(y_true[:, d], y_pred[:, d])[0] for d in range(y_true.shape[1])]
        return float(np.mean(rs))


# ============================================================
# Linear probe (task-type dispatch)
# ============================================================

def linear_probe(data, ttype, seed):
    Xtr, ytr = data["X_train"], data["y_train"]
    Xva, yva = data["X_val"],   data["y_val"]
    Xte, yte = data["X_test"],  data["y_test"]

    if ttype == "binary":
        best_c, best_val, best_model = None, -np.inf, None
        for C in LINEAR_CS:
            clf = LogisticRegression(C=C, penalty="l2", solver="lbfgs", max_iter=5000,
                                     class_weight="balanced", random_state=seed, n_jobs=1)
            clf.fit(Xtr, ytr)
            v = val_score(ttype, yva, clf.predict(Xva), clf.predict_proba(Xva)[:, 1])
            if v > best_val:
                best_val, best_c, best_model = v, C, clf
        prob = best_model.predict_proba(Xte)[:, 1]
        pred = best_model.predict(Xte)
        m = eval_metrics(ttype, yte, pred, prob)
        m["val_main"] = best_val
        m["best_hp"] = f"C={best_c}"
        return m

    if ttype == "regression":
        best_a, best_val, best_model = None, -np.inf, None
        for alpha in RIDGE_ALPHAS:
            clf = Ridge(alpha=alpha, random_state=seed)
            clf.fit(Xtr, ytr)
            v = val_score(ttype, yva, clf.predict(Xva))
            if v > best_val:
                best_val, best_a, best_model = v, alpha, clf
        pred = best_model.predict(Xte)
        m = eval_metrics(ttype, yte, pred)
        m["val_main"] = best_val
        m["best_hp"] = f"alpha={best_a}"
        return m

    if ttype == "multinomial":
        best_c, best_val, best_model = None, -np.inf, None
        for C in LINEAR_CS:
            clf = LogisticRegression(C=C, penalty="l2", solver="lbfgs", max_iter=5000,
                                     class_weight="balanced",
                                     random_state=seed, n_jobs=1)
            clf.fit(Xtr, ytr)
            v = val_score(ttype, yva, clf.predict(Xva))
            if v > best_val:
                best_val, best_c, best_model = v, C, clf
        pred = best_model.predict(Xte)
        m = eval_metrics(ttype, yte, pred)
        m["val_main"] = best_val
        m["best_hp"] = f"C={best_c}"
        return m

    if ttype == "multi_reg":
        best_a, best_val, best_model = None, -np.inf, None
        for alpha in RIDGE_ALPHAS:
            clf = MultiOutputRegressor(Ridge(alpha=alpha, random_state=seed))
            clf.fit(Xtr, ytr)
            v = val_score(ttype, yva, clf.predict(Xva))
            if v > best_val:
                best_val, best_a, best_model = v, alpha, clf
        pred = best_model.predict(Xte)
        m = eval_metrics(ttype, yte, pred)
        m["val_main"] = best_val
        m["best_hp"] = f"alpha={best_a}"
        return m

    raise ValueError(ttype)


# ============================================================
# MLP probe (task-type dispatch)
# ============================================================

def _train_one_mlp(data, ttype, seed, lr, dev, n_out):
    torch.manual_seed(seed); np.random.seed(seed)
    in_dim = data["X_train"].shape[1]
    Xtr = torch.from_numpy(data["X_train"]).float().to(dev)
    Xva = torch.from_numpy(data["X_val"]).float().to(dev)
    Xte = torch.from_numpy(data["X_test"]).float().to(dev)

    # y dtype / loss dispatch
    if ttype in ("binary", "multinomial"):
        ytr = torch.from_numpy(data["y_train"]).long().to(dev)
        loss_fn = nn.CrossEntropyLoss()
    else:  # regression / multi_reg
        # standardize y for stable training, un-standardize at predict
        y_mean = np.asarray(data["y_mean"], dtype=np.float32)
        y_std  = np.asarray(data["y_std"],  dtype=np.float32)
        ytr_np = (data["y_train"] - y_mean) / y_std
        if ttype == "regression":
            ytr_np = ytr_np.reshape(-1, 1)
        ytr = torch.from_numpy(ytr_np).float().to(dev)
        loss_fn = nn.MSELoss()

    n_train = data["y_train"].shape[0]

    # balanced sampling weight (binary/multinomial 만)
    if ttype in ("binary", "multinomial"):
        cls_count = np.bincount(data["y_train"])
        # avoid 0-count bin (e.g. some Cat34 class missing in train)
        cls_count = np.maximum(cls_count, 1)
        sample_w = 1.0 / cls_count[data["y_train"]]
        sample_w = sample_w / sample_w.sum()
    else:
        sample_w = None

    model = SwiftMLP(num_classes=n_out, num_blocks=MLP_NUM_BLOCKS, hidden_dim=in_dim,
                     mlp_ratio=MLP_RATIO, drop_rate=MLP_DROP, already_pooled=True).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=MLP_WD)
    rng = np.random.default_rng(seed)

    best_val, best_state, stale, best_epoch = -np.inf, None, 0, 0
    for epoch in range(MLP_EPOCHS):
        model.train()
        if sample_w is not None:
            idx_all = rng.choice(n_train, size=n_train, replace=True, p=sample_w)
        else:
            idx_all = rng.permutation(n_train)
        idx_all = torch.from_numpy(idx_all).long().to(dev)
        for s in range(0, n_train, MLP_BATCH):
            idx = idx_all[s:s + MLP_BATCH]
            opt.zero_grad()
            out = model(Xtr[idx])
            if ttype == "binary":
                loss = loss_fn(out, ytr[idx])
            elif ttype == "multinomial":
                loss = loss_fn(out, ytr[idx])
            else:  # regression / multi_reg
                loss = loss_fn(out, ytr[idx])
            loss.backward()
            opt.step()

        model.eval()
        with torch.no_grad():
            out_va = model(Xva).cpu().numpy()
        # predict + val_score
        if ttype == "binary":
            prob_va = torch.softmax(torch.from_numpy(out_va), dim=1)[:, 1].numpy()
            pred_va = (prob_va >= 0.5).astype(int)
            v = val_score(ttype, data["y_val"], pred_va, prob_va)
        elif ttype == "multinomial":
            pred_va = out_va.argmax(axis=1)
            v = val_score(ttype, data["y_val"], pred_va)
        else:
            # un-standardize
            y_mean = np.asarray(data["y_mean"], dtype=np.float32)
            y_std  = np.asarray(data["y_std"],  dtype=np.float32)
            pred_va = out_va * y_std + y_mean
            if ttype == "regression":
                pred_va = pred_va.squeeze(-1)
            v = val_score(ttype, data["y_val"], pred_va)

        if v > best_val:
            best_val = v
            best_state = {k: x.detach().clone() for k, x in model.state_dict().items()}
            best_epoch = epoch + 1; stale = 0
        else:
            stale += 1
            if stale >= MLP_PATIENCE:
                break

    model.load_state_dict(best_state); model.eval()
    with torch.no_grad():
        out_te = model(Xte).cpu().numpy()
    if ttype == "binary":
        prob_te = torch.softmax(torch.from_numpy(out_te), dim=1)[:, 1].numpy()
        pred_te = (prob_te >= 0.5).astype(int)
        m = eval_metrics(ttype, data["y_test"], pred_te, prob_te)
    elif ttype == "multinomial":
        pred_te = out_te.argmax(axis=1)
        m = eval_metrics(ttype, data["y_test"], pred_te)
    else:
        y_mean = np.asarray(data["y_mean"], dtype=np.float32)
        y_std  = np.asarray(data["y_std"],  dtype=np.float32)
        pred_te = out_te * y_std + y_mean
        if ttype == "regression":
            pred_te = pred_te.squeeze(-1)
        m = eval_metrics(ttype, data["y_test"], pred_te)
    return best_val, m, best_epoch


def mlp_probe(data, ttype, seed, dev, n_out):
    best_lr, best_val, best_test, best_epoch = None, -np.inf, None, 0
    for lr in MLP_LRS:
        v, t, ep = _train_one_mlp(data, ttype, seed, lr, dev, n_out)
        if v > best_val:
            best_val, best_lr, best_test, best_epoch = v, lr, t, ep
    m = dict(best_test)
    m["val_main"] = best_val
    m["best_hp"] = f"lr={best_lr},ep={best_epoch}"
    return m


# ============================================================
# Main
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_csv", default=str(OUT_DIR / "unified_probe.csv"))
    ap.add_argument("--summary_csv", default=str(OUT_DIR / "unified_probe_summary.csv"))
    ap.add_argument("--skip_mlp", action="store_true", help="Linear probe 만 실행 (빠른 floor 확인)")
    ap.add_argument("--tasks", default="all", help="comma-separated subset of TASKS keys, 'all' 이면 6 task 다")
    ap.add_argument("--features", default="all",
                    help="comma-separated feature names (predefined FEATURES 리스트 의 첫 element). "
                         "e.g. --features SwiFT_NewE96 또는 ROI_Schaefer400Tian50,Brain-JEPA. 'all' 이면 전부.")
    ap.add_argument("--seeds", default="0", help="comma-separated seeds, default 1 seed.")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if args.tasks == "all":
        task_list = list(TASKS.keys())
    else:
        task_list = [t.strip() for t in args.tasks.split(",")]
        for t in task_list:
            if t not in TASKS:
                raise ValueError(f"unknown task {t}. valid: {list(TASKS.keys())}")

    if args.features == "all":
        features_to_run = FEATURES
    else:
        wanted = set(f.strip() for f in args.features.split(","))
        features_to_run = [f for f in FEATURES if f[0] in wanted]
        if not features_to_run:
            valid = sorted(set(f[0] for f in FEATURES))
            raise ValueError(f"no features matched {wanted}. valid: {valid}")

    seeds_global = [int(s) for s in args.seeds.split(",")]
    heads_to_run = ["linear"] if args.skip_mlp else HEADS

    print(f"Device: {dev}, skip_mlp={args.skip_mlp}")
    print(f"Features: {len(features_to_run)}, tasks: {task_list}, heads: {heads_to_run}, seeds: {seeds_global}")

    rows = []
    for feat_name, dir_prefix, padding, init in features_to_run:
        print(f"\n{'='*70}\nFEATURE: {feat_name}/{init}/{padding} (dir: {dir_prefix})\n{'='*70}")
        for task in task_list:
            cfg = TASKS[task]
            ttype, n_out = cfg["type"], cfg["n_out"]
            for mode in MODES:
                if mode == "pooled":
                    groups = [("pool", list(ALL_SUBJECTS))]
                else:
                    groups = [(s, [s]) for s in ALL_SUBJECTS]
                for subj_label, subj_list in groups:
                    try:
                        data, _ = build_task_data(dir_prefix, padding, init, task, subj_list)
                    except FileNotFoundError as e:
                        print(f"  [skip] missing: {e}")
                        continue
                    ntr = data["y_train"].shape[0]
                    nva = data["y_val"].shape[0]
                    nte = data["y_test"].shape[0]
                    for head_name in heads_to_run:
                        # Linear is deterministic; 1 seed enough even if user passes more
                        seeds_for_this = [seeds_global[0]] if head_name == "linear" else seeds_global
                        for seed in seeds_for_this:
                            if head_name == "linear":
                                res = linear_probe(data, ttype, seed)
                            else:
                                res = mlp_probe(data, ttype, seed, dev, n_out)
                            row = {
                                "feature": feat_name, "dir_prefix": dir_prefix,
                                "padding": padding, "init": init,
                                "task": task, "task_type": ttype, "main_metric": cfg["main_metric"],
                                "head": head_name, "mode": mode, "subject": subj_label,
                                "seed": seed,
                                "n_train": ntr, "n_val": nva, "n_test": nte,
                                "best_hp": res["best_hp"],
                                "val_main": res["val_main"],
                                "test_main": res["test_main"],
                                "test_auroc": res.get("test_auroc"),
                                "test_auprc": res.get("test_auprc"),
                                "test_bal_acc": res.get("test_bal_acc"),
                                "test_pearson_r": res.get("test_pearson_r"),
                                "test_mae": res.get("test_mae"),
                                "test_mse": res.get("test_mse"),
                                "test_rmse": res.get("test_rmse"),
                                "test_macro_f1": res.get("test_macro_f1"),
                                "test_top1_acc": res.get("test_top1_acc"),
                                "test_pearson_r_mean": res.get("test_pearson_r_mean"),
                                "test_mae_mean": res.get("test_mae_mean"),
                                "test_mse_mean": res.get("test_mse_mean"),
                                "test_rmse_mean": res.get("test_rmse_mean"),
                                "test_pearson_r_per_dim": (
                                    json.dumps(res.get("test_pearson_r_per_dim"))
                                    if res.get("test_pearson_r_per_dim") is not None else None),
                            }
                            rows.append(row)
                            print(f"  [{feat_name:24s} {init:7s} {task:11s} {head_name:6s} "
                                  f"{mode:11s} {subj_label:6s} s{seed}] "
                                  f"main={res['test_main']:.3f} ({cfg['main_metric']})")

    df = pd.DataFrame(rows)
    df.to_csv(args.out_csv, index=False)
    print(f"\n[done] {args.out_csv}  ({len(df)} rows)")

    grp = ["feature", "init", "padding", "task", "task_type", "main_metric", "head", "mode", "subject"]
    agg = df.groupby(grp)["test_main"].agg(["mean", "std", "count"]).reset_index()
    agg.to_csv(args.summary_csv, index=False)
    print(f"[done] {args.summary_csv}  ({len(agg)} cells)")

    print("\n=== test_main per (feature, head, task) [mean over seeds × subjects/pool] ===")
    print(df.groupby(["feature", "init", "head", "task"])["test_main"].mean().unstack("task").round(3))


if __name__ == "__main__":
    main()
