"""Multi-task loss: L = L_CE(caption) + lambda1 * L_MSE(V/A) + lambda2 * L_KL(Cat34).

Pilot lambdas. lambda1 = 1.0, lambda2 = 0.5 (design.md Section 5).
"""
from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as F


@dataclass
class MultiTaskWeights:
    lambda_va: float = 1.0
    lambda_cat34: float = 0.5


def va_mse_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return F.mse_loss(pred, target)


def cat34_kl_loss(logits: torch.Tensor, target_dist: torch.Tensor) -> torch.Tensor:
    log_p = F.log_softmax(logits, dim=-1)
    return F.kl_div(log_p, target_dist, reduction="batchmean")


def total_loss(
    caption_ce: torch.Tensor,
    va_pred: torch.Tensor,
    va_tgt: torch.Tensor,
    cat34_logits: torch.Tensor,
    cat34_tgt: torch.Tensor,
    weights: MultiTaskWeights = MultiTaskWeights(),
) -> dict:
    l_va = va_mse_loss(va_pred, va_tgt)
    l_cat = cat34_kl_loss(cat34_logits, cat34_tgt)
    total = caption_ce + weights.lambda_va * l_va + weights.lambda_cat34 * l_cat
    return {"total": total, "ce_cap": caption_ce, "mse_va": l_va, "kl_cat34": l_cat}
