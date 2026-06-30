"""Emotion task evaluation. 6 task types.

  - V/A continuous regression (Pearson r, MAE)
  - V/A binary classification, Q1 vs Q4 (AUROC, balanced accuracy)
  - Cat34 multilabel at threshold 0.10 (macro AUROC, # active cats)
  - Cat34 soft distribution (mean Pearson r, top1 acc)

design.md Section 7. Baselines (Phase 1 ROI mean + Ridge, BJ resting frozen) reported alongside.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import balanced_accuracy_score, roc_auc_score


def va_regression_metrics(va_pred: np.ndarray, va_true: np.ndarray) -> dict:
    r_v, _ = pearsonr(va_pred[:, 0], va_true[:, 0])
    r_a, _ = pearsonr(va_pred[:, 1], va_true[:, 1])
    mae_v = float(np.abs(va_pred[:, 0] - va_true[:, 0]).mean())
    mae_a = float(np.abs(va_pred[:, 1] - va_true[:, 1]).mean())
    return {"r_valence": r_v, "r_arousal": r_a, "mae_valence": mae_v, "mae_arousal": mae_a}


def _binary_metrics(score: np.ndarray, label: np.ndarray, mask: np.ndarray) -> dict:
    """One-axis (V or A) binary metric. score/label/mask: (N,). label in {0,1}, mask in {True,False}."""
    s, y = score[mask], label[mask].astype(int)
    if y.size < 2 or len(np.unique(y)) < 2:
        return {"auroc": float("nan"), "balanced_acc": float("nan"), "n": int(y.size)}
    auc = float(roc_auc_score(y, s))
    pred = (s >= 0.5).astype(int) if s.min() >= 0 and s.max() <= 1 else (s >= 0).astype(int)
    bacc = float(balanced_accuracy_score(y, pred))
    return {"auroc": auc, "balanced_acc": bacc, "n": int(y.size)}


def va_binary_metrics(
    score: np.ndarray, label: np.ndarray, mask: np.ndarray
) -> dict:
    """Q1 vs Q4 binary metric for V/A. score/label/mask: (N, 2)."""
    out_v = _binary_metrics(score[:, 0], label[:, 0], mask[:, 0])
    out_a = _binary_metrics(score[:, 1], label[:, 1], mask[:, 1])
    return {
        "auroc_valence": out_v["auroc"], "bacc_valence": out_v["balanced_acc"], "n_valence": out_v["n"],
        "auroc_arousal": out_a["auroc"], "bacc_arousal": out_a["balanced_acc"], "n_arousal": out_a["n"],
    }


def cat34_multilabel_metrics(cat34_pred: np.ndarray, cat34_true: np.ndarray, threshold: float = 0.10) -> dict:
    bin_true = (cat34_true >= threshold).astype(int)
    keep = bin_true.sum(axis=0) > 0
    auc = float(roc_auc_score(bin_true[:, keep], cat34_pred[:, keep], average="macro"))
    return {"macro_auroc_t010": auc, "n_active_cats": int(keep.sum())}


def cat34_soft_metrics(cat34_pred: np.ndarray, cat34_true: np.ndarray) -> dict:
    rs = [pearsonr(cat34_pred[:, k], cat34_true[:, k])[0] for k in range(cat34_true.shape[1])]
    rs = np.nan_to_num(rs, nan=0.0)
    top1_pred = cat34_pred.argmax(axis=1)
    top1_true = cat34_true.argmax(axis=1)
    return {"mean_pearson_r": float(rs.mean()), "top1_acc": float((top1_pred == top1_true).mean())}
