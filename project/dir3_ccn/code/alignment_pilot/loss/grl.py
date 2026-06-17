"""Gradient Reversal Layer + adversarial modality loss.

The GRL passes the input through unchanged on forward but multiplies the
gradient by -lambda on backward. The modality discriminator is trained to
classify (brain=0, video=1) on z, while the projection heads (upstream of GRL)
get a reversed gradient that pushes them to make z modality-indistinguishable.

This is the fMRI-LM Stage 1 trick. It explicitly shrinks the modality gap
between projected brain and projected video.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Function


class _GradReverse(Function):
    @staticmethod
    def forward(ctx, x: torch.Tensor, lambd: float) -> torch.Tensor:
        ctx.lambd = lambd
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output: torch.Tensor):
        return -ctx.lambd * grad_output, None


def grad_reverse(x: torch.Tensor, lambd: float) -> torch.Tensor:
    return _GradReverse.apply(x, lambd)


def adversarial_loss(
    z_brain: torch.Tensor,
    z_video: torch.Tensor,
    discriminator: nn.Module,
    lambd: float,
) -> torch.Tensor:
    """Cross-entropy modality classification loss with GRL on z.

    Returns the cross-entropy of the discriminator over a (2B, 2) batch.
    The reverse-gradient is applied only to the projection-head path; the
    discriminator weights receive the normal forward gradient.
    """
    z = torch.cat([z_brain, z_video], dim=0)  # (2B, D)
    z_rev = grad_reverse(z, lambd)
    logits = discriminator(z_rev)
    B = z_brain.shape[0]
    labels = torch.cat(
        [
            torch.zeros(B, dtype=torch.long, device=z.device),
            torch.ones(B, dtype=torch.long, device=z.device),
        ]
    )
    return F.cross_entropy(logits, labels)
