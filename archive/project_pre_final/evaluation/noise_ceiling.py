"""Noise ceiling estimators for brain fMRI.

Implements the brain-side noise ceiling from
`docs/notes/architecture_design_20260629.md` §8.5 (revised 2026-07-07: Cowen
concordance is NOT used here; it is a categorical figure, not a continuous
ceiling).

Inter-Subject Correlation (ISC). 5 subjects saw the same stimuli. How
consistent is the brain response across subjects? Two complementary views.

    spatial ISC
        For one stimulus, correlate the 450-ROI response pattern between two
        subjects. "Is the spatial brain pattern for this stimulus similar
        across subjects?" Averaged over subject pairs, then over stimuli.

    per-ROI ISC (canonical ISC)
        For one ROI, correlate its response profile across stimuli between two
        subjects. "Does this brain region respond consistently to stimuli
        across subjects?" Averaged over subject pairs -> per-ROI ISC map.

ISC is not an emotion-decoding ceiling; it measures stimulus-driven
consistency of the brain signal. But it bounds how much shared signal a pooled
decoder can exploit: low ISC => brain response is idiosyncratic (R0 risk),
high ISC => shared signal exists and a better model may extract more.

Usage.
    from project.evaluation.noise_ceiling import spatial_isc, per_roi_isc
    s = spatial_isc(X)        # X: (n_subj, n_stim, n_roi)
    r = per_roi_isc(X)
"""

from __future__ import annotations

import numpy as np
from itertools import combinations


def _pearson_rows(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Row-wise Pearson correlation between two (M, D) arrays -> (M,)."""
    A = A - A.mean(axis=1, keepdims=True)
    B = B - B.mean(axis=1, keepdims=True)
    num = (A * B).sum(axis=1)
    den = np.sqrt((A * A).sum(axis=1) * (B * B).sum(axis=1))
    out = np.full(A.shape[0], np.nan)
    ok = den > 1e-12
    out[ok] = num[ok] / den[ok]
    return out


def spatial_isc(X: np.ndarray) -> dict:
    """Per-stimulus spatial-pattern ISC across subject pairs.

    Args.
        X  (n_subj, n_stim, n_roi).

    Returns.
        dict(per_stim (n_stim,), mean, median, std, n_pairs).
    """
    n_subj, n_stim, n_roi = X.shape
    pair_stim = []  # (n_pairs, n_stim)
    for i, j in combinations(range(n_subj), 2):
        # correlate the 450-vector per stimulus between subj i and j
        r = _pearson_rows(X[i], X[j])  # (n_stim,)
        pair_stim.append(r)
    pair_stim = np.stack(pair_stim, axis=0)  # (n_pairs, n_stim)
    per_stim = np.nanmean(pair_stim, axis=0)  # (n_stim,)
    return {
        "per_stim": per_stim,
        "mean": float(np.nanmean(per_stim)),
        "median": float(np.nanmedian(per_stim)),
        "std": float(np.nanstd(per_stim)),
        "n_pairs": int(pair_stim.shape[0]),
    }


def per_roi_isc(X: np.ndarray) -> dict:
    """Per-ROI ISC (canonical). Correlate each ROI's stimulus profile across
    subject pairs.

    Args.
        X  (n_subj, n_stim, n_roi).

    Returns.
        dict(per_roi (n_roi,), mean, median, top_roi_idx, n_pairs).
    """
    n_subj, n_stim, n_roi = X.shape
    # transpose to (n_subj, n_roi, n_stim) so rows are ROI profiles
    Xt = np.transpose(X, (0, 2, 1))  # (n_subj, n_roi, n_stim)
    pair_roi = []
    for i, j in combinations(range(n_subj), 2):
        r = _pearson_rows(Xt[i], Xt[j])  # (n_roi,)
        pair_roi.append(r)
    pair_roi = np.stack(pair_roi, axis=0)  # (n_pairs, n_roi)
    per_roi = np.nanmean(pair_roi, axis=0)  # (n_roi,)
    top = np.argsort(per_roi)[::-1][:10]
    return {
        "per_roi": per_roi,
        "mean": float(np.nanmean(per_roi)),
        "median": float(np.nanmedian(per_roi)),
        "top_roi_idx": [int(i) for i in top],
        "top_roi_val": [float(per_roi[i]) for i in top],
        "n_pairs": int(pair_roi.shape[0]),
    }
