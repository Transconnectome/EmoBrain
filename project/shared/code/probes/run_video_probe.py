"""
Video-only frozen-feature probe — stimulus features 만으로 emotion 예측 ceiling 측정.

Scientific question:
  자극 (영상) 자체의 feature 만으로 emotion 이 어디까지 예측되는가?
  Brain 정보 없이 video model 만의 ceiling 은 무엇인가?
  이게 곧 "brain conditioning 이 video baseline 위에 추가하는 value" 의 reference.

  가장 critical reviewer-killing baseline. "당신 brain 결과 0.7 인데 영상만 봐도
  0.85 나오면 brain 의 의의는?" 의 답을 측정 가능하게 함.

Feature sources (EmoViS 에서 추출됨, EmoBrain 은 reuse):
  V-JEPA2 (pretrained + scratch) — temporal video
  CLIP    (pretrained + scratch) — static image
  DINOv2  (pretrained + scratch) — static image
  VideoMAE (pretrained + scratch) — temporal video
  Qwen-VL caption embedding       — language-grounded

Protocol:
  Stim-level (no subject dimension. video feature 는 stim 당 1개)
  2185 stim x stim-stratified 80/10/10 split (horikawa_split.csv 의 sub-01 split 사용 — 같은
   자극 = 모든 subject 동일이므로 어느 subject 의 split row 든 같음)
  6 task (V_binary, A_binary, V_reg, A_reg, Cat34_top1, Dim14_multi)
  Linear + MLP heads, 3 seeds

Output:
  results/phase1/video_probe.csv
  results/phase1/video_probe_summary.csv
"""
import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (average_precision_score, balanced_accuracy_score,
                             f1_score, mean_absolute_error, mean_squared_error,
                             roc_auc_score)
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from scipy.linalg import LinAlgWarning
from scipy.stats import pearsonr

warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.metrics")
warnings.filterwarnings("ignore", category=LinAlgWarning)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
from _lib.heads import SwiftMLP

EmoBrain = Path("/pscratch/sd/s/sjmoon/EmoBrain")
FEAT_DIR = EmoBrain / "project/shared/data/stimulus_features"
DATA = EmoBrain / "data"
OUT_DIR = EmoBrain / "project/shared/results/phase1"

# Video feature source: (display_name, filename_in_feat_dir)
VIDEO_FEATURES = [
    ("V-JEPA2_pretrained",  "vjepa2_pretrained.npy"),
    ("V-JEPA2_scratch",     "vjepa2_scratch.npy"),
    ("CLIP_pretrained",     "clip_pretrained.npy"),
    ("CLIP_scratch",        "clip_scratch.npy"),
    ("DINOv2_pretrained",   "dinov2_pretrained.npy"),
    ("DINOv2_scratch",      "dinov2_scratch.npy"),
    ("VideoMAE_pretrained", "videomae_pretrained.npy"),
    ("VideoMAE_scratch",    "videomae_scratch.npy"),
    ("Qwen-VL_caption",     "caption_embed.npy"),
]

# Cowen 14 affective dimensions
DIM14_COLS = ["arousal_score", "dominance_score", "valence_score", "approach_score",
              "attention_score", "certainty_score", "commitment_score", "control_score",
              "effort_score", "fairness_score", "identity_score", "obstruction_score",
              "safety_score", "upswing_score"]

TASKS = {
    "V_binary":   {"type": "binary",      "n_out": 2,  "main_metric": "AUROC"},
    "A_binary":   {"type": "binary",      "n_out": 2,  "main_metric": "AUROC"},
    "V_reg":      {"type": "regression",  "n_out": 1,  "main_metric": "pearson_r"},
    "A_reg":      {"type": "regression",  "n_out": 1,  "main_metric": "pearson_r"},
    "Cat34_top1": {"type": "multinomial", "n_out": 34, "main_metric": "bal_acc"},
    "Dim14_multi":{"type": "multi_reg",   "n_out": 14, "main_metric": "mean_pearson_r"},
}

HEADS = ["linear", "mlp"]
SEEDS = [0]  # default screening: 1 seed. Final paper 직전에 --seeds 0,1,2 로 늘리기.
FOLDS = [1, 2, 3, 4, 5]  # 5-fold CV (data/horikawa_5fold.csv)

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
# Feature loading
# ============================================================

def load_video_feature(filename):
    """Return (2185, D) video feature + stim_num array (1..2185)."""
    feat = np.load(FEAT_DIR / filename).astype(np.float32)
    # EmoViS stim_idx 는 0..2184. 우리 horikawa_split 은 stimulus_num 1..2185.
    stim_num = np.arange(1, feat.shape[0] + 1, dtype=np.int64)
    if feat.shape[0] != 2185:
        raise ValueError(f"{filename} expected 2185 stim, got {feat.shape[0]}")
    return feat, stim_num


def _load_task_labels(task):
    cfg = TASKS[task]
    ttype = cfg["type"]
    if task == "V_binary":
        df = pd.read_csv(DATA / "horikawa_L0_V_binary_subset.csv")
        return df[["stimulus_num", "v_label"]], "v_label", ttype
    if task == "A_binary":
        df = pd.read_csv(DATA / "horikawa_L0_A_binary_subset.csv")
        return df[["stimulus_num", "a_label"]], "a_label", ttype
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
    raise ValueError(task)


def _get_fold_split(test_fold):
    """5-fold CV: test = fold k, val = (k%5)+1, train = remaining 3."""
    df5 = pd.read_csv(DATA / "horikawa_5fold.csv")
    val_fold = (test_fold % 5) + 1
    df5["split"] = "train"
    df5.loc[df5["fold"] == val_fold, "split"] = "val"
    df5.loc[df5["fold"] == test_fold, "split"] = "test"
    return df5[["stimulus_num", "split"]]


def build_task_data(filename, task, test_fold):
    """Stim-level data (no subject dim). 5-fold CV (test_fold = which fold is test)."""
    label_df, label_col, ttype = _load_task_labels(task)
    split = _get_fold_split(test_fold)
    feat, stim_num = load_video_feature(filename)
    stim_to_idx = {int(s): i for i, s in enumerate(stim_num)}

    df = label_df.merge(split, on="stimulus_num", how="inner")
    df["row"] = df["stimulus_num"].map(stim_to_idx)
    assert df["row"].notna().all(), "stim_num mismatch"

    out = {}
    for sp in ["train", "val", "test"]:
        sub = df[df["split"] == sp]
        rows = sub["row"].astype(int).values
        out[f"X_{sp}"] = feat[rows]
        if isinstance(label_col, list):
            out[f"y_{sp}"] = sub[label_col].values.astype(np.float32)
        else:
            out[f"y_{sp}"] = sub[label_col].values

    scaler = StandardScaler().fit(out["X_train"])
    for k in ["X_train", "X_val", "X_test"]:
        out[k] = scaler.transform(out[k])
    if ttype in ("regression", "multi_reg"):
        if ttype == "regression":
            out["y_mean"] = float(out["y_train"].mean())
            out["y_std"]  = float(out["y_train"].std() + 1e-8)
        else:
            out["y_mean"] = out["y_train"].mean(axis=0).astype(np.float32)
            out["y_std"]  = (out["y_train"].std(axis=0) + 1e-8).astype(np.float32)
    else:
        out["y_mean"], out["y_std"] = 0.0, 1.0
    return out, ttype


# ============================================================
# Metrics + probes (reuse from unified_probe pattern)
# ============================================================

def eval_metrics(ttype, y_true, y_pred, y_prob=None):
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
        rs = [pearsonr(y_true[:, d], y_pred[:, d])[0] for d in range(y_true.shape[1])]
        out["test_pearson_r_per_dim"] = [float(r) for r in rs]
        out["test_pearson_r_mean"]    = float(np.mean(rs))
        out["test_mae_mean"]          = float(mean_absolute_error(y_true, y_pred))
        out["test_mse_mean"]          = float(mean_squared_error(y_true, y_pred))
        out["test_rmse_mean"]         = float(np.sqrt(out["test_mse_mean"]))
        out["test_main"]              = out["test_pearson_r_mean"]
    return out


def val_score(ttype, y_true, y_pred, y_prob=None):
    if ttype == "binary":      return float(roc_auc_score(y_true, y_prob))
    if ttype == "regression":  r, _ = pearsonr(y_true, y_pred); return float(r)
    if ttype == "multinomial": return float(balanced_accuracy_score(y_true, y_pred))
    if ttype == "multi_reg":
        rs = [pearsonr(y_true[:, d], y_pred[:, d])[0] for d in range(y_true.shape[1])]
        return float(np.mean(rs))


def linear_probe(data, ttype, seed):
    Xtr, ytr = data["X_train"], data["y_train"]
    Xva, yva = data["X_val"],   data["y_val"]
    Xte, yte = data["X_test"],  data["y_test"]
    if ttype == "binary":
        best, best_c, best_model = -np.inf, None, None
        for C in LINEAR_CS:
            clf = LogisticRegression(C=C, penalty="l2", solver="lbfgs", max_iter=5000,
                                     class_weight="balanced", random_state=seed, n_jobs=1)
            clf.fit(Xtr, ytr)
            v = val_score(ttype, yva, clf.predict(Xva), clf.predict_proba(Xva)[:, 1])
            if v > best: best, best_c, best_model = v, C, clf
        prob = best_model.predict_proba(Xte)[:, 1]; pred = best_model.predict(Xte)
        m = eval_metrics(ttype, yte, pred, prob); m["val_main"] = best; m["best_hp"] = f"C={best_c}"
        return m
    if ttype == "regression":
        best, best_a, best_model = -np.inf, None, None
        for a in RIDGE_ALPHAS:
            clf = Ridge(alpha=a, random_state=seed); clf.fit(Xtr, ytr)
            v = val_score(ttype, yva, clf.predict(Xva))
            if v > best: best, best_a, best_model = v, a, clf
        pred = best_model.predict(Xte)
        m = eval_metrics(ttype, yte, pred); m["val_main"] = best; m["best_hp"] = f"alpha={best_a}"
        return m
    if ttype == "multinomial":
        best, best_c, best_model = -np.inf, None, None
        for C in LINEAR_CS:
            clf = LogisticRegression(C=C, penalty="l2", solver="lbfgs", max_iter=5000,
                                     class_weight="balanced", random_state=seed, n_jobs=1)
            clf.fit(Xtr, ytr)
            v = val_score(ttype, yva, clf.predict(Xva))
            if v > best: best, best_c, best_model = v, C, clf
        pred = best_model.predict(Xte)
        m = eval_metrics(ttype, yte, pred); m["val_main"] = best; m["best_hp"] = f"C={best_c}"
        return m
    if ttype == "multi_reg":
        best, best_a, best_model = -np.inf, None, None
        for a in RIDGE_ALPHAS:
            clf = MultiOutputRegressor(Ridge(alpha=a, random_state=seed)); clf.fit(Xtr, ytr)
            v = val_score(ttype, yva, clf.predict(Xva))
            if v > best: best, best_a, best_model = v, a, clf
        pred = best_model.predict(Xte)
        m = eval_metrics(ttype, yte, pred); m["val_main"] = best; m["best_hp"] = f"alpha={best_a}"
        return m
    raise ValueError(ttype)


def _train_one_mlp(data, ttype, seed, lr, dev, n_out):
    torch.manual_seed(seed); np.random.seed(seed)
    in_dim = data["X_train"].shape[1]
    Xtr = torch.from_numpy(data["X_train"]).float().to(dev)
    Xva = torch.from_numpy(data["X_val"]).float().to(dev)
    Xte = torch.from_numpy(data["X_test"]).float().to(dev)

    if ttype in ("binary", "multinomial"):
        ytr = torch.from_numpy(data["y_train"]).long().to(dev)
        loss_fn = nn.CrossEntropyLoss()
    else:
        y_mean = np.asarray(data["y_mean"], dtype=np.float32)
        y_std  = np.asarray(data["y_std"],  dtype=np.float32)
        ytr_np = (data["y_train"] - y_mean) / y_std
        if ttype == "regression": ytr_np = ytr_np.reshape(-1, 1)
        ytr = torch.from_numpy(ytr_np).float().to(dev)
        loss_fn = nn.MSELoss()

    n_train = data["y_train"].shape[0]
    if ttype in ("binary", "multinomial"):
        cls_count = np.maximum(np.bincount(data["y_train"]), 1)
        sample_w = 1.0 / cls_count[data["y_train"]]; sample_w = sample_w / sample_w.sum()
    else: sample_w = None

    model = SwiftMLP(num_classes=n_out, num_blocks=MLP_NUM_BLOCKS, hidden_dim=in_dim,
                     mlp_ratio=MLP_RATIO, drop_rate=MLP_DROP, already_pooled=True).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=MLP_WD)
    rng = np.random.default_rng(seed)

    best, best_state, stale, best_epoch = -np.inf, None, 0, 0
    for epoch in range(MLP_EPOCHS):
        model.train()
        idx = (rng.choice(n_train, size=n_train, replace=True, p=sample_w) if sample_w is not None
               else rng.permutation(n_train))
        idx = torch.from_numpy(idx).long().to(dev)
        for s in range(0, n_train, MLP_BATCH):
            i = idx[s:s+MLP_BATCH]; opt.zero_grad()
            loss = loss_fn(model(Xtr[i]), ytr[i]); loss.backward(); opt.step()
        model.eval()
        with torch.no_grad(): out_va = model(Xva).cpu().numpy()
        if ttype == "binary":
            prob_va = torch.softmax(torch.from_numpy(out_va), dim=1)[:, 1].numpy()
            pred_va = (prob_va >= 0.5).astype(int)
            v = val_score(ttype, data["y_val"], pred_va, prob_va)
        elif ttype == "multinomial":
            pred_va = out_va.argmax(axis=1); v = val_score(ttype, data["y_val"], pred_va)
        else:
            y_mean = np.asarray(data["y_mean"], dtype=np.float32)
            y_std  = np.asarray(data["y_std"],  dtype=np.float32)
            pred_va = out_va * y_std + y_mean
            if ttype == "regression": pred_va = pred_va.squeeze(-1)
            v = val_score(ttype, data["y_val"], pred_va)
        if v > best:
            best = v; best_state = {k: x.detach().clone() for k, x in model.state_dict().items()}
            best_epoch = epoch + 1; stale = 0
        else:
            stale += 1
            if stale >= MLP_PATIENCE: break

    model.load_state_dict(best_state); model.eval()
    with torch.no_grad(): out_te = model(Xte).cpu().numpy()
    if ttype == "binary":
        prob_te = torch.softmax(torch.from_numpy(out_te), dim=1)[:, 1].numpy()
        pred_te = (prob_te >= 0.5).astype(int)
        m = eval_metrics(ttype, data["y_test"], pred_te, prob_te)
    elif ttype == "multinomial":
        pred_te = out_te.argmax(axis=1); m = eval_metrics(ttype, data["y_test"], pred_te)
    else:
        y_mean = np.asarray(data["y_mean"], dtype=np.float32)
        y_std  = np.asarray(data["y_std"],  dtype=np.float32)
        pred_te = out_te * y_std + y_mean
        if ttype == "regression": pred_te = pred_te.squeeze(-1)
        m = eval_metrics(ttype, data["y_test"], pred_te)
    return best, m, best_epoch


def mlp_probe(data, ttype, seed, dev, n_out):
    best, best_lr, best_test, best_epoch = -np.inf, None, None, 0
    for lr in MLP_LRS:
        v, t, ep = _train_one_mlp(data, ttype, seed, lr, dev, n_out)
        if v > best: best, best_lr, best_test, best_epoch = v, lr, t, ep
    m = dict(best_test); m["val_main"] = best; m["best_hp"] = f"lr={best_lr},ep={best_epoch}"
    return m


# ============================================================
# Main
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_csv", default=str(OUT_DIR / "video_probe.csv"))
    ap.add_argument("--summary_csv", default=str(OUT_DIR / "video_probe_summary.csv"))
    ap.add_argument("--skip_mlp", action="store_true")
    ap.add_argument("--tasks", default="all")
    ap.add_argument("--features", default="all",
                    help="comma-separated video feature names. 'all' 이면 9 video 다.")
    ap.add_argument("--seeds", default="0", help="comma-separated seeds, default 1 seed.")
    ap.add_argument("--folds", default="1,2,3,4,5",
                    help="comma-separated outer folds for 5-fold CV.")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    task_list = list(TASKS.keys()) if args.tasks == "all" else [t.strip() for t in args.tasks.split(",")]
    if args.features == "all":
        features_to_run = VIDEO_FEATURES
    else:
        wanted = set(f.strip() for f in args.features.split(","))
        features_to_run = [f for f in VIDEO_FEATURES if f[0] in wanted]
        if not features_to_run:
            valid = sorted(set(f[0] for f in VIDEO_FEATURES))
            raise ValueError(f"no features matched {wanted}. valid: {valid}")

    seeds_global = [int(s) for s in args.seeds.split(",")]
    folds_global = [int(f) for f in args.folds.split(",")]
    heads_to_run = ["linear"] if args.skip_mlp else HEADS

    print(f"Device: {dev}, skip_mlp={args.skip_mlp}")
    print(f"Video features: {len(features_to_run)}, tasks: {task_list}, heads: {heads_to_run}, "
          f"seeds: {seeds_global}, folds: {folds_global}")

    rows = []
    for feat_name, filename in features_to_run:
        print(f"\n{'='*70}\nFEATURE: {feat_name}\n{'='*70}")
        for task in task_list:
            cfg = TASKS[task]; ttype, n_out = cfg["type"], cfg["n_out"]
            for fold in folds_global:
                try:
                    data, _ = build_task_data(filename, task, fold)
                except FileNotFoundError as e:
                    print(f"  [skip] {e}"); continue
                ntr, nva, nte = data["y_train"].shape[0], data["y_val"].shape[0], data["y_test"].shape[0]
                for head_name in heads_to_run:
                    seeds_for_this = [seeds_global[0]] if head_name == "linear" else seeds_global
                    for seed in seeds_for_this:
                        res = linear_probe(data, ttype, seed) if head_name == "linear" \
                              else mlp_probe(data, ttype, seed, dev, n_out)
                        # Unified schema with BFM probe (mode/subject/init/padding/dir_prefix 추가)
                        row = {
                            "feature": feat_name, "dir_prefix": filename,
                            "padding": "n/a", "init": "n/a",
                            "task": task, "task_type": ttype, "main_metric": cfg["main_metric"],
                            "head": head_name, "mode": "stim_level", "subject": "all",
                            "fold": fold, "seed": seed,
                            "n_train": ntr, "n_val": nva, "n_test": nte,
                            "best_hp": res["best_hp"], "val_main": res["val_main"],
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
                        print(f"  [{feat_name:24s} {task:11s} {head_name:6s} f{fold} s{seed}] "
                              f"main={res['test_main']:.3f} ({cfg['main_metric']})")

    df = pd.DataFrame(rows)
    df.to_csv(args.out_csv, index=False)
    print(f"\n[done] {args.out_csv}  ({len(df)} rows)")

    # Aggregate across folds + seeds for ALL test_* metrics (mean + std + count)
    from _summary_helper import summarize_probe_csv
    summary = summarize_probe_csv(args.out_csv, args.summary_csv)
    print(f"[done] {args.summary_csv}  ({len(summary)} cells, {len(summary.columns)} cols)")

    print("\n=== test_main per (feature, head, task) [seed 평균] ===")
    print(df.groupby(["feature", "head", "task"])["test_main"].mean().unstack("task").round(3))


if __name__ == "__main__":
    main()
