"""E2. Ridge encoder (spec §6-2, via the LLM).

A ridge regressor fitted closed-form on train is used as a FIXED brain feature
extractor; its 34D prediction is the embedding handed to the projector. Task
prior, no pretraining.

CAUTION (spec §14). This is NOT the B1 ridge baseline. B1 goes straight from
fMRI to the 34D label with no LLM and never appears in the framework graph. E2
passes its latent through the projector and the LLM. Do not conflate them.
"""

from __future__ import annotations

from pathlib import Path

import torch
import torch.nn as nn

from project.code.brain_encoder.base import BrainEncoder
from project.code.brain_encoder.registry import register_encoder

REPO_ROOT = Path(__file__).resolve().parents[3]


@register_encoder("ridge")
class RidgeEncoder(BrainEncoder):
    def __init__(self, weights_path: str = "project/shared/data/ridge_encoder.pt",
                 adapt: str = "frozen", lora: dict | None = None):
        super().__init__(adapt=adapt, lora=lora)
        p = Path(weights_path)
        if not p.is_absolute():
            p = REPO_ROOT / p
        d = torch.load(p, weights_only=False)
        n_out, n_in = d["coef"].shape                      # (34, 450)
        self.fc = nn.Linear(n_in, n_out)
        with torch.no_grad():
            self.fc.weight.copy_(torch.as_tensor(d["coef"], dtype=torch.float32))
            self.fc.bias.copy_(torch.as_tensor(d["intercept"], dtype=torch.float32))
        self.out_dim = n_out                               # 34
        self.apply_adapt(self.fc)                          # frozen by default

    def _encode(self, fmri):                               # (B,450) -> (B,1,34)
        if fmri.dim() == 3:
            fmri = fmri.mean(dim=1)
        return self.fc(fmri).unsqueeze(1)
