"""Trainable MLP encoder on a brain vector. The "adaptation" building block.

Used by E2 (raw ROI + adaptation) and E4 (frozen BFM + adaptation): a small
2-layer MLP that transforms the input vector before the projector. Pair with
IdentityEncoder (no adaptation) for E1 / E3. in_dim = input vector dim
(ROI 450, or BFM 288 / 768 / 1536).

Contract. BrainEncoder. forward(fmri [B, in_dim]) -> [B, out_dim].
"""
from __future__ import annotations

import torch.nn as nn

from project.models.base import BrainEncoder
from project.models.registry import register


@register("encoder", "vec_mlp")
class VecMLP(BrainEncoder):
    def __init__(self, in_dim: int, hidden: int = 512,
                 out_dim: int = 512, dropout: float = 0.1):
        super().__init__()
        self.out_dim = out_dim
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, fmri):  # [B, in_dim] -> [B, out_dim]
        return self.net(fmri)
