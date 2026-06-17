"""Emotion-specific evaluation metrics for D2.

fMRI-LM official 의 metrics/ 는 임상 binary classification (sex, AD 등) 위주라
emotion task (V/A regression, multilabel, soft distribution) 는 우리가 별도 정의.

D1 의 metric 과 schema 일치 (cross-direction 비교 용이).
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


def cat_multilabel_metrics(cat_pred: np.ndarray, cat_true: np.ndarray, threshold: float = 0.10) -> dict:
    bin_true = (cat_true >= threshold).astype(int)
    keep = (bin_true.sum(axis=0) > 0) & (bin_true.sum(axis=0) < bin_true.shape[0])
    auc = float(roc_auc_score(bin_true[:, keep], cat_pred[:, keep], average="macro"))
    return {"macro_auroc": auc, "threshold": threshold, "n_active_cats": int(keep.sum())}


def cat_soft_metrics(cat_pred: np.ndarray, cat_true: np.ndarray) -> dict:
    rs = [pearsonr(cat_pred[:, k], cat_true[:, k])[0] for k in range(cat_true.shape[1])]
    rs = np.nan_to_num(rs, nan=0.0)
    top1_pred = cat_pred.argmax(axis=1)
    top1_true = cat_true.argmax(axis=1)
    return {"mean_pearson_r": float(rs.mean()), "top1_acc": float((top1_pred == top1_true).mean())}
