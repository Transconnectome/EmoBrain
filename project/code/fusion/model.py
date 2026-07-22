"""EmoBrainModel. Assembles encoder x projector x prompt x backbone x head.

One class serves both roles (spec §6-1). The modality flags decide the token
order and which segments exist.
    teacher  brain + video + caption + question
    student  brain + question   (the inference form; final eval must use this)

Segment sources.
    brain    encoder -> brain projector          (vector, projector)
    video    video projector                     (vector, projector, teacher)
    caption  tokenizer -> embed_text             (text, NO projector)
    question tokenizer -> embed_text (fixed)      (text, NO projector)

Output. 34-dim z-space regression, no activation, no softmax (spec §6-6, §14).
"""

from __future__ import annotations

import torch
import torch.nn as nn
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


class EmoBrainModel(nn.Module):
    def __init__(self, encoder, brain_projector, backbone, head,
                 video_projector=None, modalities: dict | None = None,
                 use_markers: bool = True):
        super().__init__()
        self.encoder = encoder
        self.brain_projector = brain_projector
        self.video_projector = video_projector
        self.backbone = backbone
        self.head = head
        self.modalities = modalities or {"brain": True}
        self._question = question_text()

        # Segment boundary markers (red-team C4, spec §6-5). Fresh learnable
        # <seg_start>/<seg_end> embeddings so the LLM knows where each modality
        # begins and ends, instead of relying on order alone. Separate from the
        # backbone's own BOS/EOS.
        self.use_markers = use_markers
        if use_markers:
            D = backbone.hidden_dim
            segs = ("brain", "video", "caption", "question")
            self.markers = nn.ParameterDict({
                f"{s}_{b}": nn.Parameter(torch.randn(1, 1, D) * 0.02)
                for s in segs for b in ("start", "end")
            })

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
        """Prepend <seg_start> and append <seg_end> around a segment."""
        if not self.use_markers:
            return [emb], [mask]
        s = self.markers[f"{seg_name}_start"].to(dt).expand(B, -1, -1)
        e = self.markers[f"{seg_name}_end"].to(dt).expand(B, -1, -1)
        one = torch.ones(B, 1, device=device, dtype=torch.long)
        return [s, emb, e], [one, mask, one]

    def forward(self, fmri, video=None, caption=None):
        device = fmri.device
        B = fmri.shape[0]
        dt = self._bb_dtype()
        segs, masks = [], []

        for seg in token_order(self.modalities):
            if seg == "brain":
                emb = self.brain_projector(self.encoder(fmri)).to(dt)
                m = torch.ones(B, emb.shape[1], device=device, dtype=torch.long)
            elif seg == "video":
                emb = self.video_projector(video).to(dt)
                m = torch.ones(B, emb.shape[1], device=device, dtype=torch.long)
            elif seg == "caption":
                emb, m = self._text_segment([caption_field(c) for c in caption], B, device)
                emb = emb.to(dt)
            elif seg == "question":
                emb, m = self._text_segment([self._question], B, device)
                emb = emb.to(dt)
            e_list, m_list = self._wrap(seg, emb, m, B, device, dt)
            segs.extend(e_list)
            masks.extend(m_list)

        embeds = torch.cat(segs, dim=1)
        mask = torch.cat(masks, dim=1)
        embeds, mask = compact_valid_tokens(embeds, mask)
        pooled = self.backbone(embeds, mask).to(self.head.fc.weight.dtype)
        return self.head(pooled)                       # (B, 34) z-space
