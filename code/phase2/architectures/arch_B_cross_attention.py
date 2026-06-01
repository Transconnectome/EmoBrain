"""Architecture B: Cross-attention.
brain → Q, video → K/V (and vice versa for symmetry).
Two cross-attention directions, then pool, then Linear → V/A.

Trainable: Q/K/V projections + attention + linear.
"""
import torch
import torch.nn as nn


class CrossAttention(nn.Module):
    def __init__(self, brain_dim: int, video_dim: int, n_out: int,
                 task_type: str = "binary",
                 d_model: int = 256, n_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.task_type = task_type
        self.brain_proj = nn.Linear(brain_dim, d_model)
        self.video_proj = nn.Linear(video_dim, d_model)

        # Two cross-attention directions
        self.b2v = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)
        self.v2b = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model * 2, n_out if task_type == "binary" else 1)

    def forward(self, brain, video):
        b = self.brain_proj(brain).unsqueeze(1)   # (B, 1, d)
        v = self.video_proj(video).unsqueeze(1)   # (B, 1, d)

        # brain queries video
        b_out, _ = self.b2v(query=b, key=v, value=v)
        b_pool = self.norm1((b + b_out).squeeze(1))   # (B, d)

        # video queries brain
        v_out, _ = self.v2b(query=v, key=b, value=b)
        v_pool = self.norm2((v + v_out).squeeze(1))   # (B, d)

        x = torch.cat([b_pool, v_pool], dim=-1)       # (B, 2d)
        return self.head(x)
