"""Supervised loss for 34D independent emotion regression.

Implementation of `docs/notes/implementation_spec_20260702.md` §8-1.

Core principle. The 34 emotions are NOT mutually exclusive (bittersweet =
joy and sadness both high). No softmax, no sum-to-1, no cross-entropy, no KL.
Each emotion is an independent regression target in z-space.

Loss.
    per-sample  = sum over 34 emotions of (pred_k - target_k)^2
    batch loss  = mean over batch of per-sample

    L_main(pred, target) = mean_b( sum_k (pred[b,k] - target[b,k])^2 )

Optional per-emotion weight (config loss.hard.per_emotion_weight) lets rare or
low-variance emotions contribute more. Default = uniform (all ones).

Curriculum subset (Track A/B stage 1-3, spec §8.9).
    An optional active-target mask A restricts the loss to a subset of the 34
    emotions (top-1, top-2, top-k). Non-active emotions get zero gradient.
    Full 34D (stage 4) uses no mask.

Usage.
    from project.models.losses.supervised import supervised_loss

    loss = supervised_loss(pred, target)                 # full 34D MSE
    loss = supervised_loss(pred, target, active=mask)    # curriculum subset
"""

from __future__ import annotations

import torch


C = 34


def supervised_loss(
    pred: torch.Tensor,
    target: torch.Tensor,
    active: torch.Tensor | None = None,
    per_emotion_weight: torch.Tensor | None = None,
    huber_delta: float | None = None,
) -> torch.Tensor:
    """Per-emotion MSE (or Huber) summed over emotions, averaged over batch.

    Args.
        pred                (B, 34) z-space predictions.
        target              (B, 34) z-space targets.
        active              (B, 34) or (34,) bool/float mask of emotions to
                            include (curriculum). None = all 34.
        per_emotion_weight  (34,) non-negative weights. None = uniform.
        huber_delta         if set, use Huber instead of squared error.

    Returns.
        scalar loss.
    """
    assert pred.shape == target.shape, f"shape mismatch {pred.shape} vs {target.shape}"
    assert pred.ndim == 2 and pred.shape[1] == C, f"expected (B, {C}), got {tuple(pred.shape)}"

    diff = pred - target  # (B, 34)

    if huber_delta is None:
        elem = diff ** 2  # (B, 34)
    else:
        assert huber_delta > 0
        abs_diff = diff.abs()
        quad = 0.5 * diff ** 2
        lin = huber_delta * (abs_diff - 0.5 * huber_delta)
        elem = torch.where(abs_diff <= huber_delta, quad, lin)  # (B, 34)

    if per_emotion_weight is not None:
        assert per_emotion_weight.shape == (C,), f"weight must be ({C},)"
        assert (per_emotion_weight >= 0).all()
        elem = elem * per_emotion_weight.view(1, C)

    if active is not None:
        active = active.to(elem.dtype)
        if active.ndim == 1:
            assert active.shape == (C,)
            active = active.view(1, C).expand_as(elem)
        else:
            assert active.shape == elem.shape, f"active must be (B, {C}) or ({C},)"
        elem = elem * active

    per_sample = elem.sum(dim=1)  # (B,)
    return per_sample.mean()
