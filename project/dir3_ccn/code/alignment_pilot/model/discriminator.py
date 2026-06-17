"""Modality discriminator. Takes z (B, 512) and predicts brain (0) vs video (1).

Small 2-layer MLP. Used with GRL on the projection-head path.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class ModalityDiscriminator(nn.Module):
    def __init__(self, in_dim: int = 512, hidden: int = 256) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hidden, 2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
