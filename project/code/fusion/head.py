"""34-dim output head (spec §6-6). z-space, NO activation, NO softmax.

The 34 Cowen-Keltner emotions co-occur (bittersweet = joy and sadness both high),
so any softmax / sum-to-1 / sigmoid destroys co-occurrence. Bare linear map to
raw z-space; the log1p_z preprocessing and per-emotion MSE live elsewhere.
"""

from __future__ import annotations

import torch.nn as nn


class Linear34(nn.Module):
    def __init__(self, hidden_dim: int, n_emotions: int = 34):
        super().__init__()
        self.fc = nn.Linear(hidden_dim, n_emotions)

    def forward(self, hidden):
        return self.fc(hidden)
