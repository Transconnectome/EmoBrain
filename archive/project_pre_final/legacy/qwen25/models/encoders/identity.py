"""Identity encoder. Passes a precomputed brain vector straight to the projector.

Used by E3 (frozen BFM): the encoder IS the frozen foundation model, so there is
no trainable encoder here, only the downstream projector. out_dim = the embedding
dim, set in config to match the chosen BFM variant (288 / 768 / 1536).

Contract. BrainEncoder. forward(fmri [B, dim]) -> [B, dim]. No parameters.
"""
from __future__ import annotations

from project.models.base import BrainEncoder
from project.models.registry import register


@register("encoder", "identity")
class IdentityEncoder(BrainEncoder):
    def __init__(self, dim: int):
        super().__init__()
        self.out_dim = dim

    def forward(self, fmri):  # [B, dim] -> [B, dim]
        return fmri
