"""EmoBrainModel. Fixed wiring for any (encoder, projector, backbone, head).

The wiring below never changes when a component is swapped; only the config
does. That is the whole point of the registry + factory (NV3 swappable adapter).

Flow (skeleton).
    fmri -> encoder -> projector -> brain tokens [B, N_b, H] ┐
    text -> backbone.embed_text  -> text embeds  [B, L,  H]  ├ concat
                                                             ┘
    concat -> backbone -> pooled [B, H] -> head -> [B, 34]

modalities toggles which streams are active. Student = brain only; the teacher
adds video and caption later (video encoder + caption field, Step 6). Setting
brain=False gives the brain-ablated student for the distillation sanity check.

Skeleton note. Brain tokens are prepended to the text embeds here. Placeholder
position insertion (implementation_spec 8-3) is a later refinement and is not
needed to validate wiring. Caption stays a separate field, never concatenated
into the question string.
"""
from __future__ import annotations

import torch
import torch.nn as nn


class EmoBrainModel(nn.Module):
    def __init__(self, encoder, projector, backbone, head, modalities):
        super().__init__()
        self.encoder = encoder
        self.projector = projector
        self.backbone = backbone
        self.head = head
        self.modalities = dict(modalities)

    def _backbone_dtype(self):
        return next(self.backbone.parameters()).dtype

    def forward(self, fmri=None, text_ids=None, text_mask=None):
        parts, masks = [], []

        if self.modalities.get("brain", True):
            if fmri is None:
                raise ValueError("modalities.brain is on but fmri is None")
            brain_tok = self.projector(self.encoder(fmri))   # [B, N_b, H]
            # encoder/projector are fp32; match the backbone dtype (bf16 for
            # qwen, fp32 for stub) so brain and text tokens concat cleanly.
            brain_tok = brain_tok.to(self._backbone_dtype())
            parts.append(brain_tok)
            ones = torch.ones(
                brain_tok.shape[:2], device=brain_tok.device, dtype=torch.long
            )
            masks.append(ones)

        if text_ids is not None:
            text_emb = self.backbone.embed_text(text_ids)    # [B, L, H]
            parts.append(text_emb)
            if text_mask is None:
                text_mask = torch.ones(
                    text_ids.shape, device=text_ids.device, dtype=torch.long
                )
            masks.append(text_mask.long())

        if not parts:
            raise ValueError("no active input stream (brain off and no text)")

        seq = torch.cat(parts, dim=1)                        # [B, L_tot, H]
        mask = torch.cat(masks, dim=1)                       # [B, L_tot]
        pooled = self.backbone(inputs_embeds=seq, attention_mask=mask)  # [B, H]
        # backbone may run in bf16 (qwen); head + loss + metrics are fp32.
        pooled = pooled.to(next(self.head.parameters()).dtype)
        return self.head(pooled)                             # [B, 34]
