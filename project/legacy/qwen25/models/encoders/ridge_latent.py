"""E2. Frozen ridge encoder. ROI 450 -> 34D "ridge latent" (fixed feature).

A ridge regressor is fit closed-form on train (scripts/fit_ridge_encoder.py),
frozen, and used as a brain feature extractor: its 34D prediction is the latent
that feeds the projector -> LLM. No pretraining, but a task-specific linear
prior. out_dim = 34 (the ridge latent dim).

Contract. BrainEncoder. forward(fmri [B, 450]) -> [B, 34]. No trainable params.
"""
from __future__ import annotations

from pathlib import Path

import torch
import torch.nn as nn

from project.models.base import BrainEncoder
from project.models.registry import register

REPO_ROOT = Path(__file__).resolve().parents[3]


@register("encoder", "ridge_latent")
class RidgeLatent(BrainEncoder):
    def __init__(self, weights_path: str = "project/shared/data/ridge_encoder.pt"):
        super().__init__()
        d = torch.load(REPO_ROOT / weights_path, weights_only=False)
        n_out, n_in = d["coef"].shape                     # (34, 450)
        self.fc = nn.Linear(n_in, n_out)
        with torch.no_grad():
            self.fc.weight.copy_(torch.as_tensor(d["coef"], dtype=torch.float32))
            self.fc.bias.copy_(torch.as_tensor(d["intercept"], dtype=torch.float32))
        self.fc.weight.requires_grad_(False)              # frozen ridge
        self.fc.bias.requires_grad_(False)
        self.out_dim = n_out                              # 34

    def forward(self, fmri):  # [B, 450] -> [B, 34]
        return self.fc(fmri)
