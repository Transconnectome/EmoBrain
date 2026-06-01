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
    "V_binary": {"type": "binary",     "n_out": 2,  "main_metric": "AUROC"},
    "A_binary": {"type": "binary",     "n_out": 2,  "main_metric": "AUROC"},
    "V_reg":    {"type": "regression", "n_out": 1,  "main_metric": "pearson_r"},
    "A_reg":    {"type": "regression", "n_out": 1,  "main_metric": "pearson_r"},
}


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
    cfg = TASKS[task]
    ttype = cfg["type"]
    if task == "V_binary":
        df = pd.read_csv(DATA / "horikawa_L0_V_binary_subset.csv")
        return df[["stimulus_num", "v_label"]].rename(columns={"v_label": "label"}), ttype
    if task == "A_binary":
        df = pd.read_csv(DATA / "horikawa_L0_A_binary_subset.csv")
        return df[["stimulus_num", "a_label"]].rename(columns={"a_label": "label"}), ttype
    df = pd.read_csv(DATA / "cowen_horikawa_labels.csv")
    df = df.rename(columns={"stimulus_num": "stim_str", "stim_num_int": "stimulus_num"})
    if task == "V_reg":
        return df[["stimulus_num", "valence_score"]].rename(columns={"valence_score": "label"}), ttype
    if task == "A_reg":
        return df[["stimulus_num", "arousal_score"]].rename(columns={"arousal_score": "label"}), ttype
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
                      task_type: str):
    """For 'pooled' mode: each of 5 subjects contributes its (brain, video, label) tuples;
    all stacked together (same stim appears 5 times with different brain).

    Returns dict {split: {brain (N, D_brain), video (N, D_video), label (N,)}}.
    """
    label_df = label_df.merge(split_df, on="stimulus_num", how="inner")
    stim_to_video_idx = {int(s): i for i, s in enumerate(video_stim_idx)}
    out = {sp: {"brain": [], "video": [], "label": []} for sp in ["train", "val", "test"]}

    for subj, (emb, stim_arr) in brain_dict.items():
        stim_to_brain_idx = {int(s): i for i, s in enumerate(stim_arr)}
        for _, row in label_df.iterrows():
            stim = int(row["stimulus_num"])
            sp = row["split"]
            label = row["label"]
            if stim not in stim_to_brain_idx or stim not in stim_to_video_idx:
                continue
            out[sp]["brain"].append(emb[stim_to_brain_idx[stim]])
            out[sp]["video"].append(video_feat[stim_to_video_idx[stim]])
            out[sp]["label"].append(label)

    for sp in ["train", "val", "test"]:
        out[sp]["brain"] = np.stack(out[sp]["brain"], axis=0)
        out[sp]["video"] = np.stack(out[sp]["video"], axis=0)
        if task_type == "binary":
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
                                 mean_absolute_error, mean_squared_error)
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
    return out


def val_score(task_type, y_true, y_pred, y_prob=None):
    """Single scalar for HP selection (higher = better)."""
    from scipy.stats import pearsonr
    from sklearn.metrics import roc_auc_score
    if task_type == "binary":
        return float(roc_auc_score(y_true, y_prob))
    r, _ = pearsonr(y_true, y_pred)
    return float(r)


# ============================================================
# Standardization
# ============================================================

def fit_standardizer(X):
    mu = X.mean(axis=0, keepdims=True)
    std = X.std(axis=0, keepdims=True) + 1e-8
    return mu, std


def apply_standardizer(X, mu, std):
    return (X - mu) / std
