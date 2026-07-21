"""Brain encoder contract (implementation_spec_20260702 §6-2).

Every encoder occupies the SAME slot. fMRI goes in, a brain embedding sequence
comes out, and the projector lifts it to LLM tokens. Swapping E1..E4 is a config
edit and nothing downstream changes.

Contract.
    forward(fmri) -> (B, T_e, D_enc)
    out_dim       == D_enc

Adapt axis (spec §6-2, and the global CAUTION list). frozen vs fine-tune is an
INDEPENDENT axis from which encoder is used, so it lives here in the base class
rather than in each encoder.
    frozen : no gradient reaches encoder parameters (linear probing).
    lora   : PEFT adapters on the encoder, base weights frozen.
    full   : everything trainable. Allowed but never the default; on 10925
             pooled trials it overfits (E4 mode collapse was observed).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import torch
import torch.nn as nn


class BrainEncoder(nn.Module, ABC):
    """Base for E1..E4. Subclasses set self.out_dim and implement _encode()."""

    #: set by every subclass. D_enc.
    out_dim: int

    def __init__(self, adapt: str = "frozen", lora: dict | None = None):
        super().__init__()
        if adapt not in ("frozen", "lora", "full"):
            raise ValueError(f"adapt must be frozen|lora|full, got {adapt!r}")
        self.adapt = adapt
        self.lora_cfg = lora or {}

    # --- subclass hook -----------------------------------------------------
    @abstractmethod
    def _encode(self, fmri: torch.Tensor) -> torch.Tensor:
        """Return (B, T_e, D_enc). Subclasses implement only this."""

    # --- shared -----------------------------------------------------------
    def forward(self, fmri: torch.Tensor) -> torch.Tensor:
        out = self._encode(fmri)
        if out.dim() == 2:                      # (B, D) -> (B, 1, D)
            out = out.unsqueeze(1)
        assert out.dim() == 3, f"encoder must return (B,T_e,D_enc), got {tuple(out.shape)}"
        assert out.shape[-1] == self.out_dim, (
            f"out_dim mismatch: declared {self.out_dim}, got {out.shape[-1]}")
        return out

    def apply_adapt(self, module: nn.Module, lora_targets: list[str] | None = None) -> nn.Module:
        """Apply the adapt axis to a pretrained submodule.

        Call this from a subclass right after loading pretrained weights. Returns
        the (possibly wrapped) module so the subclass can reassign it.
        """
        if self.adapt == "frozen":
            for p in module.parameters():
                p.requires_grad_(False)
            module.eval()
            return module
        if self.adapt == "lora":
            from peft import LoraConfig, get_peft_model
            cfg = {"r": 16, "lora_alpha": 32, "lora_dropout": 0.05}
            cfg.update(self.lora_cfg)
            if lora_targets:
                cfg.setdefault("target_modules", lora_targets)
            return get_peft_model(module, LoraConfig(**cfg))
        return module                            # full: leave trainable

    def n_trainable(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def extra_repr(self) -> str:
        return f"adapt={self.adapt}, out_dim={getattr(self, 'out_dim', '?')}"
