"""Structure loss. Match the 34x34 emotion correlation structure.

Implementation of `docs/notes/implementation_spec_20260702.md` §8-1 (optional).

Motivation. The supervised (per-emotion MSE) loss trains each emotion
independently and does NOT directly enforce inter-emotion relationships
(e.g., joy-nostalgia positively correlated, joy-fear negatively). A model can
fit individual values yet invert the correlation structure. This loss makes
the predicted 34x34 emotion correlation matrix match the target's.

    C_pred[i,j]   = corr over batch of pred[:,i] and pred[:,j]
    C_target[i,j] = corr over batch of target[:,i] and target[:,j]
    L_struct      = mean over (i,j) of (C_pred[i,j] - C_target[i,j])^2

Default OFF. Enabled via config loss.structure.enabled with lambda_struct.
Total loss = lambda_hard * L_main + lambda_struct * L_struct.

CAUTION. Correlation over a batch needs enough samples. Batch < min_batch is
rejected because correlation on tiny batches is ~ +/-1 and unstable.

Usage.
    from project.models.losses.structure import structure_loss
    loss = structure_loss(pred, target)   # scalar, 0 if structure matches
"""

from __future__ import annotations

import torch


C = 34
MIN_BATCH = 4


def _corr_matrix(x: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """Pearson correlation matrix over the batch dimension.

    Args.
        x  (B, 34).

    Returns.
        (34, 34) correlation matrix.
    """
    x = x - x.mean(dim=0, keepdim=True)  # center per emotion
    std = x.std(dim=0, unbiased=False, keepdim=True)  # (1, 34)
    x = x / (std + eps)
    B = x.shape[0]
    return (x.t() @ x) / B  # (34, 34)


def structure_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    min_batch: int = MIN_BATCH,
) -> torch.Tensor:
    """MSE between predicted and target 34x34 correlation matrices.

    Args.
        pred       (B, 34) z-space predictions.
        target     (B, 34) z-space targets.
        min_batch  minimum batch size for a stable correlation.

    Returns.
        scalar loss (0 if structures match exactly).
    """
    assert pred.shape == target.shape, f"shape mismatch {pred.shape} vs {target.shape}"
    assert pred.ndim == 2 and pred.shape[1] == C, f"expected (B, {C}), got {tuple(pred.shape)}"
    assert pred.shape[0] >= min_batch, (
        f"structure_loss needs batch >= {min_batch}, got {pred.shape[0]}. "
        "Correlation on tiny batches is unstable."
    )

    c_pred = _corr_matrix(pred)
    c_target = _corr_matrix(target)
    return ((c_pred - c_target) ** 2).mean()
