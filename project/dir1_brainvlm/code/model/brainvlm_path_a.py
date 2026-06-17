"""Path A. Qwen3-VL + linear projection (LLaVA-style) + LoRA + multi-task heads.

Design.md Section 4. Architecture:
    image -> [frozen] Qwen3-VL vision tower
          -> [trainable] linear projection (D_vis -> D_llm)
          -> concat with text prompt embedding
          -> [LoRA] Qwen3-VL LLM body
          -> 3 outputs:
               (a) caption (LM head)
               (b) V/A scalar regression head
               (c) Cat34 distribution head

Skeleton only. Full integration with Qwen3VLForConditionalGeneration deferred to
train/train_pilot.py once env is verified.
"""
from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn as nn


@dataclass
class BrainVLMConfig:
    qwen_model_id: str = "Qwen/Qwen3-VL-2B-Instruct"
    d_vis: int = 1152
    d_llm: int = 2048
    cat34_dim: int = 34
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "k_proj", "v_proj", "o_proj")
    freeze_vision_tower: bool = True
    freeze_llm_base: bool = True


class VisionToLLMProj(nn.Module):
    """Minimal LLaVA-style linear bridge."""

    def __init__(self, d_vis: int, d_llm: int):
        super().__init__()
        self.proj = nn.Sequential(
            nn.LayerNorm(d_vis),
            nn.Linear(d_vis, d_llm),
            nn.GELU(),
            nn.Linear(d_llm, d_llm),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.proj(x)


class VAHead(nn.Module):
    def __init__(self, d_llm: int):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(d_llm, 128),
            nn.GELU(),
            nn.Linear(128, 2),
        )

    def forward(self, pooled: torch.Tensor) -> torch.Tensor:
        return self.mlp(pooled)


class Cat34Head(nn.Module):
    def __init__(self, d_llm: int, cat34_dim: int = 34):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(d_llm, 256),
            nn.GELU(),
            nn.Linear(256, cat34_dim),
        )

    def forward(self, pooled: torch.Tensor) -> torch.Tensor:
        return self.mlp(pooled)


class BrainVLMPathA(nn.Module):
    """Full Path A wrapper. Vision tower + LLM are deferred-loaded.

    `forward_pilot` returns dict(loss components) for the train loop.
    Backbone integration happens in `train/train_pilot.py` when Qwen3VL is verified.
    """

    def __init__(self, cfg: BrainVLMConfig):
        super().__init__()
        self.cfg = cfg
        self.projector = VisionToLLMProj(cfg.d_vis, cfg.d_llm)
        self.va_head = VAHead(cfg.d_llm)
        self.cat34_head = Cat34Head(cfg.d_llm, cfg.cat34_dim)
        self.vision_tower = None
        self.llm = None

    def attach_backbones(self, vision_tower: nn.Module, llm: nn.Module) -> None:
        self.vision_tower = vision_tower
        self.llm = llm
        if self.cfg.freeze_vision_tower:
            for p in self.vision_tower.parameters():
                p.requires_grad = False
        if self.cfg.freeze_llm_base:
            for p in self.llm.parameters():
                p.requires_grad = False

    def encode_vision(self, image: torch.Tensor) -> torch.Tensor:
        assert self.vision_tower is not None, "call attach_backbones first"
        with torch.no_grad():
            feats = self.vision_tower(image)
        return self.projector(feats)
