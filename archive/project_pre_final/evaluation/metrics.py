"""Evaluation metrics for 34D emotion prediction.

Implementation of `docs/notes/implementation_spec_20260702.md` §9, extended to
report every reasonable metric (loss is one number, evaluation should be rich).

Loss vs metric. Loss drives training; metrics are the report card. The headline
is per-clip 34D profile correlation (does the emotion SHAPE match), but we also
report absolute error (MSE/MAE), regression fit (R2), structure (RSA), and
sparse-aware retrieval (the labels are ~74% zero).

Why CCC in addition to Pearson and MSE.
    Pearson measures only SHAPE (a prediction scaled to half the target still
    scores 1.0). MSE measures VALUE but is blunt on our labels (73.8% zero, so
    "predict all zero" already has low MSE). CCC combines both: it penalizes
    both shape mismatch and scale/bias mismatch, so a good-shape but
    miscalibrated prediction is correctly downweighted. All three are reported.

Metric families.
    profile_correlation      HEADLINE. per-clip 34D Pearson + Spearman + cosine
                             + CCC.
    error                    MSE / MAE / R2 in z-space (+ raw space if a
                             normalizer is given).
    per_emotion_correlation  per-emotion Pearson + CCC across clips + rare subset.
    rsa                      upper-triangle Pearson of 34x34 corr matrices.
    dim_compression_curve    PCA-reduced profile correlation retained per k.
    sparse_retrieval         top-k emotion retrieval (labels are sparse):
                             precision@k / recall@k / Jaccard vs the clip's
                             truly-active emotions.

All inputs are (N, 34) in z-space. compute_metrics() runs any subset.

Usage.
    from project.evaluation.metrics import compute_metrics
    m = compute_metrics(pred, target)                       # all families
    m = compute_metrics(pred, target, which=["profile", "error"])
    m = compute_metrics(pred, target, normalizer=norm)      # adds raw-space error
"""

from __future__ import annotations

import numpy as np
import torch
from scipy.stats import spearmanr

C = 34
_RARE_DEFAULT_K = 10


def _to_np(x) -> np.ndarray:
    if isinstance(x, torch.Tensor):
        return x.detach().cpu().numpy().astype(np.float64)
    return np.asarray(x, dtype=np.float64)


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    a = a - a.mean()
    b = b - b.mean()
    denom = np.sqrt((a * a).sum() * (b * b).sum())
    if denom < 1e-12:
        return np.nan
    return float((a * b).sum() / denom)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.sqrt((a * a).sum() * (b * b).sum())
    if denom < 1e-12:
        return np.nan
    return float((a * b).sum() / denom)


def _ccc(pred: np.ndarray, true: np.ndarray) -> float:
    """Concordance Correlation Coefficient between two 1D arrays.

    CCC = 2*rho*sx*sy / (sx^2 + sy^2 + (mx - my)^2)

    Penalizes both shape mismatch (via rho) and scale/bias mismatch (via the
    variance and mean-difference terms). Standard metric for dimensional
    emotion recognition (AVEC). Range [-1, 1]; 1 iff identical distribution.
    """
    mx, my = pred.mean(), true.mean()
    sx2, sy2 = pred.var(), true.var()
    cov = ((pred - mx) * (true - my)).mean()
    denom = sx2 + sy2 + (mx - my) ** 2
    if denom < 1e-12:
        return np.nan
    return float(2 * cov / denom)


# ---------------------------------------------------------------- headline

def profile_correlation(pred, target) -> dict:
    """HEADLINE. Per-clip 34D Pearson + Spearman + cosine + CCC, mean over clips.

    Pearson = shape only. CCC = shape AND value/scale (stricter). Reporting both
    shows whether a good-shape prediction is also well-calibrated in magnitude.
    """
    p = _to_np(pred)
    t = _to_np(target)
    assert p.shape == t.shape and p.shape[1] == C

    pearsons, spearmans, cosines, cccs, skipped = [], [], [], [], 0
    for i in range(p.shape[0]):
        r = _pearson(p[i], t[i])
        if np.isnan(r):
            skipped += 1
            continue
        pearsons.append(r)
        rho, _ = spearmanr(p[i], t[i])
        spearmans.append(rho if not np.isnan(rho) else 0.0)
        cosines.append(_cosine(p[i], t[i]))
        c = _ccc(p[i], t[i])
        if not np.isnan(c):
            cccs.append(c)

    return {
        "pearson_mean": float(np.mean(pearsons)) if pearsons else float("nan"),
        "pearson_median": float(np.median(pearsons)) if pearsons else float("nan"),
        "spearman_mean": float(np.mean(spearmans)) if spearmans else float("nan"),
        "cosine_mean": float(np.mean(cosines)) if cosines else float("nan"),
        "ccc_mean": float(np.mean(cccs)) if cccs else float("nan"),
        "n_used": len(pearsons),
        "n_skipped": skipped,
    }


# ---------------------------------------------------------------- error

def error(pred, target, normalizer=None) -> dict:
    """MSE / MAE / R2 in z-space, plus raw space if a normalizer is given.

    R2 is the coefficient of determination against the per-emotion mean, so
    R2 > 0 means better than predicting the training mean (0 in z-space).
    """
    p = _to_np(pred)
    t = _to_np(target)
    assert p.shape == t.shape and p.shape[1] == C

    diff = p - t
    mse = float((diff ** 2).mean())
    mae = float(np.abs(diff).mean())

    # R2 against per-emotion mean of target.
    ss_res = (diff ** 2).sum(axis=0)  # (34,)
    ss_tot = ((t - t.mean(axis=0, keepdims=True)) ** 2).sum(axis=0)  # (34,)
    r2_per = 1.0 - ss_res / np.where(ss_tot < 1e-12, np.nan, ss_tot)
    r2_mean = float(np.nanmean(r2_per))

    # baseline: predict all-zero (= per-emotion train mean in z-space).
    zero_mse = float((t ** 2).mean())
    zero_mae = float(np.abs(t).mean())

    out = {
        "mse_z": mse,
        "mae_z": mae,
        "r2_mean_z": r2_mean,
        "zero_pred_mse_z": zero_mse,
        "zero_pred_mae_z": zero_mae,
        "mse_improve_vs_zero": zero_mse - mse,
    }

    if normalizer is not None:
        p_raw = _to_np(normalizer.inverse_transform(p))
        t_raw = _to_np(normalizer.inverse_transform(t))
        draw = p_raw - t_raw
        out["mse_raw"] = float((draw ** 2).mean())
        out["mae_raw"] = float(np.abs(draw).mean())

    return out


# ---------------------------------------------------------------- per emotion

def per_emotion_correlation(pred, target, rare_idx=None) -> dict:
    """Per-emotion Pearson across clips. Mean + rare subset mean + full list."""
    p = _to_np(pred)
    t = _to_np(target)
    assert p.shape == t.shape and p.shape[1] == C

    per_emotion = np.full(C, np.nan)
    per_emotion_ccc = np.full(C, np.nan)
    for k in range(C):
        per_emotion[k] = _pearson(p[:, k], t[:, k])
        per_emotion_ccc[k] = _ccc(p[:, k], t[:, k])

    valid = per_emotion[~np.isnan(per_emotion)]
    valid_ccc = per_emotion_ccc[~np.isnan(per_emotion_ccc)]
    out = {
        "per_emotion": per_emotion.tolist(),
        "per_emotion_ccc": per_emotion_ccc.tolist(),
        "mean": float(valid.mean()) if valid.size else float("nan"),
        "median": float(np.median(valid)) if valid.size else float("nan"),
        "min": float(valid.min()) if valid.size else float("nan"),
        "max": float(valid.max()) if valid.size else float("nan"),
        "ccc_mean": float(valid_ccc.mean()) if valid_ccc.size else float("nan"),
        "n_skipped": int(np.isnan(per_emotion).sum()),
    }
    if rare_idx is not None:
        rare_vals = per_emotion[rare_idx]
        rare_valid = rare_vals[~np.isnan(rare_vals)]
        out["rare_mean"] = float(rare_valid.mean()) if rare_valid.size else float("nan")
        rare_ccc = per_emotion_ccc[rare_idx]
        rare_ccc_valid = rare_ccc[~np.isnan(rare_ccc)]
        out["rare_ccc_mean"] = float(rare_ccc_valid.mean()) if rare_ccc_valid.size else float("nan")
    return out


# ---------------------------------------------------------------- structure

def _corr_matrix(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    x = x - x.mean(axis=0, keepdims=True)
    std = x.std(axis=0, keepdims=True)
    x = x / (std + eps)
    return (x.T @ x) / x.shape[0]


def rsa(pred, target) -> dict:
    """Upper-triangle Pearson between predicted and target 34x34 corr matrices."""
    p = _to_np(pred)
    t = _to_np(target)
    assert p.shape == t.shape and p.shape[1] == C
    cp = _corr_matrix(p)
    ct = _corr_matrix(t)
    iu = np.triu_indices(C, k=1)
    return {"rsa_pearson": _pearson(cp[iu], ct[iu]), "n_pairs": len(iu[0])}


def dim_compression_curve(pred, target, ks=None) -> dict:
    """PCA-reduce onto target's top-k directions; retained profile correlation."""
    from sklearn.decomposition import PCA

    p = _to_np(pred)
    t = _to_np(target)
    assert p.shape == t.shape and p.shape[1] == C
    if ks is None:
        ks = [1, 2, 3, 5, 8, 13, 21, 34]

    comps = PCA(n_components=C).fit(t).components_
    pearson_at_k = []
    for k in ks:
        proj = comps[:k]
        p_red = p @ proj.T
        t_red = t @ proj.T
        rs = []
        for i in range(p_red.shape[0]):
            if k == 1:
                rs.append(1.0 if np.sign(p_red[i, 0]) == np.sign(t_red[i, 0]) else 0.0)
            else:
                r = _pearson(p_red[i], t_red[i])
                if not np.isnan(r):
                    rs.append(r)
        pearson_at_k.append(float(np.mean(rs)) if rs else float("nan"))
    return {"ks": list(ks), "pearson_at_k": pearson_at_k}


# ---------------------------------------------------------------- sparse

def sparse_retrieval(pred, target, ks=(1, 3, 5), active_threshold=0.0) -> dict:
    """Top-k emotion retrieval. Labels are sparse (~74% zero), so besides the
    correlation view we ask: does the model surface the RIGHT active emotions?

    For each clip the "true active" set = emotions above active_threshold in
    z-space relative to the clip (we use target rank, not an absolute cut, to
    stay scale-free): the top-|active| target emotions where target is among
    the highest. In practice we score precision/recall of the model's top-k
    predicted emotions against the target's top-k.
    """
    p = _to_np(pred)
    t = _to_np(target)
    assert p.shape == t.shape and p.shape[1] == C
    N = p.shape[0]

    out = {}
    for k in ks:
        prec, rec, jac = [], [], []
        for i in range(N):
            pred_top = set(np.argsort(p[i])[::-1][:k].tolist())
            true_top = set(np.argsort(t[i])[::-1][:k].tolist())
            inter = len(pred_top & true_top)
            union = len(pred_top | true_top)
            prec.append(inter / k)
            rec.append(inter / k)  # |true_top| == k so recall == precision here
            jac.append(inter / union if union else 0.0)
        out[f"precision@{k}"] = float(np.mean(prec))
        out[f"jaccard@{k}"] = float(np.mean(jac))
    return out


# ---------------------------------------------------------------- dispatcher

_ALL = ["profile", "error", "per_emotion", "rsa", "dim_compression", "sparse"]


def compute_metrics(pred, target, which=None, rare_idx=None, normalizer=None) -> dict:
    """Run selected metric families and return a nested dict.

    which  subset of ["profile","error","per_emotion","rsa","dim_compression",
           "sparse"]. None = all.
    """
    if which is None:
        which = list(_ALL)
    out: dict = {}
    if "profile" in which:
        out["profile"] = profile_correlation(pred, target)
    if "error" in which:
        out["error"] = error(pred, target, normalizer=normalizer)
    if "per_emotion" in which:
        out["per_emotion"] = per_emotion_correlation(pred, target, rare_idx=rare_idx)
    if "rsa" in which:
        out["rsa"] = rsa(pred, target)
    if "dim_compression" in which:
        out["dim_compression"] = dim_compression_curve(pred, target)
    if "sparse" in which:
        out["sparse"] = sparse_retrieval(pred, target)
    return out
