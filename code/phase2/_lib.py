"""
FEELIN Phase 2 — shared utilities.

Loads frozen brain BFM embeddings + frozen video features for joint training of 4
fusion architectures (A/B/C/D) on V/A tasks.

Same 5-fold stim-stratified CV protocol as Phase 1 (data/horikawa_5fold.csv).
Same task definitions (V_binary, A_binary, V_reg, A_reg).
"""
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import torch

warnings.filterwarnings("ignore")

FEELIN = Path("/pscratch/sd/s/sjmoon/FEELIN")
EMB_ROOT = FEELIN / "output/embeddings"
DATA = FEELIN / "data"
VIDEO_DIR = DATA / "stimulus_features"

ALL_SUBJECTS = ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05"]

# Phase 2 default: BJ + CLIP. Override via train args if needed.
DEFAULT_BRAIN = "brain_jepa"
DEFAULT_BRAIN_INIT = "resting"
DEFAULT_BRAIN_PAD = "zero"
DEFAULT_VIDEO = "clip_pretrained"

TASKS = {
    "V_binary":         {"type": "binary",     "n_out": 2,  "main_metric": "AUROC"},
    "A_binary":         {"type": "binary",     "n_out": 2,  "main_metric": "AUROC"},
    "V_reg":            {"type": "regression", "n_out": 1,  "main_metric": "pearson_r"},
    "A_reg":            {"type": "regression", "n_out": 1,  "main_metric": "pearson_r"},
    "Cat34_multilabel": {"type": "multilabel", "n_out": 34, "main_metric": "macro_auroc"},
    "Cat34_soft":       {"type": "soft_dist",  "n_out": 34, "main_metric": "mean_pearson_r"},
}

CAT34_MULTILABEL_THRESHOLD = 0.15
SCORE_COLS = [f"score_{i}" for i in range(34)]
MULTILABEL_COLS = [f"cat_{i}" for i in range(34)]


# ============================================================
# Data loading
# ============================================================

def load_brain_embeddings(brain_model: str = DEFAULT_BRAIN,
                          init: str = DEFAULT_BRAIN_INIT,
                          padding: str = DEFAULT_BRAIN_PAD,
                          subjects=None):
    """Return dict {subject: (emb (N, D), stim_num (N,))}."""
    if subjects is None:
        subjects = ALL_SUBJECTS
    out = {}
    for subj in subjects:
        p = EMB_ROOT / f"{brain_model}_{init}_pad-{padding}" / f"{subj}.pt"
        d = torch.load(p, map_location="cpu", weights_only=False)
        emb = d["embeddings"].numpy().astype(np.float32)
        stim = d["stim_num"].numpy() if hasattr(d["stim_num"], "numpy") else np.asarray(d["stim_num"])
        out[subj] = (emb, stim)
    return out


def load_video_feature(name: str = DEFAULT_VIDEO):
    """Return (feat (N, D), stim_num (N,) 1-indexed).

    Note: EmoViS stim_idx.npy is 0-indexed (0..N-1), but our label CSVs use
    stimulus_num 1-indexed (1..N). To align with Phase 1 video probe convention
    (run_video_probe.py:110-117), we IGNORE stim_idx.npy and assume video features
    are stored in order 1..N. video[i] corresponds to stimulus_num (i+1).
    """
    feat = np.load(VIDEO_DIR / f"{name}.npy").astype(np.float32)
    if feat.shape[0] != 2185:
        raise ValueError(f"{name}: expected 2185 stim, got {feat.shape[0]}")
    stim_num = np.arange(1, feat.shape[0] + 1, dtype=np.int64)
    return feat, stim_num


def load_task_labels(task: str):
    """Return (label_df, label_cols, task_type).
    - For single-target tasks (binary, regression): label_cols = "label" (str). df has one "label" column.
    - For multi-target tasks (multilabel, soft_dist): label_cols = list of column names.
    """
    cfg = TASKS[task]
    ttype = cfg["type"]
    if task == "V_binary":
        df = pd.read_csv(DATA / "horikawa_L0_V_binary_subset.csv")
        return df[["stimulus_num", "v_label"]].rename(columns={"v_label": "label"}), "label", ttype
    if task == "A_binary":
        df = pd.read_csv(DATA / "horikawa_L0_A_binary_subset.csv")
        return df[["stimulus_num", "a_label"]].rename(columns={"a_label": "label"}), "label", ttype
    df = pd.read_csv(DATA / "cowen_horikawa_labels.csv")
    df = df.rename(columns={"stimulus_num": "stim_str", "stim_num_int": "stimulus_num"})
    if task == "V_reg":
        return df[["stimulus_num", "valence_score"]].rename(columns={"valence_score": "label"}), "label", ttype
    if task == "A_reg":
        return df[["stimulus_num", "arousal_score"]].rename(columns={"arousal_score": "label"}), "label", ttype
    if task == "Cat34_multilabel":
        scores = df[SCORE_COLS].values
        mask = (scores >= CAT34_MULTILABEL_THRESHOLD).astype(np.float32)
        out = df[["stimulus_num"]].copy()
        for i, c in enumerate(MULTILABEL_COLS):
            out[c] = mask[:, i]
        return out, MULTILABEL_COLS, ttype
    if task == "Cat34_soft":
        scores = df[SCORE_COLS].values.astype(np.float32)
        row_sum = scores.sum(axis=1, keepdims=True)
        scores = scores / np.clip(row_sum, 1e-8, None)
        out = df[["stimulus_num"]].copy()
        for i, c in enumerate(SCORE_COLS):
            out[c] = scores[:, i]
        return out, SCORE_COLS, ttype
    raise ValueError(task)


def get_fold_split(test_fold: int):
    """Same as Phase 1: test=fold k, val=(k%5)+1, train=rest."""
    df = pd.read_csv(DATA / "horikawa_5fold.csv")
    val_fold = (test_fold % 5) + 1
    df["split"] = "train"
    df.loc[df["fold"] == val_fold, "split"] = "val"
    df.loc[df["fold"] == test_fold, "split"] = "test"
    return df[["stimulus_num", "split"]]


def build_pooled_data(brain_dict, video_feat, video_stim_idx, label_df, split_df,
                      task_type: str, label_cols=None):
    """For 'pooled' mode: each of 5 subjects contributes its (brain, video, label) tuples;
    all stacked together (same stim appears 5 times with different brain).

    label_cols: 'label' for single-target tasks (binary/regression),
                list of column names for multi-target tasks (multilabel/soft_dist).

    Returns dict {split: {brain (N, D_brain), video (N, D_video), label (N,) or (N, K)}}.
    """
    if label_cols is None:
        label_cols = "label"
    is_multi = isinstance(label_cols, list)
    label_df = label_df.merge(split_df, on="stimulus_num", how="inner")
    stim_to_video_idx = {int(s): i for i, s in enumerate(video_stim_idx)}
    out = {sp: {"brain": [], "video": [], "label": []} for sp in ["train", "val", "test"]}

    for subj, (emb, stim_arr) in brain_dict.items():
        stim_to_brain_idx = {int(s): i for i, s in enumerate(stim_arr)}
        for _, row in label_df.iterrows():
            stim = int(row["stimulus_num"])
            sp = row["split"]
            if stim not in stim_to_brain_idx or stim not in stim_to_video_idx:
                continue
            out[sp]["brain"].append(emb[stim_to_brain_idx[stim]])
            out[sp]["video"].append(video_feat[stim_to_video_idx[stim]])
            if is_multi:
                out[sp]["label"].append(np.asarray([row[c] for c in label_cols], dtype=np.float32))
            else:
                out[sp]["label"].append(row[label_cols])

    for sp in ["train", "val", "test"]:
        out[sp]["brain"] = np.stack(out[sp]["brain"], axis=0)
        out[sp]["video"] = np.stack(out[sp]["video"], axis=0)
        if is_multi:
            out[sp]["label"] = np.stack(out[sp]["label"], axis=0).astype(np.float32)
        elif task_type == "binary":
            out[sp]["label"] = np.asarray(out[sp]["label"], dtype=np.int64)
        else:
            out[sp]["label"] = np.asarray(out[sp]["label"], dtype=np.float32)
    return out


# ============================================================
# Metrics
# ============================================================

def eval_metrics(task_type: str, y_true, y_pred, y_prob=None):
    from scipy.stats import pearsonr
    from sklearn.metrics import (roc_auc_score, average_precision_score, balanced_accuracy_score,
                                 mean_absolute_error, mean_squared_error, f1_score)
    out = {}
    if task_type == "binary":
        out["test_auroc"] = float(roc_auc_score(y_true, y_prob))
        out["test_auprc"] = float(average_precision_score(y_true, y_prob))
        out["test_bal_acc"] = float(balanced_accuracy_score(y_true, y_pred))
        out["test_main"] = out["test_auroc"]
    elif task_type == "regression":
        r, _ = pearsonr(y_true, y_pred)
        out["test_pearson_r"] = float(r)
        out["test_mae"] = float(mean_absolute_error(y_true, y_pred))
        out["test_mse"] = float(mean_squared_error(y_true, y_pred))
        out["test_rmse"] = float(np.sqrt(out["test_mse"]))
        out["test_main"] = out["test_pearson_r"]
    elif task_type == "multilabel":
        aurocs = []
        for d in range(y_true.shape[1]):
            yt = y_true[:, d]
            if yt.sum() == 0 or yt.sum() == len(yt):
                aurocs.append(float("nan")); continue
            aurocs.append(float(roc_auc_score(yt, y_prob[:, d])))
        valid = [a for a in aurocs if not (a != a)]
        out["test_macro_auroc"] = float(np.mean(valid)) if valid else float("nan")
        out["test_macro_f1"] = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
        out["test_micro_f1"] = float(f1_score(y_true, y_pred, average="micro", zero_division=0))
        out["test_main"] = out["test_macro_auroc"]
    elif task_type == "soft_dist":
        rs = []
        for d in range(y_true.shape[1]):
            yt, yp = y_true[:, d], y_pred[:, d]
            if yt.std() < 1e-8 or yp.std() < 1e-8:
                rs.append(float("nan")); continue
            r, _ = pearsonr(yt, yp); rs.append(float(r))
        valid = [r for r in rs if not (r != r)]
        out["test_pearson_r_mean"] = float(np.mean(valid)) if valid else float("nan")
        top1_pred = y_pred.argmax(axis=1); top1_true = y_true.argmax(axis=1)
        out["test_top1_acc"] = float((top1_pred == top1_true).mean())
        out["test_main"] = out["test_pearson_r_mean"]
    return out


def val_score(task_type, y_true, y_pred, y_prob=None):
    """Single scalar for HP selection (higher = better)."""
    from scipy.stats import pearsonr
    from sklearn.metrics import roc_auc_score
    if task_type == "binary":
        return float(roc_auc_score(y_true, y_prob))
    if task_type == "multilabel":
        aurocs = []
        for d in range(y_true.shape[1]):
            yt = y_true[:, d]
            if yt.sum() == 0 or yt.sum() == len(yt):
                continue
            aurocs.append(roc_auc_score(yt, y_prob[:, d]))
        return float(np.mean(aurocs)) if aurocs else 0.0
    if task_type == "soft_dist":
        rs = []
        for d in range(y_true.shape[1]):
            yt, yp = y_true[:, d], y_pred[:, d]
            if yt.std() < 1e-8 or yp.std() < 1e-8: continue
            rs.append(pearsonr(yt, yp)[0])
        return float(np.mean(rs)) if rs else 0.0
    r, _ = pearsonr(y_true, y_pred)
    return float(r)


# ============================================================
# Task-type aware loss / output / prediction helpers
# ============================================================
def output_dim_for(task_type: str, n_out: int) -> int:
    """Required output dim of the model head, given task_type and n_out from TASKS."""
    if task_type == "binary":         return n_out   # 2
    if task_type == "regression":     return 1
    if task_type == "multilabel":     return n_out   # 34
    if task_type == "soft_dist":      return n_out   # 34
    raise ValueError(task_type)


def compute_loss(task_type, logits, target, y_mean=0.0, y_std=1.0):
    """Standard training loss per task type. For regression, target is expected ALREADY
    standardized (z-norm) by the caller; logits are the raw model output."""
    import torch
    import torch.nn.functional as F
    if task_type == "binary":
        return F.cross_entropy(logits, target)
    if task_type == "regression":
        return F.mse_loss(logits.squeeze(-1), target)
    if task_type == "multilabel":
        return F.binary_cross_entropy_with_logits(logits, target)
    if task_type == "soft_dist":
        # Target is a probability distribution. Use KL with log_softmax(logits) as input.
        return F.kl_div(F.log_softmax(logits, dim=-1), target, reduction="batchmean")
    raise ValueError(task_type)


def predict_from_logits(task_type, logits_np, y_mean=0.0, y_std=1.0):
    """Returns (pred, prob).
    - binary: pred = argmax, prob = softmax[:, 1]
    - regression: pred = logits * y_std + y_mean (1D), prob = pred
    - multilabel: pred = (sigmoid >= 0.5).int, prob = sigmoid
    - soft_dist: pred = softmax (also serves as prob), pred has shape (N, n_out)
    """
    import numpy as _np
    if task_type == "binary":
        ex = _np.exp(logits_np - logits_np.max(axis=1, keepdims=True))
        prob_all = ex / ex.sum(axis=1, keepdims=True)
        prob = prob_all[:, 1]
        pred = logits_np.argmax(axis=1)
        return pred, prob
    if task_type == "regression":
        pred = logits_np.squeeze(-1) * y_std + y_mean
        return pred, pred
    if task_type == "multilabel":
        prob = 1.0 / (1.0 + _np.exp(-logits_np))
        pred = (prob >= 0.5).astype(int)
        return pred, prob
    if task_type == "soft_dist":
        ex = _np.exp(logits_np - logits_np.max(axis=1, keepdims=True))
        prob = ex / _np.clip(ex.sum(axis=1, keepdims=True), 1e-8, None)
        return prob, prob
    raise ValueError(task_type)


def is_multi_target(task_type: str) -> bool:
    """True for tasks where label is 2D (N, K)."""
    return task_type in ("multilabel", "soft_dist")


# ============================================================
# Standardization
# ============================================================

def fit_standardizer(X):
    mu = X.mean(axis=0, keepdims=True)
    std = X.std(axis=0, keepdims=True) + 1e-8
    return mu, std


def apply_standardizer(X, mu, std):
    return (X - mu) / std
