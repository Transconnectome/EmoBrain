"""Architecture C: Contrastive alignment (Stage 1) + Linear probe (Stage 2).

Stage 1: brain_proj + video_proj 학습 (InfoNCE / NT-Xent loss).
         Same-stim (brain, video) pair = positive, different-stim = negative.
         Temperature τ = 0.07 (CLIP default).

Stage 2: 학습된 brain_proj 위에 linear V/A probe.
         또한 concat(brain_proj, video_proj) 위에도 probe (joint variant).
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class ContrastiveAligner(nn.Module):
    """Stage 1: project both modalities to common d_model, L2-normalize, InfoNCE.

    forward returns the loss directly during training; use .encode_brain / .encode_video
    for inference to get the projected features.
    """
    def __init__(self, brain_dim: int, video_dim: int,
                 d_model: int = 256, temperature: float = 0.07):
        super().__init__()
        self.brain_proj = nn.Sequential(
            nn.Linear(brain_dim, d_model * 2),
            nn.GELU(),
            nn.Linear(d_model * 2, d_model),
        )
        self.video_proj = nn.Sequential(
            nn.Linear(video_dim, d_model * 2),
            nn.GELU(),
            nn.Linear(d_model * 2, d_model),
        )
        self.temperature = temperature

    def encode_brain(self, brain):
        z = self.brain_proj(brain)
        return F.normalize(z, dim=-1)

    def encode_video(self, video):
        z = self.video_proj(video)
        return F.normalize(z, dim=-1)

    def info_nce(self, z_b, z_v):
        """Symmetric InfoNCE (CLIP-style)."""
        logits = (z_b @ z_v.T) / self.temperature
        labels = torch.arange(z_b.shape[0], device=z_b.device)
        loss_b2v = F.cross_entropy(logits, labels)
        loss_v2b = F.cross_entropy(logits.T, labels)
        return 0.5 * (loss_b2v + loss_v2b)

    def forward(self, brain, video):
        z_b = self.encode_brain(brain)
        z_v = self.encode_video(video)
        return self.info_nce(z_b, z_v)
