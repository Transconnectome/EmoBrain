"""Projector (spec §6-3). encoder embedding -> LLM tokens.

Contract.
    forward((B, T_e, D_enc)) -> (B, N, D_llm)      N = projector.n_tokens

Two types.
    mlp      map D_enc to D_llm and expand to N tokens (default).
    qformer  N learned queries cross-attend over the T_e sequence, so a long
             encoder sequence is summarised without mean-pooling it away.

Rules from the spec.
    - per-modality AND per-encoder. The brain projector and the video projector
      never share parameters, and each encoder owns its own instance.
    - text (caption, question) NEVER gets a projector, only the tokenizer
      (spec §14). Nothing here is applied to text.
    - CAUTION. Too small an N compresses the 34D structure away in this
      bottleneck, so n_tokens is a sweep target, not a constant to hardcode.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class MLPProjector(nn.Module):
    """D_enc -> D_llm, expanded to N tokens. Sequence input is mean-pooled."""

    def __init__(self, in_dim: int, llm_dim: int, n_tokens: int = 16,
                 hidden_dim: int | None = None, dropout: float = 0.0):
        super().__init__()
        hidden_dim = hidden_dim or llm_dim
        self.n_tokens, self.llm_dim = n_tokens, llm_dim
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(hidden_dim, n_tokens * llm_dim),
        )

    def forward(self, x):                          # (B,T_e,D_enc) -> (B,N,D_llm)
        if x.dim() == 3:
            x = x.mean(dim=1)
        return self.net(x).view(x.shape[0], self.n_tokens, self.llm_dim)


class QFormerProjector(nn.Module):
    """N learned queries cross-attend over the encoder sequence."""

    def __init__(self, in_dim: int, llm_dim: int, n_tokens: int = 16,
                 n_heads: int = 8, n_layers: int = 2, dropout: float = 0.0):
        super().__init__()
        self.n_tokens, self.llm_dim = n_tokens, llm_dim
        self.query = nn.Parameter(torch.randn(1, n_tokens, llm_dim) * 0.02)
        self.kv = nn.Linear(in_dim, llm_dim)
        self.blocks = nn.ModuleList([
            nn.ModuleDict({
                "attn": nn.MultiheadAttention(llm_dim, n_heads, dropout=dropout,
                                              batch_first=True),
                "norm_q": nn.LayerNorm(llm_dim),
                "norm_o": nn.LayerNorm(llm_dim),
                "ff": nn.Sequential(nn.Linear(llm_dim, llm_dim * 4), nn.GELU(),
                                    nn.Linear(llm_dim * 4, llm_dim)),
            }) for _ in range(n_layers)
        ])

    def forward(self, x):                          # (B,T_e,D_enc) -> (B,N,D_llm)
        if x.dim() == 2:
            x = x.unsqueeze(1)
        kv = self.kv(x)
        q = self.query.expand(x.shape[0], -1, -1)
        for b in self.blocks:
            h, _ = b["attn"](b["norm_q"](q), kv, kv)
            q = q + h
            q = q + b["ff"](b["norm_o"](q))
        return q


def build_projector(cfg: dict, in_dim: int, llm_dim: int) -> nn.Module:
    """cfg = {"type": "mlp"|"qformer", "n_tokens": N, ...}."""
    cfg = dict(cfg)
    t = cfg.pop("type", "mlp")
    if t == "mlp":
        return MLPProjector(in_dim=in_dim, llm_dim=llm_dim, **cfg)
    if t == "qformer":
        return QFormerProjector(in_dim=in_dim, llm_dim=llm_dim, **cfg)
    raise KeyError(f"unknown projector type {t!r} (mlp|qformer)")
