"""LLM backbone contract + registry + a CPU stub (spec §6-6).

Contract (both stub and Qwen implement it).
    hidden_dim               D_llm
    tokenize(texts)          list[str] -> (ids [B,L], mask [B,L])
    embed_text(ids)          [B,L] -> [B,L,D_llm]      (tokenizer path, no projector)
    forward(embeds, mask)    [B,S,D_llm] -> [B,D_llm]  (pooled last non-pad token)

The stub is a tiny transformer with a hashing tokenizer so the whole assembly
(encoder x projector x prompt x backbone x head, teacher and student) can be
wired and unit-tested on CPU without downloading a 4B model. The real Qwen3-VL
backbone lives in backbone_qwen.py and is imported only when selected.
"""

from __future__ import annotations

from typing import Callable

import torch
import torch.nn as nn

_BACKBONES: dict[str, Callable] = {}


def register_backbone(name: str):
    def deco(cls):
        _BACKBONES[name] = cls
        return cls
    return deco


def build_backbone(cfg: dict):
    cfg = dict(cfg)
    name = cfg.pop("type", "stub")
    if name == "qwen":
        import project.code.fusion.backbone_qwen  # noqa: F401  (registers, lazy)
    if name not in _BACKBONES:
        raise KeyError(f"unknown backbone {name!r}. available={sorted(_BACKBONES)}")
    return _BACKBONES[name](**cfg)


@register_backbone("stub")
class StubBackbone(nn.Module):
    """Tiny transformer + deterministic hashing tokenizer. CPU wiring only."""

    def __init__(self, hidden_dim: int = 128, vocab: int = 4096, n_layers: int = 2,
                 n_heads: int = 4, max_len: int = 512):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.vocab = vocab
        self.embed = nn.Embedding(vocab, hidden_dim)
        self.pos = nn.Embedding(max_len, hidden_dim)
        layer = nn.TransformerEncoderLayer(hidden_dim, n_heads, hidden_dim * 4,
                                           batch_first=True)
        self.enc = nn.TransformerEncoder(layer, n_layers)

    def tokenize(self, texts):
        ids = [[(hash(w) % (self.vocab - 1)) + 1 for w in t.split()] for t in texts]
        L = max(len(x) for x in ids)
        mask = torch.zeros(len(ids), L, dtype=torch.long)
        out = torch.zeros(len(ids), L, dtype=torch.long)
        for i, x in enumerate(ids):
            out[i, : len(x)] = torch.tensor(x)
            mask[i, : len(x)] = 1
        return out, mask

    def embed_text(self, token_ids):
        return self.embed(token_ids)

    def forward(self, inputs_embeds, attention_mask):
        B, S, _ = inputs_embeds.shape
        pos = self.pos(torch.arange(S, device=inputs_embeds.device))[None]
        h = self.enc(inputs_embeds + pos,
                     src_key_padding_mask=(attention_mask == 0))
        last = attention_mask.long().sum(1) - 1
        return h[torch.arange(B, device=h.device), last]
