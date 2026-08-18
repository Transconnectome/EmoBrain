"""EmoBrainModel — Sensory-Grounded Affective Residual (SGAR).

Drop-in model variant for the original EmoBrainModel.

Core idea
---------
Video and caption describe the same stimulus, so aligning the entire video
representation to brain can mostly transfer redundant semantics. SGAR instead:

  1) predicts video features from caption features,
  2) takes the residual video - E[video | caption],
  3) compresses that residual through an affect bottleneck,
  4) forces the bottleneck to predict the 34-D affect target,
  5) distills the resulting sensory-affective code into the brain representation.

Inference remains brain + question only.

Training integration
--------------------
Normal forward remains valid:

    pred = model(fmri, video=video, caption=caption, target_z=target)

The target_z argument is OPTIONAL for forward compatibility. If omitted, the
model uses the current task prediction as a detached pseudo-target for the
affective bottleneck. Supplying ground-truth target_z is strongly recommended.

After the normal task loss:

    loss = model.loss_with_aux(loss)

Diagnostics:
    model.last_aux_losses
    model.last_aux_metrics
"""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pad_sequence

from project.code.fusion.prompt import question_text, caption_field, token_order


def compact_valid_tokens(embeds: torch.Tensor, mask: torch.Tensor):
    """Remove internal padding and pad only at each sequence's right edge."""
    if embeds.shape[:2] != mask.shape:
        raise ValueError(
            f"embed/mask shape mismatch: {tuple(embeds.shape)} vs {tuple(mask.shape)}"
        )
    rows = [row[row_mask.bool()] for row, row_mask in zip(embeds, mask)]
    if any(row.shape[0] == 0 for row in rows):
        raise ValueError("every sequence must contain at least one valid token")
    packed = pad_sequence(rows, batch_first=True)
    lengths = torch.tensor([row.shape[0] for row in rows], device=mask.device)
    packed_mask = (
        torch.arange(packed.shape[1], device=mask.device)[None, :] < lengths[:, None]
    ).to(mask.dtype)
    return packed, packed_mask


def masked_mean(x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    w = mask.to(dtype=x.dtype).unsqueeze(-1)
    return (x * w).sum(dim=1) / w.sum(dim=1).clamp_min(1.0)


def cosine_distill_loss(student: torch.Tensor, teacher: torch.Tensor) -> torch.Tensor:
    s = F.normalize(student.float(), dim=-1, eps=1e-8)
    t = F.normalize(teacher.float(), dim=-1, eps=1e-8)
    return (1.0 - (s * t).sum(dim=-1)).mean()


class EmoBrainModel(nn.Module):
    """Original EmoBrainModel + sensory-grounded affective residual distillation."""

    def __init__(
        self,
        encoder,
        brain_projector,
        backbone,
        head,
        video_projector=None,
        modalities: dict | None = None,
        use_markers: bool = True,
        *,
        bottleneck_dim: int = 128,
        aux_weight: float = 0.10,
        video_pred_weight: float = 0.25,
        affect_weight: float = 1.00,
        distill_weight: float = 1.00,
    ):
        super().__init__()
        self.encoder = encoder
        self.brain_projector = brain_projector
        self.video_projector = video_projector
        self.backbone = backbone
        self.head = head
        self.modalities = modalities or {"brain": True}
        self._question = question_text()

        D = int(backbone.hidden_dim)
        K = int(min(max(8, bottleneck_dim), D))

        # Caption -> expected video feature. Kept deliberately small.
        self.caption_to_video = nn.Sequential(
            nn.LayerNorm(D),
            nn.Linear(D, D),
            nn.GELU(),
            nn.Linear(D, D),
        )

        # "What vision adds beyond words" -> compact affective code.
        self.sensory_affect_projector = nn.Sequential(
            nn.LayerNorm(D),
            nn.Linear(D, K),
            nn.GELU(),
            nn.LayerNorm(K),
        )

        # Brain must learn the same training-time code.
        self.brain_affect_projector = nn.Sequential(
            nn.LayerNorm(D),
            nn.Linear(D, K),
            nn.GELU(),
            nn.LayerNorm(K),
        )

        self.sensory_affect_head = nn.Linear(K, 34)

        self.aux_weight = float(aux_weight)
        self.video_pred_weight = float(video_pred_weight)
        self.affect_weight = float(affect_weight)
        self.distill_weight = float(distill_weight)

        self.last_aux_losses: dict[str, torch.Tensor] = {}
        self.last_aux_metrics: dict[str, Any] = {}

        self.use_markers = use_markers
        if use_markers:
            segs = ("brain", "video", "caption", "question")
            self.markers = nn.ParameterDict(
                {
                    f"{s}_{b}": nn.Parameter(torch.randn(1, 1, D) * 0.02)
                    for s in segs
                    for b in ("start", "end")
                }
            )

    def _bb_dtype(self):
        p = next((p for p in self.backbone.parameters()), None)
        return p.dtype if p is not None else torch.float32

    def _text_segment(self, texts, B, device):
        ids, mask = self.backbone.tokenize(texts)
        if ids.shape[0] == 1 and B > 1:
            ids, mask = ids.expand(B, -1), mask.expand(B, -1)
        emb = self.backbone.embed_text(ids.to(device))
        return emb, mask.to(device)

    def _wrap(self, seg_name, emb, mask, B, device, dt):
        if not self.use_markers:
            return [emb], [mask]
        s = self.markers[f"{seg_name}_start"].to(device=device, dtype=dt).expand(B, -1, -1)
        e = self.markers[f"{seg_name}_end"].to(device=device, dtype=dt).expand(B, -1, -1)
        one = torch.ones(B, 1, device=device, dtype=torch.long)
        return [s, emb, e], [one, mask, one]

    def loss_with_aux(self, base_loss: torch.Tensor) -> torch.Tensor:
        """Combine task loss with SGAR objectives."""
        if not self.last_aux_losses:
            return base_loss

        total_aux = base_loss.sum() * 0.0
        if "video_pred" in self.last_aux_losses:
            total_aux = total_aux + self.video_pred_weight * self.last_aux_losses["video_pred"]
        if "affect" in self.last_aux_losses:
            total_aux = total_aux + self.affect_weight * self.last_aux_losses["affect"]
        if "distill" in self.last_aux_losses:
            total_aux = total_aux + self.distill_weight * self.last_aux_losses["distill"]
        return base_loss + self.aux_weight * total_aux

    def forward(self, fmri, video=None, caption=None, target_z=None):
        device = fmri.device
        B = fmri.shape[0]
        dt = self._bb_dtype()

        self.last_aux_losses = {}
        self.last_aux_metrics = {}

        segs, masks = [], []
        raw: dict[str, tuple[torch.Tensor, torch.Tensor]] = {}

        for seg in token_order(self.modalities):
            if seg == "brain":
                emb = self.brain_projector(self.encoder(fmri)).to(dt)
                m = torch.ones(B, emb.shape[1], device=device, dtype=torch.long)
            elif seg == "video":
                if self.video_projector is None or video is None:
                    raise ValueError("video modality is active but video/video_projector is missing")
                emb = self.video_projector(video).to(dt)
                m = torch.ones(B, emb.shape[1], device=device, dtype=torch.long)
            elif seg == "caption":
                if caption is None:
                    raise ValueError("caption modality is active but caption is missing")
                emb, m = self._text_segment(
                    [caption_field(c) for c in caption], B, device
                )
                emb = emb.to(dt)
            elif seg == "question":
                emb, m = self._text_segment([self._question], B, device)
                emb = emb.to(dt)
            else:
                raise ValueError(f"unknown segment: {seg}")

            raw[seg] = (emb, m)
            e_list, m_list = self._wrap(seg, emb, m, B, device, dt)
            segs.extend(e_list)
            masks.extend(m_list)

        embeds = torch.cat(segs, dim=1)
        mask = torch.cat(masks, dim=1)
        embeds, mask = compact_valid_tokens(embeds, mask)
        pooled = self.backbone(embeds, mask).to(self.head.fc.weight.dtype)
        pred = self.head(pooled)

        # The full SGAR decomposition needs both privileged modalities.
        if self.training and all(k in raw for k in ("brain", "video", "caption")):
            brain_repr = masked_mean(*raw["brain"]).float()
            video_repr = masked_mean(*raw["video"]).float()
            caption_repr = masked_mean(*raw["caption"]).float()

            # Stage 1 is an explicit conditional predictor. Detaching its input
            # prevents the text embedding itself from drifting merely to make
            # video prediction easy.
            pred_video = self.caption_to_video(caption_repr.detach())

            # The decomposition is treated as a teacher construction: affect
            # gradients must not game E[V|C] or the video representation to
            # manufacture an easy residual. Only the sensory-affect projector
            # learns from the affect objective below.
            visual_residual = video_repr.detach() - pred_video.detach()

            teacher_code = self.sensory_affect_projector(visual_residual)
            brain_code = self.brain_affect_projector(brain_repr)

            # Stage 1: make E[V|C] a real conditional predictor.
            loss_video_pred = F.smooth_l1_loss(
                pred_video, video_repr.detach()
            )

            # Stage 2: only the affect-predictive part of the visual residual
            # should become the teacher code. Ground truth is preferred.
            if target_z is not None:
                affect_target = target_z.to(
                    device=device, dtype=self.sensory_affect_head.weight.dtype
                )
                target_source = "ground_truth"
            else:
                # Forward-compatible fallback. Because the normal prediction is
                # task-supervised outside this module, its detached value is a
                # better affect target than leaving the residual unconstrained.
                affect_target = pred.detach().to(self.sensory_affect_head.weight.dtype)
                target_source = "detached_model_prediction"

            teacher_z = self.sensory_affect_head(
                teacher_code.to(self.sensory_affect_head.weight.dtype)
            )
            loss_affect = F.mse_loss(teacher_z, affect_target)

            # Stage 3: transfer the selected sensory-affective code to brain.
            loss_distill = cosine_distill_loss(brain_code, teacher_code.detach())

            self.last_aux_losses = {
                "video_pred": loss_video_pred,
                "affect": loss_affect,
                "distill": loss_distill,
            }

            with torch.no_grad():
                residual_ratio = (
                    visual_residual.norm(dim=-1).mean()
                    / video_repr.norm(dim=-1).mean().clamp_min(1e-8)
                )
                code_cos = 1.0 - cosine_distill_loss(
                    brain_code.detach(), teacher_code.detach()
                )

            self.last_aux_metrics = {
                "target_source": target_source,
                "visual_residual_norm_ratio": float(residual_ratio.cpu()),
                "brain_teacher_code_cosine": float(code_cos.cpu()),
            }

        return pred
