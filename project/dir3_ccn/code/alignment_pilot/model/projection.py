"""Projection heads. Brain (768) and Video (1408) -> common 512-dim space.

2-layer MLP with GELU + Dropout + LayerNorm. ~1.5M params total.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class ProjBrain(nn.Module):
    def __init__(self, in_dim: int = 768, hidden: int = 1024, out_dim: int = 512, drop: float = 0.1) -> None:
        super().__init__()
        self.fc1 = nn.Linear(in_dim, hidden)
        self.act = nn.GELU()
        self.drop = nn.Dropout(drop)
        self.fc2 = nn.Linear(hidden, out_dim)
        self.norm = nn.LayerNorm(out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop(x)
        x = self.fc2(x)
        x = self.norm(x)
        return x


class ProjVideo(nn.Module):
    def __init__(self, in_dim: int = 1408, hidden: int = 1024, out_dim: int = 512, drop: float = 0.1) -> None:
        super().__init__()
        self.fc1 = nn.Linear(in_dim, hidden)
        self.act = nn.GELU()
        self.drop = nn.Dropout(drop)
        self.fc2 = nn.Linear(hidden, out_dim)
        self.norm = nn.LayerNorm(out_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop(x)
        x = self.fc2(x)
        x = self.norm(x)
        return x
