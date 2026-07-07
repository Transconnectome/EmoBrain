"""Evaluation metrics for 34D emotion prediction.

Implementation of `docs/notes/implementation_spec_20260702.md` §9.

Loss vs metric. Loss drives training; metrics are the report card. The
headline is NOT per-value accuracy but whether the 34D emotion PROFILE of one
clip matches the target profile.

Metrics.
    profile_correlation   HEADLINE. Per-clip 34D Pearson + Spearman, mean over
                          clips. "Does this clip's emotion shape match?"
    per_emotion_correlation  Per-emotion Pearson across clips + rare subset.
                          "Is each emotion (incl. rare ones) decodable?"
    rsa                   Upper-triangle Pearson between predicted and target
                          34x34 correlation matrices. Structure preservation.
    dim_compression_curve PCA-reduce to k dims, measure profile correlation
                          retained. Tests whether high-D structure is real.

All inputs are (N, 34) in z-space. Clips whose vector is constant (zero std)
have undefined correlation; those clips are skipped and counted, never NaN.

Usage.
    from project.evaluation.metrics import profile_correlation, compute_metrics
    m = profile_correlation(pred, target)     # {pearson_mean, spearman_mean, ...}
    all_m = compute_metrics(pred, target, which=["profile", "rsa"])
"""

from __future__ import annotations

import numpy as np
import torch
from scipy.stats import spearmanr

C = 34
_RARE_DEFAULT_K = 10


def _to_np(x: torch.Tensor | np.ndarray) -> np.ndarray:
    if isinstance(x, torch.Tensor):
        return x.detach().cpu().numpy().astype(np.float64)
    return np.asarray(x, dtype=np.float64)


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson r between two 1D arrays. NaN if either is constant."""
    a = a - a.mean()
    b = b - b.mean()
    denom = np.sqrt((a * a).sum() * (b * b).sum())
    if denom < 1e-12:
        return np.nan
    return float((a * b).sum() / denom)


def profile_correlation(pred, target) -> dict:
    """HEADLINE. Per-clip 34D profile Pearson + Spearman, mean over clips.

    Args.
        pred, target  (N, 34).

    Returns.
        dict(pearson_mean, spearman_mean, n_used, n_skipped).
    """
    p = _to_np(pred)
    t = _to_np(target)
    assert p.shape == t.shape and p.shape[1] == C

    pearsons, spearmans, skipped = [], [], 0
    for i in range(p.shape[0]):
        r = _pearson(p[i], t[i])
        if np.isnan(r):
            skipped += 1
            continue
        pearsons.append(r)
        rho, _ = spearmanr(p[i], t[i])
        spearmans.append(rho if not np.isnan(rho) else 0.0)

    return {
        "pearson_mean": float(np.mean(pearsons)) if pearsons else float("nan"),
        "spearman_mean": float(np.mean(spearmans)) if spearmans else float("nan"),
        "n_used": len(pearsons),
        "n_skipped": skipped,
    }


def per_emotion_correlation(pred, target, rare_idx: list[int] | None = None) -> dict:
    """Per-emotion Pearson across clips. Mean + rare-emotion subset mean.

    Args.
        pred, target  (N, 34).
        rare_idx      indices of rare emotions. If None, no rare breakdown.

    Returns.
        dict(per_emotion (34,), mean, rare_mean, n_skipped).
    """
    p = _to_np(pred)
    t = _to_np(target)
    assert p.shape == t.shape and p.shape[1] == C

    per_emotion = np.full(C, np.nan)
    for k in range(C):
        per_emotion[k] = _pearson(p[:, k], t[:, k])

    valid = per_emotion[~np.isnan(per_emotion)]
    out = {
        "per_emotion": per_emotion.tolist(),
        "mean": float(valid.mean()) if valid.size else float("nan"),
        "n_skipped": int(np.isnan(per_emotion).sum()),
    }
    if rare_idx is not None:
        rare_vals = per_emotion[rare_idx]
        rare_valid = rare_vals[~np.isnan(rare_vals)]
        out["rare_mean"] = float(rare_valid.mean()) if rare_valid.size else float("nan")
    return out


def _corr_matrix(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    x = x - x.mean(axis=0, keepdims=True)
    std = x.std(axis=0, keepdims=True)
    x = x / (std + eps)
    return (x.T @ x) / x.shape[0]  # (34, 34)


def rsa(pred, target) -> dict:
    """Upper-triangle Pearson between predicted and target 34x34 corr matrices.

    Returns.
        dict(rsa_pearson, n_pairs).
    """
    p = _to_np(pred)
    t = _to_np(target)
    assert p.shape == t.shape and p.shape[1] == C
    cp = _corr_matrix(p)
    ct = _corr_matrix(t)
    iu = np.triu_indices(C, k=1)
    r = _pearson(cp[iu], ct[iu])
    return {"rsa_pearson": r, "n_pairs": len(iu[0])}


def dim_compression_curve(pred, target, ks: list[int] | None = None) -> dict:
    """PCA-reduce target profiles to k dims, measure retained profile corr.

    For each k, project both pred and target onto the top-k principal
    directions of the target, then compute mean per-clip profile Pearson in
    that reduced space. A curve that saturates early => low intrinsic dim.

    Returns.
        dict(ks, pearson_at_k).
    """
    from sklearn.decomposition import PCA

    p = _to_np(pred)
    t = _to_np(target)
    assert p.shape == t.shape and p.shape[1] == C
    if ks is None:
        ks = [1, 2, 3, 5, 8, 13, 21, 34]

    pca = PCA(n_components=C)
    pca.fit(t)
    comps = pca.components_  # (34, 34)

    pearson_at_k = []
    for k in ks:
        proj = comps[:k]  # (k, 34)
        p_red = p @ proj.T  # (N, k)
        t_red = t @ proj.T
        rs = []
        for i in range(p_red.shape[0]):
            if k == 1:
                # Single dim: correlation over one number is undefined; use
                # sign agreement as a degenerate proxy.
                rs.append(1.0 if np.sign(p_red[i, 0]) == np.sign(t_red[i, 0]) else 0.0)
            else:
                r = _pearson(p_red[i], t_red[i])
                if not np.isnan(r):
                    rs.append(r)
        pearson_at_k.append(float(np.mean(rs)) if rs else float("nan"))

    return {"ks": list(ks), "pearson_at_k": pearson_at_k}


def compute_metrics(pred, target, which: list[str] | None = None, rare_idx=None) -> dict:
    """Dispatcher. Run selected metrics and return a flat dict.

    Args.
        which  subset of ["profile", "per_emotion", "rsa", "dim_compression"].
               None = all.
    """
    if which is None:
        which = ["profile", "per_emotion", "rsa", "dim_compression"]
    out: dict = {}
    if "profile" in which:
        out["profile"] = profile_correlation(pred, target)
    if "per_emotion" in which:
        out["per_emotion"] = per_emotion_correlation(pred, target, rare_idx=rare_idx)
    if "rsa" in which:
        out["rsa"] = rsa(pred, target)
    if "dim_compression" in which:
        out["dim_compression"] = dim_compression_curve(pred, target)
    return out
