"""34D Cowen-Keltner emotion label z-score normalization.

Implementation of `docs/notes/implementation_spec_20260702.md` §5-2.

Fit per-emotion mu and std on the train split only, apply the same statistics
to val and test. Test / val statistics must never be used to fit.

The 34 emotion order follows `project/shared/data/cowen34_order.txt`.

Raw data column convention (`cowen_horikawa_labels.csv`).
    score_0 ... score_33   34D emotion scores per stimulus (0-1 fraction of
                           rater agreement, not sum-to-1). Column index k
                           corresponds to emotion k in the canonical order.
    stim_idx               stimulus index (0-2184 for Horikawa 2185 canonical).

Usage.
    from project.data.labels import Cowen34Normalizer

    # Fit on train, save
    norm = Cowen34Normalizer()
    train_z = norm.fit_transform(train_labels)
    norm.save("project/shared/data/norm_stats/cowen34_train.pt")

    # Load elsewhere, transform test (no fit)
    norm = Cowen34Normalizer.load("project/shared/data/norm_stats/cowen34_train.pt")
    test_z = norm.transform(test_labels)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch


C = 34


class Cowen34Normalizer:
    """Per-emotion z-score normalizer for 34D Cowen-Keltner labels.

    Attributes.
        mu   (torch.Tensor)  shape (34,), per-emotion mean of the train split.
        std  (torch.Tensor)  shape (34,), per-emotion std of the train split.
    """

    def __init__(self, mu: torch.Tensor | None = None, std: torch.Tensor | None = None):
        self.mu = mu
        self.std = std

    def fit(self, train_labels: np.ndarray | torch.Tensor) -> "Cowen34Normalizer":
        """Fit mu and std from a train label matrix.

        Args.
            train_labels  array or tensor of shape (N_train, 34).

        Returns.
            self (fitted).
        """
        x = self._to_tensor(train_labels)
        assert x.ndim == 2 and x.shape[1] == C, f"expected (N, {C}), got {tuple(x.shape)}"
        self.mu = x.mean(dim=0)
        self.std = x.std(dim=0, unbiased=False)
        assert (self.std > 0).all(), "zero-variance emotion column in train split"
        return self

    def transform(self, labels: np.ndarray | torch.Tensor) -> torch.Tensor:
        """Apply z-score with previously fitted mu, std.

        Args.
            labels  array or tensor of shape (N, 34).

        Returns.
            z-scored tensor of shape (N, 34).
        """
        self._require_fitted()
        x = self._to_tensor(labels)
        assert x.ndim == 2 and x.shape[1] == C, f"expected (N, {C}), got {tuple(x.shape)}"
        return (x - self.mu) / self.std

    def fit_transform(self, train_labels: np.ndarray | torch.Tensor) -> torch.Tensor:
        """Fit on train_labels then return the z-scored train tensor."""
        self.fit(train_labels)
        return self.transform(train_labels)

    def inverse_transform(self, z_labels: np.ndarray | torch.Tensor) -> torch.Tensor:
        """Recover raw scale from z-scored values (reporting only, not training)."""
        self._require_fitted()
        z = self._to_tensor(z_labels)
        return z * self.std + self.mu

    def save(self, path: str | Path) -> None:
        """Serialize mu and std to a torch pt file."""
        self._require_fitted()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"mu": self.mu, "std": self.std, "emotion_dim": C}, path)

    @classmethod
    def load(cls, path: str | Path) -> "Cowen34Normalizer":
        """Load a previously saved normalizer."""
        state = torch.load(Path(path), map_location="cpu", weights_only=True)
        assert state["emotion_dim"] == C, f"emotion_dim mismatch: {state['emotion_dim']} != {C}"
        return cls(mu=state["mu"], std=state["std"])

    def _require_fitted(self) -> None:
        if self.mu is None or self.std is None:
            raise RuntimeError("Cowen34Normalizer is not fitted. Call .fit() or .load() first.")

    @staticmethod
    def _to_tensor(x: np.ndarray | torch.Tensor) -> torch.Tensor:
        if isinstance(x, torch.Tensor):
            return x.float()
        return torch.as_tensor(np.asarray(x), dtype=torch.float32)
