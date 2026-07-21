"""SigLIP loss. Pairwise sigmoid for batched contrastive alignment.

Reference. Zhai et al. 2023. Sigmoid Loss for Language-Image Pretraining.
fMRI-LM Stage 1 also uses this (Wei 2026, arXiv 2511.21760).

Compared to CLIP-style softmax InfoNCE:
- pairwise sigmoid avoids the softmax normalization which makes the loss less
  dependent on batch size and reduces hard-negative domination.
- temperature `t` and bias `b` are learnable (initialized log_t=log(10) and
  b=-10 per the SigLIP defaults).
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class SigLIPLoss(nn.Module):
    def __init__(self, init_log_t: float = math.log(10.0), init_b: float = -10.0) -> None:
        super().__init__()
        self.log_t = nn.Parameter(torch.tensor(init_log_t, dtype=torch.float32))
        self.b = nn.Parameter(torch.tensor(init_b, dtype=torch.float32))

    def forward(self, z_brain: torch.Tensor, z_video: torch.Tensor) -> torch.Tensor:
        # Normalize the embeddings, then build a (B, B) pairwise score matrix.
        zb = F.normalize(z_brain, dim=-1)
        zv = F.normalize(z_video, dim=-1)
        t = self.log_t.exp()
        s = t * (zb @ zv.t()) + self.b  # (B, B)
        B = s.size(0)
        # Positive pairs lie on the diagonal; off-diagonal are negatives.
        labels = 2 * torch.eye(B, device=s.device) - 1  # (+1 on diag, -1 elsewhere)
        # log-sigmoid form: -log sigmoid(z_ij * s_ij), averaged.
        loss = -F.logsigmoid(labels * s).mean()
        return loss
