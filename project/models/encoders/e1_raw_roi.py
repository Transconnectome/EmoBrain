"""E1. Raw ROI projection encoder (control: no pretrain, no adaptation).

The floor of the NV3 encoder ladder. An fMRI ROI feature vector goes through a
small MLP to a brain embedding. No pretraining, no fMRI-specific adaptation, so
it isolates one question. Does routing raw ROI through the LLM readout beat the
ridge baseline (Pearson 0.30 / CCC 0.17)? E2-E4 are measured against this floor.

Contract. BrainEncoder. forward(fmri [B, roi_dim]) -> [B, out_dim].
"""
from __future__ import annotations

import torch.nn as nn

from project.models.base import BrainEncoder
from project.models.registry import register


@register("encoder", "e1_raw_roi")
class E1RawROI(BrainEncoder):
    def __init__(self, roi_dim: int = 450, hidden: int = 512,
                 out_dim: int = 512, dropout: float = 0.1):
        super().__init__()
        self.out_dim = out_dim
        self.net = nn.Sequential(
            nn.Linear(roi_dim, hidden),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, fmri):  # [B, roi_dim] -> [B, out_dim]
        return self.net(fmri)
