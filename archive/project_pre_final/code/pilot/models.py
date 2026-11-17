"""Small brain-query teacher and strictly brain-only student; no downloads."""
from dataclasses import dataclass

import torch
from torch import nn
import torch.nn.functional as F

from .baseline import TARGET_DIMS


@dataclass(frozen=True)
class ModelConfig:
    target: str
    rois: int
    brain_features: int
    participants: int = 1
    width: int = 16
    heads: int = 2
    video_dim: int = 6
    caption_dim: int = 5

    def __post_init__(self):
        if self.target not in TARGET_DIMS:
            raise ValueError("Unsupported target; do not invent VA/VAD coding")
        if min(self.rois, self.brain_features, self.participants, self.width, self.heads,
               self.video_dim, self.caption_dim) < 1 or self.width % self.heads:
            raise ValueError("Invalid model dimensions")


class BrainPath(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.maps = nn.ModuleList([nn.Linear(cfg.brain_features, cfg.width)
                                   for _ in range(cfg.participants)])
        self.roi_id = nn.Parameter(torch.randn(cfg.rois, cfg.width) * .02)
        self.norm = nn.LayerNorm(cfg.width)

    def forward(self, brain, valid, participant):
        if brain.ndim != 3 or brain.shape[1:] != (self.cfg.rois, self.cfg.brain_features):
            raise ValueError("Brain must retain ROI spatial features")
        if valid.shape != brain.shape or valid.dtype != torch.bool:
            raise ValueError("Explicit brain feature validity required")
        if not torch.isfinite(brain[valid]).all():
            raise ValueError("Nonfinite valid brain entries")
        if participant.shape != (len(brain),) or participant.dtype != torch.long:
            raise ValueError("Participant map index must be an integer per observation")
        if (participant < 0).any() or (participant >= self.cfg.participants).any():
            raise ValueError("Unfitted participant adapter requested")
        roi_valid = valid.any(dim=-1)
        if (~roi_valid.any(dim=1)).any():
            raise ValueError("All brain tokens masked")
        clean = torch.where(valid, brain, torch.zeros_like(brain))
        tokens = torch.zeros((*brain.shape[:2], self.cfg.width), device=brain.device, dtype=brain.dtype)
        for index, mapping in enumerate(self.maps):
            use = participant == index
            if use.any():
                tokens[use] = mapping(clean[use])
        tokens = self.norm(tokens + self.roi_id)
        return tokens.masked_fill(~roi_valid[..., None], 0), roi_valid


def pool(tokens, valid):
    return (tokens * valid[..., None]).sum(1) / valid.sum(1, keepdim=True).clamp_min(1)


class BrainStudent(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.brain_path = BrainPath(cfg)
        self.mixer = nn.TransformerEncoderLayer(cfg.width, cfg.heads, cfg.width * 2,
                                               dropout=0, batch_first=True)
        self.head = nn.Linear(cfg.width, TARGET_DIMS[cfg.target])

    def forward(self, brain, brain_valid, participant):
        tokens, valid = self.brain_path(brain, brain_valid, participant)
        mixed = self.mixer(tokens, src_key_padding_mask=~valid).masked_fill(~valid[..., None], 0)
        latent = pool(mixed, valid)
        return {"logits": self.head(latent), "brain_tokens": tokens, "student_stage": latent}


class JointTeacher(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.brain_path = BrainPath(cfg)
        self.video = nn.Linear(cfg.video_dim, cfg.width)
        self.caption = nn.Linear(cfg.caption_dim, cfg.width)
        self.content_type = nn.Parameter(torch.randn(2, cfg.width) * .02)
        self.attention = nn.MultiheadAttention(cfg.width, cfg.heads, dropout=0, batch_first=True)
        self.norm = nn.LayerNorm(cfg.width)
        self.head = nn.Linear(cfg.width, TARGET_DIMS[cfg.target])

    def forward(self, brain, brain_valid, participant, video, caption, content_valid):
        tokens, roi_valid = self.brain_path(brain, brain_valid, participant)
        if content_valid.shape != (len(brain), 2) or content_valid.dtype != torch.bool:
            raise ValueError("Content validity must identify video/caption per observation")
        if video.shape != (len(brain), self.cfg.video_dim) or caption.shape != (len(brain), self.cfg.caption_dim):
            raise ValueError("Frozen feature dimensions mismatch")
        raw = (video, caption)
        projected = []
        for j, (feature, projection) in enumerate(zip(raw, (self.video, self.caption))):
            if not torch.isfinite(feature[content_valid[:, j]]).all():
                raise ValueError("Nonfinite valid content features")
            feature = torch.where(content_valid[:, j, None], feature.detach(), torch.zeros_like(feature))
            projected.append(projection(feature) + self.content_type[j])
        kv = torch.stack(projected, dim=1)
        update = torch.zeros_like(tokens)
        # Never call softmax on a row whose entire key/value memory is masked.
        has_content = content_valid.any(dim=1)
        if has_content.any():
            update[has_content] = self.attention(tokens[has_content], kv[has_content], kv[has_content],
                                                 key_padding_mask=~content_valid[has_content],
                                                 need_weights=False)[0]
        fused = self.norm(tokens + update).masked_fill(~roi_valid[..., None], 0)
        latent = pool(fused, roi_valid)
        return {"logits": self.head(latent), "brain_tokens": tokens,
                "fused_tokens": fused, "joint_stage": latent}


def supervised(logits, targets, valid, target):
    if target not in TARGET_DIMS or logits.shape[-1] != TARGET_DIMS[target]:
        raise ValueError("Target/head mismatch")
    if logits.shape != targets.shape or valid.shape != targets.shape or valid.dtype != torch.bool:
        raise ValueError("Target and mask shape mismatch")
    if not valid.any() or not torch.isfinite(targets[valid]).all() or not torch.isfinite(logits[valid]).all():
        raise ValueError("No valid finite supervised entries")
    if target == "cat34":
        if ((targets[valid] < 0) | (targets[valid] > 1)).any():
            raise ValueError("CAT-34 proportions outside [0,1]")
        return F.binary_cross_entropy_with_logits(logits[valid], targets[valid])
    return F.mse_loss(logits[valid], targets[valid])


def student_objective(logits, targets, valid, target, guidance=None, guidance_valid=None, weight=0.):
    if not torch.isfinite(torch.tensor(weight)) or weight < 0:
        raise ValueError("Invalid guidance weight")
    label_loss = supervised(logits, targets, valid, target)
    kd = logits.sum() * 0
    if guidance is not None:
        if guidance_valid is None or guidance_valid.dtype != torch.bool or guidance.shape != logits.shape or guidance_valid.shape != logits.shape:
            raise ValueError("Explicit guidance values and validity required")
        if not guidance_valid.any() or not torch.isfinite(guidance[guidance_valid]).all():
            raise ValueError("Empty or nonfinite valid guidance")
        detached = guidance.detach()
        if target == "cat34" and ((detached[guidance_valid] < 0) | (detached[guidance_valid] > 1)).any():
            raise ValueError("OOF CAT-34 guidance must be probabilities")
        output = logits.sigmoid() if target == "cat34" else logits
        kd = F.mse_loss(output[guidance_valid], detached[guidance_valid])
    elif weight:
        raise ValueError("Nonzero guidance weight without OOF predictions")
    return {"total": label_loss + weight * kd, "label": label_loss, "distillation": kd}
