"""E1. Image-pretrained ViT adapted to an fMRI ROI grid.

fMRI ROI vector -> square grid -> upsample 224 -> 3 channels -> pretrained ViT ->
CLS embedding. The image prior is a stretch for fMRI by design; whether a little
LoRA adaptation makes the transfer work is exactly this encoder's question.

Adapt axis. frozen = pure image prior, no adaptation. lora = q,v LoRA on the ViT
(the default per spec §14, full fine-tune forbidden on this data). Handled by the
base class apply_adapt.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F

from project.code.brain_encoder.base import BrainEncoder
from project.code.brain_encoder.registry import register_encoder


@register_encoder("vit")
class ViTEncoder(BrainEncoder):
    def __init__(self, hf_model: str = "google/vit-base-patch16-224", in_dim: int = 450,
                 grid: int = 22, adapt: str = "lora", lora: dict | None = None,
                 dtype: str = "float32"):
        super().__init__(adapt=adapt, lora=lora)
        from transformers import ViTModel

        self.grid = grid
        self.vit = ViTModel.from_pretrained(hf_model, torch_dtype=getattr(torch, dtype))
        self.out_dim = self.vit.config.hidden_size            # 768 for vit-base
        # ViT q,v are named "query","value"; base class wires LoRA / freeze.
        self.vit = self.apply_adapt(self.vit, lora_targets=["query", "value"])

    def _encode(self, fmri):                                  # (B,450) -> (B,1,768)
        if fmri.dim() == 3:
            fmri = fmri.mean(dim=1)
        b, d = fmri.shape
        n = self.grid * self.grid
        x = F.pad(fmri, (0, n - d)) if d < n else fmri[:, :n]
        img = x.view(b, 1, self.grid, self.grid)
        img = F.interpolate(img, size=(224, 224), mode="bilinear", align_corners=False)
        img = img.repeat(1, 3, 1, 1).to(next(self.vit.parameters()).dtype)
        cls = self.vit(pixel_values=img).last_hidden_state[:, 0]   # CLS token
        return cls.unsqueeze(1)
