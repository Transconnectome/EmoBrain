"""34D Cowen-Keltner emotion label normalization.

Implementation of `docs/notes/implementation_spec_20260702.md` §5-2.

Fit per-emotion statistics on the train split only, apply the same statistics
to val and test. Test / val statistics must never be used to fit.

The 34 emotion order follows `project/shared/data/cowen34_order.txt`.

Two transform modes (both per-emotion, fit on train only).
    zscore     z = (raw - mu) / std.
    log1p_z    z = (log1p(raw) - mu_log) / std_log. Compresses the heavy tail
               of the crowd-proportion labels (73.8% zero, rare extremes) while
               preserving rank. Chosen default 2026-07-07 (marginal but
               balanced improvement on rare emotions + gentler extremes for NN
               training; see docs/notes/build_log.md Cycle 12).

Raw data column convention (`cowen_horikawa_labels.csv`).
    score_0 ... score_33   34D crowd-proportion labels (fraction of raters who
                           chose that emotion, 0-1, NOT sum-to-1). Column index
                           k corresponds to emotion k in the canonical order.

Usage.
    from project.data.labels import Cowen34Normalizer

    norm = Cowen34Normalizer(mode="log1p_z")
    train_z = norm.fit_transform(train_labels)
    norm.save("project/shared/data/norm_stats/cowen34_train_log1p_z.pt")

    norm = Cowen34Normalizer.load(".../cowen34_train_log1p_z.pt")   # mode restored
    test_z = norm.transform(test_labels)
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
import torch


C = 34
Mode = Literal["zscore", "log1p_z"]


class Cowen34Normalizer:
    """Per-emotion normalizer for 34D Cowen-Keltner crowd-proportion labels.

    Attributes.
        mode  "zscore" | "log1p_z".
        mu    (torch.Tensor)  shape (34,), per-emotion mean (of raw or log1p).
        std   (torch.Tensor)  shape (34,), per-emotion std.
    """

    def __init__(self, mode: Mode = "log1p_z",
                 mu: torch.Tensor | None = None, std: torch.Tensor | None = None):
        assert mode in ("zscore", "log1p_z"), f"unknown mode {mode!r}"
        self.mode = mode
        self.mu = mu
        self.std = std

    def _base(self, x: torch.Tensor) -> torch.Tensor:
        """Apply the pre-standardization transform (identity or log1p)."""
        if self.mode == "log1p_z":
            return torch.log1p(x)
        return x

    def fit(self, train_labels: np.ndarray | torch.Tensor) -> "Cowen34Normalizer":
        """Fit mu and std from a train label matrix (after the mode transform)."""
        x = self._base(self._to_tensor(train_labels))
        assert x.ndim == 2 and x.shape[1] == C, f"expected (N, {C}), got {tuple(x.shape)}"
        self.mu = x.mean(dim=0)
        self.std = x.std(dim=0, unbiased=False)
        assert (self.std > 0).all(), "zero-variance emotion column in train split"
        return self

    def transform(self, labels: np.ndarray | torch.Tensor) -> torch.Tensor:
        """Apply the mode transform then z-score with fitted mu, std."""
        self._require_fitted()
        x = self._base(self._to_tensor(labels))
        assert x.ndim == 2 and x.shape[1] == C, f"expected (N, {C}), got {tuple(x.shape)}"
        return (x - self.mu) / self.std

    def fit_transform(self, train_labels: np.ndarray | torch.Tensor) -> torch.Tensor:
        self.fit(train_labels)
        return self.transform(train_labels)

    def inverse_transform(self, z_labels: np.ndarray | torch.Tensor) -> torch.Tensor:
        """Recover raw scale from z-scored values (reporting only, not training)."""
        self._require_fitted()
        z = self._to_tensor(z_labels)
        base = z * self.std + self.mu
        if self.mode == "log1p_z":
            return torch.expm1(base)
        return base

    def save(self, path: str | Path) -> None:
        self._require_fitted()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"mode": self.mode, "mu": self.mu, "std": self.std, "emotion_dim": C}, path)

    @classmethod
    def load(cls, path: str | Path) -> "Cowen34Normalizer":
        state = torch.load(Path(path), map_location="cpu", weights_only=True)
        assert state["emotion_dim"] == C, f"emotion_dim mismatch: {state['emotion_dim']} != {C}"
        return cls(mode=state.get("mode", "zscore"), mu=state["mu"], std=state["std"])

    def _require_fitted(self) -> None:
        if self.mu is None or self.std is None:
            raise RuntimeError("Cowen34Normalizer is not fitted. Call .fit() or .load() first.")

    @staticmethod
    def _to_tensor(x: np.ndarray | torch.Tensor) -> torch.Tensor:
        if isinstance(x, torch.Tensor):
            return x.float()
        return torch.as_tensor(np.asarray(x), dtype=torch.float32)
