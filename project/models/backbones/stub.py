"""Stub backbone. Tiny pure-torch transformer for CPU wiring smoke.

No pretrained weights, no downloads, no transformers dependency. It exists so
the wiring (encoder -> projector -> prompt assembly -> backbone -> head) can be
smoke-tested on CPU in seconds. Real training swaps in backbones/qwen.py by
changing one config line. Both expose the same contract, so nothing else moves.

Contract. Backbone. hidden_dim, embed_text(ids) -> [B, L, H],
    forward(inputs_embeds [B, L, H], attention_mask [B, L]) -> pooled [B, H].
"""
from __future__ import annotations

import torch
import torch.nn as nn

from project.models.base import Backbone
from project.models.registry import register


def _stable_hash(word: str, mod: int) -> int:
    """Deterministic string -> [1, mod] hash (no Python hash randomization)."""
    h = 0
    for ch in word:
        h = (h * 131 + ord(ch)) % mod
    return h + 1


@register("backbone", "stub")
class StubBackbone(Backbone):
    def __init__(self, hidden_dim: int = 64, n_layers: int = 2,
                 n_heads: int = 4, vocab: int = 1000):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.tok_embed = nn.Embedding(vocab, hidden_dim)
        layer = nn.TransformerEncoderLayer(
            hidden_dim, n_heads, dim_feedforward=hidden_dim * 2,
            batch_first=True,
        )
        self.enc = nn.TransformerEncoder(layer, n_layers)

    def tokenize(self, texts):  # list[str] -> (ids [B, L], mask [B, L])
        vocab = self.tok_embed.num_embeddings
        toks = [t.replace("\n", " ").split() for t in texts]
        seq_len = max((len(t) for t in toks), default=1)
        ids = torch.zeros(len(texts), seq_len, dtype=torch.long)
        mask = torch.zeros(len(texts), seq_len, dtype=torch.long)
        for i, words in enumerate(toks):
            for j, w in enumerate(words):
                ids[i, j] = _stable_hash(w, vocab - 1)
                mask[i, j] = 1
        return ids, mask

    def embed_text(self, token_ids):  # [B, L] -> [B, L, H]
        return self.tok_embed(token_ids)

    def forward(self, inputs_embeds, attention_mask):
        pad = attention_mask == 0                       # True = padding
        h = self.enc(inputs_embeds, src_key_padding_mask=pad)   # [B, L, H]
        m = attention_mask.unsqueeze(-1).float()
        pooled = (h * m).sum(dim=1) / m.sum(dim=1).clamp(min=1.0)  # mean-pool
        return pooled                                   # [B, H]
