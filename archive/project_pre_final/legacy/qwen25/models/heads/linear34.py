"""34D linear head (z-space, NO activation, NO softmax).

The 34 Cowen-Keltner emotions are non-exclusive independent regression targets
(bittersweet = joy and sadness both high). Any softmax / sum-to-1 / sigmoid
destroys co-occurrence, so the head is a bare linear map to raw z-space values.
Preprocessing (log1p_z) and the per-emotion MSE loss live elsewhere.

Contract. Head. forward(hidden [B, hidden_dim]) -> [B, n_emotions].
"""
from __future__ import annotations

import torch.nn as nn

from project.models.base import Head
from project.models.registry import register


@register("head", "linear34")
class Linear34(Head):
    def __init__(self, hidden_dim: int, n_emotions: int = 34):
        super().__init__()
        self.fc = nn.Linear(hidden_dim, n_emotions)

    def forward(self, hidden):  # [B, hidden_dim] -> [B, n_emotions]
        return self.fc(hidden)
