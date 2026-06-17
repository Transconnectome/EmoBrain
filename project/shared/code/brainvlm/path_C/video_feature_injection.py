"""
Path C (Decoupled) skeleton: video feature injection via cross-attention.

Goal:
  - fMRI 는 Path B 와 동일 (BrainVLM PatchEmbedQwen.fMRI → Qwen3-VL ViT → merger → LLM token)
  - video 는 EmoViS 의 pre-extracted feature (V-JEPA2 / CLIP / DINOv2 / VideoMAE / Qwen-VL caption) 사용.
    이 feature 는 이미 (N_stim, D) shape 의 .npy 로 저장돼있음 (data/stimulus_features/)
  - Video feature 를 LLM 의 hidden state 에 cross-attention 으로 inject

핵심 차이 (vs Path B):
  - Path B: 두 vision tower 가 각자 token 생성 → LLM input 으로 concat
  - Path C: 하나의 vision tower (fMRI 전용) + cross-attention 어댑터로 video 정보 주입

Why Path C:
  - Video feature extraction 비용 0 (이미 추출됨)
  - Qwen3-VL 의 native vision tower 거치지 않으므로 LLM input 길이 절약
  - Cross-attention 어댑터만 학습 (very lightweight, ~수십 K params)
  - Disadvantage: video 의 raw spatial pattern 손실, V-JEPA2 의 학습된 representation 에 의존

Skeleton 구조:
  1. VideoFeatureInjector: cross-attention module (q=LLM hidden, k/v=video feature)
  2. Inject into Qwen3-VL LLM decoder layers (e.g., 마지막 N layer)
  3. Training: cross-attention weights 만 trainable (rest frozen)
"""
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, "/pscratch/sd/s/sjmoon/EmoBrain/project/shared/code/brainvlm")
from _lib import load_video_feature


class VideoFeatureInjector(nn.Module):
    """Cross-attention adapter for injecting pre-extracted video features into LLM hidden states.

    Args:
        llm_dim: hidden dim of the LLM (2048 for Qwen3-VL-2B-Instruct)
        video_feature_dim: dim of the pre-extracted video feature (\eg 1408 for V-JEPA2, 768 for CLIP)
        num_heads: attention heads
    """

    def __init__(self, llm_dim: int = 2048, video_feature_dim: int = 1408, num_heads: int = 8):
        super().__init__()
        self.llm_dim = llm_dim
        self.video_feature_dim = video_feature_dim
        self.num_heads = num_heads

        # Project video feature → LLM dim
        self.video_proj = nn.Linear(video_feature_dim, llm_dim)
        self.layer_norm_v = nn.LayerNorm(llm_dim)
        self.layer_norm_h = nn.LayerNorm(llm_dim)

        # Cross-attention: q=LLM hidden, k/v=video
        self.cross_attn = nn.MultiheadAttention(llm_dim, num_heads, batch_first=True)

        # Output projection + residual gate
        self.out_proj = nn.Linear(llm_dim, llm_dim)
        self.gate = nn.Parameter(torch.zeros(1))  # zero-init: 학습 초기에 cross-attn 영향 0

    def forward(self, hidden_states: torch.Tensor, video_feat: torch.Tensor) -> torch.Tensor:
        """
        hidden_states: (B, L_text, llm_dim) — LLM decoder hidden states
        video_feat: (B, L_video, video_feature_dim) — pre-extracted video features.
                   For pooled single-vector feature, L_video=1.
        """
        v = self.video_proj(video_feat)
        v = self.layer_norm_v(v)
        q = self.layer_norm_h(hidden_states)

        # Cross-attention
        attn_out, _ = self.cross_attn(query=q, key=v, value=v)
        attn_out = self.out_proj(attn_out)

        # Gated residual (gate starts at 0, learns to increase)
        return hidden_states + torch.tanh(self.gate) * attn_out


def attach_injector_to_qwen(model, video_feature_dim: int, layer_indices: list = None):
    """Attach VideoFeatureInjector after the last few LLM decoder layers."""
    if layer_indices is None:
        # Default: last 4 layers
        n_layers = len(model.model.language_model.layers)
        layer_indices = list(range(n_layers - 4, n_layers))
    injectors = nn.ModuleList()
    for idx in layer_indices:
        inj = VideoFeatureInjector(
            llm_dim=model.config.text_config.hidden_size,
            video_feature_dim=video_feature_dim,
        )
        injectors.append(inj)
    model._video_injectors = injectors
    model._video_injector_layer_indices = layer_indices

    # TODO: register forward hooks on those layers that call the injector with the
    # current sample's video feature. Requires passing video_feat through model.forward kwargs.
    return model


if __name__ == "__main__":
    # Sanity test
    print("=== Path C VideoFeatureInjector smoke test ===\n")
    feat, stim_idx = load_video_feature("vjepa2_pretrained")
    print(f"V-JEPA2 features loaded: {feat.shape}")

    inj = VideoFeatureInjector(llm_dim=2048, video_feature_dim=feat.shape[1])
    n_params = sum(p.numel() for p in inj.parameters())
    print(f"Injector params: {n_params/1e6:.2f}M")

    # Mock LLM hidden + video feature
    B, L_text = 1, 50
    h = torch.randn(B, L_text, 2048)
    v = torch.from_numpy(feat[:1]).float().unsqueeze(1)  # (1, 1, D)
    print(f"input hidden: {tuple(h.shape)}, video feat: {tuple(v.shape)}")
    out = inj(h, v)
    print(f"output hidden: {tuple(out.shape)}")
    print(f"  residual: out ≈ h (gate starts at 0) → diff norm = {(out - h).norm():.6f}")
    print("\n✅ Injector forward OK, gate starts at 0 as designed.")
