"""
Chance baseline (absolute statistical floor).

각 task 에 대해 feature 무관 dummy predictor 의 5-fold CV 성능을 측정.
- Binary: DummyClassifier(strategy='stratified') + 'most_frequent'
- Regression: DummyRegressor(strategy='mean') + 'median'
- Multinomial: DummyClassifier(strategy='stratified') + 'most_frequent'
- Multi-reg: DummyRegressor(strategy='mean')

Result CSV schema 는 run_unified_probe.py 와 호환되도록 정렬:
  feature, dir_prefix, padding, init, task, task_type, main_metric,
  head, mode, subject, fold, seed, n_train, n_val, n_test, test_main, ...
"""
import argparse
import csv
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    roc_auc_score,
)

warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
DATA = FEELIN / "data"
OUT_DIR = FEELIN / "project/shared/results/background/phase1"

DIM14_COLS = [
    "arousal_score", "dominance_score", "valence_score", "approach_score",
    "attention_score", "certainty_score", "commitment_score", "control_score",
    "effort_score", "fairness_score", "identity_score", "obstruction_score",
    "safety_score", "upswing_score",
]

TASKS = {
    "V_binary":    {"type": "binary",      "n_out": 2,  "main_metric": "AUROC"},
    "A_binary":    {"type": "binary",      "n_out": 2,  "main_metric": "AUROC"},
    "V_reg":       {"type": "regression",  "n_out": 1,  "main_metric": "pearson_r"},
    "A_reg":       {"type": "regression",  "n_out": 1,  "main_metric": "pearson_r"},
    "Cat34_top1":  {"type": "multinomial", "n_out": 34, "main_metric": "bal_acc"},
    "Dim14_multi": {"type": "multi_reg",   "n_out": 14, "main_metric": "mean_pearson_r"},
}

# Dummy strategies per task type
DUMMY_HEADS = {
    "binary":      [("stratified",   DummyClassifier, {"strategy": "stratified"}),
                    ("most_frequent",DummyClassifier, {"strategy": "most_frequent"})],
    "regression":  [("mean",         DummyRegressor,  {"strategy": "mean"}),
                    ("median",       DummyRegressor,  {"strategy": "median"})],
    "multinomial": [("stratified",   DummyClassifier, {"strategy": "stratified"}),
                    ("most_frequent",DummyClassifier, {"strategy": "most_frequent"})],
    "multi_reg":   [("mean",         DummyRegressor,  {"strategy": "mean"})],
}


def _load_task_labels(task):
    if task == "V_binary":
        df = pd.read_csv(DATA / "horikawa_L0_V_binary_subset.csv")
        return df[["stimulus_num", "v_label"]], "v_label"
    if task == "A_binary":
        df = pd.read_csv(DATA / "horikawa_L0_A_binary_subset.csv")
        return df[["stimulus_num", "a_label"]], "a_label"
    df = pd.read_csv(DATA / "cowen_horikawa_labels.csv")
    df = df.rename(columns={"stimulus_num": "stimulus_name_str", "stim_num_int": "stimulus_num"})
    if task == "V_reg":
        return df[["stimulus_num", "valence_score"]], "valence_score"
    if task == "A_reg":
        return df[["stimulus_num", "arousal_score"]], "arousal_score"
    if task == "Cat34_top1":
        score_cols = [f"score_{i}" for i in range(34)]
        df["cat34_top1"] = df[score_cols].values.argmax(axis=1)
        return df[["stimulus_num", "cat34_top1"]], "cat34_top1"
    if task == "Dim14_multi":
        return df[["stimulus_num"] + DIM14_COLS], DIM14_COLS
    raise ValueError(task)


def _get_fold_split(test_fold):
    df5 = pd.read_csv(DATA / "horikawa_5fold.csv")
    val_fold = (test_fold % 5) + 1
    df5["split"] = "train"
    df5.loc[df5["fold"] == val_fold, "split"] = "val"
    df5.loc[df5["fold"] == test_fold, "split"] = "test"
    return df5[["stimulus_num", "split"]]


def build_split(task, test_fold):
    label_df, label_col = _load_task_labels(task)
    split = _get_fold_split(test_fold)
    df = label_df.merge(split, on="stimulus_num", how="inner")
    out = {}
    for sp in ["train", "val", "test"]:
        sub = df[df["split"] == sp]
        if isinstance(label_col, list):
            out[f"y_{sp}"] = sub[label_col].values.astype(np.float32)
        else:
            out[f"y_{sp}"] = sub[label_col].values
    return out


def eval_metrics(ttype, y_true, y_pred, y_prob=None):
    out = {}
    if ttype == "binary":
        out["test_auroc"]   = float(roc_auc_score(y_true, y_prob))
        out["test_auprc"]   = float(average_precision_score(y_true, y_prob))
        out["test_bal_acc"] = float(balanced_accuracy_score(y_true, y_pred))
        out["test_main"]    = out["test_auroc"]
    elif ttype == "regression":
        # Dummy mean/median has zero variance → pearsonr undefined. Set to 0.
        if np.std(y_pred) < 1e-10:
            r = 0.0
        else:
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
        rs = []
        for d in range(y_true.shape[1]):
            if np.std(y_pred[:, d]) < 1e-10 or np.std(y_true[:, d]) < 1e-10:
                rs.append(0.0)
                continue
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                r, _ = pearsonr(y_true[:, d], y_pred[:, d])
            rs.append(0.0 if np.isnan(r) else float(r))
        out["test_pearson_r_per_dim"] = rs
        out["test_pearson_r_mean"]    = float(np.mean(rs))
        out["test_mae_mean"]          = float(mean_absolute_error(y_true, y_pred))
        out["test_mse_mean"]          = float(mean_squared_error(y_true, y_pred))
        out["test_rmse_mean"]         = float(np.sqrt(out["test_mse_mean"]))
        out["test_main"]              = out["test_pearson_r_mean"]
    return out


def run_dummy(data, ttype, head_name, ModelCls, kw, seed):
    ytr, yte = data["y_train"], data["y_test"]
    if ttype == "multi_reg":
        # MultiOutputRegressor 안 필요. DummyRegressor 가 multi-output 지원.
        model = ModelCls(**kw)
        # DummyRegressor needs X; use dummy zeros
        Xtr = np.zeros((len(ytr), 1))
        Xte = np.zeros((len(yte), 1))
        model.fit(Xtr, ytr)
        y_pred = model.predict(Xte)
        return eval_metrics(ttype, yte, y_pred, y_pred)
    if ttype == "regression":
        model = ModelCls(**kw)
        Xtr = np.zeros((len(ytr), 1))
        Xte = np.zeros((len(yte), 1))
        model.fit(Xtr, ytr)
        y_pred = model.predict(Xte)
        return eval_metrics(ttype, yte, y_pred, y_pred)
    # classifier
    kw_seed = dict(kw)
    if kw.get("strategy") in ("stratified", "uniform", "prior"):
        kw_seed["random_state"] = seed
    model = ModelCls(**kw_seed)
    Xtr = np.zeros((len(ytr), 1))
    Xte = np.zeros((len(yte), 1))
    model.fit(Xtr, ytr)
    y_pred = model.predict(Xte)
    if ttype == "binary":
        y_prob = model.predict_proba(Xte)[:, 1]
    else:
        y_prob = None
    return eval_metrics(ttype, yte, y_pred, y_prob)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_csv", default=str(OUT_DIR / "chance_baseline.csv"))
    ap.add_argument("--summary_csv", default=str(OUT_DIR / "chance_baseline_summary.csv"))
    ap.add_argument("--tasks", default="all")
    ap.add_argument("--folds", default="1,2,3,4,5")
    ap.add_argument("--seeds", default="0,1,2", help="stratified dummy 는 random 이라 seed 평균 의미. default 3.")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    task_list = list(TASKS.keys()) if args.tasks == "all" else [t.strip() for t in args.tasks.split(",")]
    folds = [int(f) for f in args.folds.split(",")]
    seeds = [int(s) for s in args.seeds.split(",")]

    rows = []
    for task in task_list:
        cfg = TASKS[task]
        ttype = cfg["type"]
        for fold in folds:
            data = build_split(task, fold)
            ntr, nva, nte = len(data["y_train"]), len(data["y_val"]), len(data["y_test"])
            for head_name, ModelCls, kw in DUMMY_HEADS[ttype]:
                # Deterministic dummy (most_frequent / mean / median) → 1 seed
                if kw.get("strategy") in ("most_frequent", "mean", "median"):
                    seed_list = [seeds[0]]
                else:
                    seed_list = seeds
                for seed in seed_list:
                    res = run_dummy(data, ttype, head_name, ModelCls, kw, seed)
                    row = {
                        "feature": "chance",
                        "dir_prefix": "n/a",
                        "padding": "n/a",
                        "init": "n/a",
                        "task": task,
                        "task_type": ttype,
                        "main_metric": cfg["main_metric"],
                        "head": head_name,
                        "mode": "stim_level",
                        "subject": "all",
                        "fold": fold,
                        "seed": seed,
                        "n_train": ntr,
                        "n_val": nva,
                        "n_test": nte,
                    }
                    for k, v in res.items():
                        if isinstance(v, list):
                            row[k] = ";".join(f"{x:.6f}" for x in v)
                        else:
                            row[k] = v
                    rows.append(row)
                    print(f"  {task:12s} fold={fold} head={head_name:14s} seed={seed} test_main={res['test_main']:.4f}")

    df = pd.DataFrame(rows)
    df.to_csv(args.out_csv, index=False)
    print(f"\nWrote {len(df)} rows to {args.out_csv}")

    # Aggregate across folds + seeds for ALL test_* metrics (mean + std + count)
    from _summary_helper import summarize_probe_csv
    summary = summarize_probe_csv(args.out_csv, args.summary_csv)
    print(f"Wrote summary to {args.summary_csv} ({len(summary)} cells, {len(summary.columns)} cols)")
    # short stdout: just main metric + 1 condition per task
    if "test_main_mean" in summary.columns:
        cols = [c for c in ["task", "head", "test_main_mean", "test_main_std", "count"] if c in summary.columns]
        print(summary[cols].to_string(index=False))


if __name__ == "__main__":
    main()
