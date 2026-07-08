"""Component contracts for the swappable EmoBrain model (NV3).

build_model() wires four component kinds using ONLY the contracts below, so
any (encoder x projector x backbone x head) combination composes and a script
can swap a component by changing one config line. See project/models/build.py.

Contracts.
    BrainEncoder. fmri -> brain embedding. Exposes .out_dim so the projector
        adapts automatically (no per-encoder dim hardcoding).
        forward(fmri) -> [B, out_dim]  or  [B, T, out_dim] (sequence).
    Projector. (any in_dim) -> [B, n_tokens, llm_dim]. Adapts encoder dim to
        the LLM hidden dim and emits a fixed number of tokens.
    Backbone. inputs_embeds + attention_mask -> pooled [B, hidden_dim].
        Exposes .hidden_dim and .embed_text(token_ids) -> [B, L, hidden_dim].
        (Text goes through the tokenizer + embedding, NEVER the projector.)
    Head. pooled hidden -> [B, 34]. No activation, no softmax (z-space).

These are thin nn.Module subclasses used as type markers; components subclass
them and register via project.models.registry.register.
"""
from __future__ import annotations

import torch.nn as nn


class BrainEncoder(nn.Module):
    """fmri -> brain embedding. Subclass must set self.out_dim."""

    out_dim: int

    def forward(self, fmri):  # -> [B, out_dim] or [B, T, out_dim]
        raise NotImplementedError


class Projector(nn.Module):
    """brain embedding -> [B, n_tokens, llm_dim]. Adapts dims."""

    def forward(self, x):  # -> [B, n_tokens, llm_dim]
        raise NotImplementedError


class Backbone(nn.Module):
    """inputs_embeds + mask -> pooled [B, hidden_dim]. Set self.hidden_dim."""

    hidden_dim: int

    def tokenize(self, texts):  # list[str] -> (ids [B, L], mask [B, L])
        raise NotImplementedError

    def embed_text(self, token_ids):  # -> [B, L, hidden_dim]
        raise NotImplementedError

    def forward(self, inputs_embeds, attention_mask):  # -> [B, hidden_dim]
        raise NotImplementedError


class Head(nn.Module):
    """pooled hidden -> [B, n_emotions]. No activation (z-space)."""

    def forward(self, hidden):  # -> [B, 34]
        raise NotImplementedError
