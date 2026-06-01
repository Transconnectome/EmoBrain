"""Architecture D: Late fusion.
concat(brain_emb, video_emb) → Linear → V/A

Trainable: Linear only. Deterministic (single-seed sufficient).
"""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class LateFusion(nn.Module):
    def __init__(self, brain_dim: int, video_dim: int, n_out: int,
                 task_type: str = "binary"):
        super().__init__()
        self.task_type = task_type
        self.head = nn.Linear(brain_dim + video_dim, n_out if task_type == "binary" else 1)

    def forward(self, brain, video):
        x = torch.cat([brain, video], dim=-1)
        return self.head(x)
