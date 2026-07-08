"""MLP projector. brain embedding -> N_b LLM tokens.

Maps any encoder out_dim (in_dim) to the LLM hidden dim (llm_dim) and expands
to a fixed n_tokens. This is the adapter that makes any encoder plug into any
backbone. Accepts a single vector [B, in_dim] or a sequence [B, T, in_dim];
a sequence is mean-pooled before projection (Q-Former, which attends over the
sequence instead of pooling, is a separate projector for later).

Contract. Projector. forward(x) -> [B, n_tokens, llm_dim].
"""
from __future__ import annotations

import torch.nn as nn

from project.models.base import Projector
from project.models.registry import register


@register("projector", "mlp")
class MLPProjector(Projector):
    def __init__(self, in_dim: int, llm_dim: int, n_tokens: int = 8,
                 hidden: int | None = None):
        super().__init__()
        self.n_tokens = n_tokens
        self.llm_dim = llm_dim
        hidden = hidden or llm_dim
        self.proj = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.GELU(),
            nn.Linear(hidden, n_tokens * llm_dim),
        )

    def forward(self, x):
        if x.dim() == 3:            # [B, T, D] -> [B, D]
            x = x.mean(dim=1)
        b = x.shape[0]
        y = self.proj(x)            # [B, n_tokens * llm_dim]
        return y.view(b, self.n_tokens, self.llm_dim)
