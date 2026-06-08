"""
Chance baseline for Cat34_multilabel and Cat34_soft tasks.

These two tasks were not covered by run_chance_baseline.py (which handles
V/A binary, V/A regression, Cat34_top1, Dim14_multi). This script supplements
the Cat34 chance floor so that BFM Cat34 results have a meaningful baseline.

Strategies
  Cat34_multilabel (per-category binary classification, 34 cats)
    - stratified    : per-category positive-rate prior. Probability for cat i = train prevalence of cat i.
                      Repeated across test samples. seed = noop here (probability is deterministic given training stats).
    - most_frequent : per-category majority class (deterministic). Predicts the more frequent label per cat.
  Cat34_soft (probability distribution over 34 cats)
    - shuffled : reassigns train target distributions to test samples at random (seed-dependent).
                 Provides a finite Pearson r near 0 by construction.
    - mean     : train fold's mean distribution, broadcast to all test samples. Per-cat std = 0 across
                 predictions, so per-cat Pearson r is undefined. Reported for reference; metric stays NaN.
    - uniform  : 1/34 each, broadcast to all test samples. Same NaN behaviour as mean.

Metrics
  Cat34_multilabel : macro AUROC (mean of per-cat binary AUROC, cats with all-pos or all-neg skipped) + macro F1.
  Cat34_soft       : mean Pearson r over 34 cats + top1 accuracy (argmax match).

Output CSV is compatible with the existing summary aggregator (_summary_helper).
"""
import argparse
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.metrics import f1_score, roc_auc_score

warnings.filterwarnings("ignore")

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
DATA = FEELIN / "data"
OUT_DIR = FEELIN / "project/shared/results/background/phase1"

CAT34_MULTILABEL_THRESHOLD = 0.10  # 2026-06-07: was 0.15. See run_unified_probe.py.

TASKS = {
    "Cat34_multilabel": {"type": "multilabel", "main_metric": "macro_auroc"},
    "Cat34_soft":       {"type": "soft_dist",  "main_metric": "mean_pearson_r"},
}


def _load_task_labels(task):
    df = pd.read_csv(DATA / "cowen_horikawa_labels.csv")
    df = df.rename(columns={"stimulus_num": "stimulus_name_str",
                            "stim_num_int": "stimulus_num"})
    score_cols = [f"score_{i}" for i in range(34)]

    if task == "Cat34_multilabel":
        scores = df[score_cols].values
        mask = (scores >= CAT34_MULTILABEL_THRESHOLD).astype(np.float32)
        cols = [f"cat_{i}" for i in range(34)]
        out = df[["stimulus_num"]].copy()
        for i, c in enumerate(cols):
            out[c] = mask[:, i]
        return out, cols

    if task == "Cat34_soft":
        scores = df[score_cols].values.astype(np.float32)
        row_sum = scores.sum(axis=1, keepdims=True)
        scores = scores / np.clip(row_sum, 1e-8, None)
        out = df[["stimulus_num"]].copy()
        for i, c in enumerate(score_cols):
            out[c] = scores[:, i]
        return out, score_cols

    raise ValueError(task)


def _get_fold_split(test_fold):
    df5 = pd.read_csv(DATA / "horikawa_5fold.csv")
    val_fold = (test_fold % 5) + 1
    df5["split"] = "train"
    df5.loc[df5["fold"] == val_fold, "split"] = "val"
    df5.loc[df5["fold"] == test_fold, "split"] = "test"
    return df5[["stimulus_num", "split"]]


def build_split(task, test_fold):
    label_df, label_cols = _load_task_labels(task)
    split = _get_fold_split(test_fold)
    df = label_df.merge(split, on="stimulus_num", how="inner")
    out = {}
    for sp in ["train", "val", "test"]:
        sub = df[df["split"] == sp]
        out[f"y_{sp}"] = sub[label_cols].values.astype(np.float32)
    return out


def eval_multilabel(y_true, y_prob):
    per_cat_auroc = []
    for d in range(y_true.shape[1]):
        yt = y_true[:, d]
        if yt.sum() == 0 or yt.sum() == len(yt):
            continue
        per_cat_auroc.append(float(roc_auc_score(yt, y_prob[:, d])))
    macro_auroc = float(np.mean(per_cat_auroc)) if per_cat_auroc else float("nan")
    pred = (y_prob >= 0.5).astype(int)
    macro_f1 = float(f1_score(y_true.astype(int), pred, average="macro", zero_division=0))
    return {
        "test_main": macro_auroc,
        "test_auroc": macro_auroc,
        "test_macro_f1": macro_f1,
    }


def eval_soft(y_true, y_pred):
    rs = []
    for d in range(y_true.shape[1]):
        yt, yp = y_true[:, d], y_pred[:, d]
        if yt.std() < 1e-8 or yp.std() < 1e-8:
            continue
        r, _ = pearsonr(yt, yp)
        if np.isnan(r):
            continue
        rs.append(float(r))
    mean_r = float(np.mean(rs)) if rs else float("nan")
    pred_top = y_pred.argmax(axis=1)
    true_top = y_true.argmax(axis=1)
    top1 = float((pred_top == true_top).mean())
    return {
        "test_main": mean_r,
        "test_pearson_r_mean": mean_r,
        "test_top1_acc": top1,
    }


def run_dummy(task, fold, seed, strategy):
    data = build_split(task, fold)
    ytr, yte = data["y_train"], data["y_test"]
    ntr, nva, nte = len(ytr), len(data["y_val"]), len(yte)

    if task == "Cat34_multilabel":
        prevs = ytr.mean(axis=0).astype(np.float32)
        if strategy == "stratified":
            prob_te = np.tile(prevs, (nte, 1))
        elif strategy == "most_frequent":
            pred = (prevs > 0.5).astype(np.float32)
            prob_te = np.tile(pred, (nte, 1))
        else:
            raise ValueError(strategy)
        res = eval_multilabel(yte, prob_te)

    elif task == "Cat34_soft":
        if strategy == "mean":
            mean_dist = ytr.mean(axis=0).astype(np.float32)
            s = mean_dist.sum()
            mean_dist = mean_dist / max(s, 1e-8)
            pred = np.tile(mean_dist, (nte, 1))
        elif strategy == "uniform":
            pred = np.full(yte.shape, 1.0 / 34, dtype=np.float32)
        elif strategy == "shuffled":
            # Reassign train distributions to test samples at random.
            rng = np.random.default_rng(seed)
            idx = rng.integers(0, len(ytr), size=nte)
            pred = ytr[idx].astype(np.float32)
        else:
            raise ValueError(strategy)
        res = eval_soft(yte, pred)

    else:
        raise ValueError(task)

    return res, ntr, nva, nte


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_csv", default=str(OUT_DIR / "chance_cat34.csv"))
    ap.add_argument("--summary_csv", default=str(OUT_DIR / "chance_cat34_summary.csv"))
    ap.add_argument("--folds", default="1,2,3,4,5")
    ap.add_argument("--seeds", default="0,1,2",
                    help="Multilabel stratified / most_frequent and soft mean / uniform are all "
                         "deterministic given training stats, so seed only labels the row. "
                         "Default 3 to match V/A chance baseline schema.")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    folds = [int(f) for f in args.folds.split(",")]
    seeds = [int(s) for s in args.seeds.split(",")]

    plan = {
        "Cat34_multilabel": ["stratified", "most_frequent"],
        "Cat34_soft":       ["shuffled", "mean", "uniform"],
    }

    rows = []
    for task, strategies in plan.items():
        cfg = TASKS[task]
        for strategy in strategies:
            seed_list = seeds  # all deterministic, but keep schema parity with chance_baseline.csv
            for fold in folds:
                for seed in seed_list:
                    res, ntr, nva, nte = run_dummy(task, fold, seed, strategy)
                    row = {
                        "feature": "chance",
                        "dir_prefix": "n/a",
                        "padding": "n/a",
                        "init": "n/a",
                        "task": task,
                        "task_type": cfg["type"],
                        "main_metric": cfg["main_metric"],
                        "head": strategy,
                        "mode": "stim_level",
                        "subject": "all",
                        "fold": fold,
                        "seed": seed,
                        "n_train": ntr,
                        "n_val": nva,
                        "n_test": nte,
                    }
                    row.update(res)
                    rows.append(row)
                    print(f"  {task:18s} fold={fold} head={strategy:14s} seed={seed} "
                          f"test_main={res['test_main']:.4f}")

    df = pd.DataFrame(rows)
    df.to_csv(args.out_csv, index=False)
    print(f"\nWrote {len(df)} rows to {args.out_csv}")

    # Aggregate across folds + seeds for all test_* metrics.
    import sys
    sys.path.insert(0, str(FEELIN / "project/shared/code/probes"))
    from _summary_helper import summarize_probe_csv
    summary = summarize_probe_csv(args.out_csv, args.summary_csv)
    print(f"Wrote summary {len(summary)} rows to {args.summary_csv}")


if __name__ == "__main__":
    main()
