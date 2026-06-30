"""ABCD-pretrained vs Horikawa token distribution analysis.

If ABCD pretrained BrainVLM weight becomes available, compare token-mean / token-std /
KL of token activation distribution to detect zero-shot transferability.
Placeholder until pretrained ckpt arrives.
"""
from __future__ import annotations

import numpy as np


def token_kl_divergence(tokens_a: np.ndarray, tokens_b: np.ndarray, n_bins: int = 50) -> float:
    """Histogram-based symmetric KL on flat token activation."""
    a, b = tokens_a.flatten(), tokens_b.flatten()
    lo, hi = float(min(a.min(), b.min())), float(max(a.max(), b.max()))
    pa, _ = np.histogram(a, bins=n_bins, range=(lo, hi), density=True)
    pb, _ = np.histogram(b, bins=n_bins, range=(lo, hi), density=True)
    pa, pb = pa + 1e-12, pb + 1e-12
    pa, pb = pa / pa.sum(), pb / pb.sum()
    return float(0.5 * ((pa * np.log(pa / pb)).sum() + (pb * np.log(pb / pa)).sum()))
