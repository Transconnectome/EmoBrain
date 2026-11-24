"""EmoBrainModel. Fixed wiring for brain (+ optional video / caption) -> LLM -> head.

modalities toggles which streams are active.
    student : brain only.
    teacher : brain + video (vector -> video_projector) + caption (text tokens).
Sequence order (implementation_spec teacher): video, caption, brain, question.

Vector modalities (brain, video) go through a projector. Text (caption, question)
go through the tokenizer + embed_text, never a projector. Caption is a separate
field, never merged into the question string.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class EmoBrainModel(nn.Module):
    def __init__(self, encoder, projector, backbone, head, modalities,
                 video_projector=None):
        super().__init__()
        self.encoder = encoder
        self.projector = projector
        self.video_projector = video_projector   # None unless modalities.video
        self.backbone = backbone
        self.head = head
        self.modalities = dict(modalities)

    def _backbone_dtype(self):
        return next(self.backbone.parameters()).dtype

    def _vec_tokens(self, tok):
        tok = tok.to(self._backbone_dtype())
        mask = torch.ones(tok.shape[:2], device=tok.device, dtype=torch.long)
        return tok, mask

    def forward(self, fmri=None, video=None, caption_ids=None, caption_mask=None,
                text_ids=None, text_mask=None):
        parts, masks = [], []

        # order: video, caption, brain, question
        if self.modalities.get("video") and video is not None:
            vt = self.video_projector(video)                  # [B, N_v, H]
            t, m = self._vec_tokens(vt)
            parts.append(t); masks.append(m)

        if self.modalities.get("caption") and caption_ids is not None:
            ce = self.backbone.embed_text(caption_ids)        # [B, L_c, H]
            parts.append(ce)
            masks.append((caption_mask if caption_mask is not None
                          else torch.ones_like(caption_ids)).long())

        if self.modalities.get("brain", True):
            if fmri is None:
                raise ValueError("modalities.brain is on but fmri is None")
            bt = self.projector(self.encoder(fmri))           # [B, N_b, H]
            t, m = self._vec_tokens(bt)
            parts.append(t); masks.append(m)

        if text_ids is not None:
            te = self.backbone.embed_text(text_ids)           # [B, L_q, H]
            parts.append(te)
            masks.append((text_mask if text_mask is not None
                          else torch.ones_like(text_ids)).long())

        if not parts:
            raise ValueError("no active input stream")

        seq = torch.cat(parts, dim=1)
        mask = torch.cat(masks, dim=1)
        pooled = self.backbone(inputs_embeds=seq, attention_mask=mask)
        pooled = pooled.to(next(self.head.parameters()).dtype)
        return self.head(pooled)                              # [B, 34]
