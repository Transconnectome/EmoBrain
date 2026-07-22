"""Losses for independent, continuous emotion-profile regression.

supervised    L_sup = mean_c (pred - true)^2 over the active target subset
              (curriculum stage). Huber optional (spec OPEN).
distillation  L_dist = mean_c (student - teacher)^2 on the teacher's 34D output.
              Teacher outputs stay continuous; no softmax or KL is applied.

active_mask (B, 34) or None selects the curriculum-stage target subset; masked
emotions get no gradient but the head still emits all 34 (spec §8.3.1).
"""

from __future__ import annotations

import torch
import torch.nn.functional as F


def _masked_mean(sq, mask):
    if mask is None:
        return sq.mean()
    m = mask.to(sq.dtype)
    return (sq * m).sum() / m.sum().clamp_min(1.0)


def ccc_loss(pred, target, eps=1e-8):
    """1 - per-clip CCC, averaged over clips. Directly optimises the headline
    metric (per-clip 34D profile CCC = shape + scale + bias), which per-emotion
    MSE does not. CCC = 2*cov / (var_x + var_y + (mean_x - mean_y)^2), computed
    over the 34 emotions within each clip. Curriculum masking is not applied
    here (CCC needs the full profile); combine with masked MSE if a subset stage
    also wants a shape term.
    """
    mx = pred.mean(dim=1, keepdim=True)
    my = target.mean(dim=1, keepdim=True)
    xc, yc = pred - mx, target - my
    vx = (xc * xc).mean(dim=1)
    vy = (yc * yc).mean(dim=1)
    cov = (xc * yc).mean(dim=1)
    ccc = 2 * cov / (vx + vy + (mx.squeeze(1) - my.squeeze(1)) ** 2 + eps)
    return 1.0 - ccc.mean()


def supervised_loss(pred, target, active_mask=None, kind="mse", huber_beta=1.0,
                    ccc_weight=1.0):
    """kind. mse | huber | ccc | mse+ccc.

    mse+ccc = masked per-emotion MSE (value + curriculum subset) plus a per-clip
    CCC term (shape + scale). MSE keeps the sparse labels anchored, CCC pushes
    the profile shape that Pearson-only training would leave miscalibrated.
    """
    if kind == "ccc":
        return ccc_loss(pred, target)
    if kind == "huber":
        sq = F.huber_loss(pred, target, reduction="none", delta=huber_beta)
    else:
        sq = (pred - target) ** 2
    mse = _masked_mean(sq, active_mask)
    if kind == "mse+ccc":
        return mse + ccc_weight * ccc_loss(pred, target)
    return mse


def distillation_loss(student_pred, teacher_pred, active_mask=None, kind="mse",
                      temperature=1.0):
    del temperature
    if kind != "mse":
        raise ValueError(f"distillation kind must be 'mse', got {kind!r}")
    return _masked_mean((student_pred - teacher_pred) ** 2, active_mask)


def total_student_loss(student_pred, target, teacher_pred=None, active_mask=None,
                       lambda_hard=1.0, lambda_dist=1.0, **kw):
    L = lambda_hard * supervised_loss(student_pred, target, active_mask,
                                      kind=kw.get("hard_kind", "mse"),
                                      ccc_weight=kw.get("ccc_weight", 1.0))
    if teacher_pred is not None and lambda_dist > 0:
        L = L + lambda_dist * distillation_loss(
            student_pred, teacher_pred, active_mask,
            kind=kw.get("distill_kind", "mse"), temperature=kw.get("temperature", 1.0))
    return L
