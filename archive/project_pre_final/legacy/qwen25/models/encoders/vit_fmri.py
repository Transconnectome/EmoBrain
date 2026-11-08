"""E4. Image-pretrained ViT on an fMRI grid (fMRI-as-image).

fMRI ROI vector -> pad to grid*grid -> [B,1,grid,grid] -> upsample 224 -> 3ch ->
pretrained ViT -> CLS embedding -> projector -> LLM. case1 grid (simple square
reshape, no spatial meaning; master default). frozen (default) or LoRA on the
ViT. fMRI is not a natural image, so the image pretraining is a stretch by design
(this is exactly the E4 question). Lazy-imports transformers; needs the ViT
predownloaded (compute nodes are offline).

Contract. BrainEncoder. forward(fmri [B, D_roi]) -> [B, hidden]. out_dim = ViT hidden.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F

from project.models.base import BrainEncoder
from project.models.registry import register


@register("encoder", "vit_fmri")
class ViTfMRI(BrainEncoder):
    def __init__(self, hf_model: str = "google/vit-base-patch16-224",
                 grid: int = 22, frozen: bool = True, lora: dict | None = None,
                 dtype: str = "float32"):
        super().__init__()
        from transformers import ViTModel

        self.grid = grid
        self.vit = ViTModel.from_pretrained(hf_model, torch_dtype=getattr(torch, dtype))
        self.out_dim = self.vit.config.hidden_size            # 768 for vit-base
        if lora:
            from peft import LoraConfig, get_peft_model
            self.vit = get_peft_model(
                self.vit, LoraConfig(target_modules=["query", "value"], **lora)
            )
        elif frozen:
            for p in self.vit.parameters():
                p.requires_grad_(False)

    def forward(self, fmri):  # [B, D_roi] -> [B, hidden]
        b, d = fmri.shape
        n = self.grid * self.grid
        x = F.pad(fmri, (0, n - d)) if d < n else fmri[:, :n]
        img = x.view(b, 1, self.grid, self.grid)
        img = F.interpolate(img, size=(224, 224), mode="bilinear", align_corners=False)
        img = img.repeat(1, 3, 1, 1).to(next(self.vit.parameters()).dtype)
        return self.vit(pixel_values=img).last_hidden_state[:, 0]   # CLS token
