"""Emotion task evaluation. V/A regression, Cat34 multilabel, Cat34 soft distribution.

design.md Section 7. Baselines (Phase 1 ROI mean + Ridge, BJ resting frozen) reported alongside.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import roc_auc_score


def va_regression_metrics(va_pred: np.ndarray, va_true: np.ndarray) -> dict:
    r_v, _ = pearsonr(va_pred[:, 0], va_true[:, 0])
    r_a, _ = pearsonr(va_pred[:, 1], va_true[:, 1])
    mae_v = float(np.abs(va_pred[:, 0] - va_true[:, 0]).mean())
    mae_a = float(np.abs(va_pred[:, 1] - va_true[:, 1]).mean())
    return {"r_valence": r_v, "r_arousal": r_a, "mae_valence": mae_v, "mae_arousal": mae_a}


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
