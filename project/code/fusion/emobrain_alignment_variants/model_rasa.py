"""EmoBrainModel — Residual Affective Structure Alignment (RASA).

Drop-in model variant for the original EmoBrainModel.

Core idea
---------
The normal teacher concatenates video/caption/brain/question and relies on the
backbone to discover useful multimodal structure. RASA adds a training-time
auxiliary objective that aligns *brain relational geometry* to a privileged
(video+caption+question) teacher geometry only after removing geometry that is
already explained by generic video/caption similarity.

Inference is unchanged:
    brain + question -> backbone -> 34-D z

Training integration
--------------------
The forward API remains compatible with the original model:

    pred = model(fmri, video=video, caption=caption)

After computing the normal task loss, add exactly one line:

    loss = model.loss_with_aux(loss)

Without this line the file is still forward-compatible, but the RASA objective
cannot affect training because an auxiliary objective must participate in
backpropagation.

The most useful diagnostics are available in:
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
    """Mean-pool valid tokens only."""
    w = mask.to(dtype=x.dtype).unsqueeze(-1)
    return (x * w).sum(dim=1) / w.sum(dim=1).clamp_min(1.0)


def pairwise_cosine_distance_vector(x: torch.Tensor) -> torch.Tensor:
    """Upper-triangular pairwise cosine distances, shape (B*(B-1)/2,)."""
    if x.ndim != 2:
        raise ValueError(f"expected (B,D), got {tuple(x.shape)}")
    B = x.shape[0]
    if B < 2:
        return x.new_empty((0,))
    xn = F.normalize(x.float(), dim=-1, eps=1e-8)
    dist = 1.0 - xn @ xn.transpose(0, 1)
    ij = torch.triu_indices(B, B, offset=1, device=x.device)
    return dist[ij[0], ij[1]]


def pearson_corr(x: torch.Tensor, y: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """Stable differentiable Pearson correlation."""
    x = x.float()
    y = y.float()
    x = x - x.mean()
    y = y - y.mean()
    denom = x.norm() * y.norm()
    return (x * y).sum() / denom.clamp_min(eps)


def partial_residual(
    y: torch.Tensor,
    nuisance: torch.Tensor,
    *,
    alpha: float,
    ridge: float,
) -> torch.Tensor:
    """Remove an alpha fraction of the component linearly explained by nuisance.

    y:        (P,)
    nuisance: (P,K)

    The regression is intentionally simple: the scientific claim is about
    *which geometry* is supervised, not about a complicated residualizer.
    """
    if nuisance.ndim != 2 or nuisance.shape[0] != y.shape[0]:
        raise ValueError(
            f"bad nuisance shape {tuple(nuisance.shape)} for y {tuple(y.shape)}"
        )
    if nuisance.shape[1] == 0:
        return y

    yf = y.float()
    X = nuisance.float()

    # Centering removes the need for an explicit intercept.
    yc = yf - yf.mean()
    Xc = X - X.mean(dim=0, keepdim=True)

    k = Xc.shape[1]
    eye = torch.eye(k, device=Xc.device, dtype=Xc.dtype)
    gram = Xc.transpose(0, 1) @ Xc + float(ridge) * eye
    rhs = Xc.transpose(0, 1) @ yc
    beta = torch.linalg.solve(gram, rhs)
    explained = Xc @ beta
    return yc - float(alpha) * explained


class EmoBrainModel(nn.Module):
    """Original EmoBrainModel + residual affective structure alignment."""

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
        aux_weight: float = 0.10,
        residual_alpha: float = 0.50,
        residual_ridge: float = 1e-3,
        min_pairs: int = 6,
    ):
        super().__init__()
        self.encoder = encoder
        self.brain_projector = brain_projector
        self.video_projector = video_projector
        self.backbone = backbone
        self.head = head
        self.modalities = modalities or {"brain": True}
        self._question = question_text()

        self.aux_weight = float(aux_weight)
        self.residual_alpha = float(residual_alpha)
        self.residual_ridge = float(residual_ridge)
        self.min_pairs = int(min_pairs)

        self.last_aux_losses: dict[str, torch.Tensor] = {}
        self.last_aux_metrics: dict[str, Any] = {}

        self.use_markers = use_markers
        if use_markers:
            D = backbone.hidden_dim
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
        """Prepend <seg_start> and append <seg_end> around a segment."""
        if not self.use_markers:
            return [emb], [mask]
        s = self.markers[f"{seg_name}_start"].to(device=device, dtype=dt).expand(B, -1, -1)
        e = self.markers[f"{seg_name}_end"].to(device=device, dtype=dt).expand(B, -1, -1)
        one = torch.ones(B, 1, device=device, dtype=torch.long)
        return [s, emb, e], [one, mask, one]

    def _run_backbone_from_segments(self, ordered_segments, B, device, dt):
        segs, masks = [], []
        for name, emb, mask in ordered_segments:
            e_list, m_list = self._wrap(name, emb, mask, B, device, dt)
            segs.extend(e_list)
            masks.extend(m_list)
        embeds = torch.cat(segs, dim=1)
        mask = torch.cat(masks, dim=1)
        embeds, mask = compact_valid_tokens(embeds, mask)
        return self.backbone(embeds, mask)

    def _zero_aux(self, ref: torch.Tensor):
        # Connected zero makes loss_with_aux safe under DDP / AMP.
        return ref.sum() * 0.0

    def loss_with_aux(self, base_loss: torch.Tensor) -> torch.Tensor:
        """Add the RASA objective to an externally computed task loss."""
        aux = self.last_aux_losses.get("rasa")
        if aux is None:
            return base_loss
        return base_loss + self.aux_weight * aux

    def forward(self, fmri, video=None, caption=None):
        device = fmri.device
        B = fmri.shape[0]
        dt = self._bb_dtype()

        self.last_aux_losses = {}
        self.last_aux_metrics = {}

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

        # Original forward path.
        ordered = [(name, *raw[name]) for name in token_order(self.modalities)]
        pooled = self._run_backbone_from_segments(ordered, B, device, dt)
        pred = self.head(pooled.to(self.head.fc.weight.dtype))

        # RASA is meaningful only in the privileged teacher condition.
        if self.training and "brain" in raw and ("video" in raw or "caption" in raw):
            brain_repr = masked_mean(*raw["brain"])

            nuisance_cols = []
            if "video" in raw:
                video_repr = masked_mean(*raw["video"]).detach()
                nuisance_cols.append(pairwise_cosine_distance_vector(video_repr))
            if "caption" in raw:
                caption_repr = masked_mean(*raw["caption"]).detach()
                nuisance_cols.append(pairwise_cosine_distance_vector(caption_repr))

            # Build a privileged-only teacher so the target is not defined using
            # the brain representation that it supervises.
            privileged_order = []
            if "video" in raw:
                privileged_order.append(("video", *raw["video"]))
            if "caption" in raw:
                privileged_order.append(("caption", *raw["caption"]))
            privileged_order.append(("question", *raw["question"]))

            # Teacher is a target only; no auxiliary gradient should update the
            # privileged pathway, and no_grad saves a second backbone graph.
            with torch.no_grad():
                teacher_repr = self._run_backbone_from_segments(
                    privileged_order, B, device, dt
                )

            d_brain = pairwise_cosine_distance_vector(brain_repr)
            d_teacher = pairwise_cosine_distance_vector(teacher_repr)
            nuisance = torch.stack(nuisance_cols, dim=1).detach()

            if d_brain.numel() >= self.min_pairs:
                r_brain = partial_residual(
                    d_brain,
                    nuisance,
                    alpha=self.residual_alpha,
                    ridge=self.residual_ridge,
                )
                r_teacher = partial_residual(
                    d_teacher.detach(),
                    nuisance,
                    alpha=self.residual_alpha,
                    ridge=self.residual_ridge,
                )
                corr = pearson_corr(r_brain, r_teacher)
                rasa_loss = 1.0 - corr
                self.last_aux_losses["rasa"] = rasa_loss
                self.last_aux_metrics.update(
                    {
                        "rasa_corr": float(corr.detach().cpu()),
                        "num_pairs": int(d_brain.numel()),
                        "residual_alpha": self.residual_alpha,
                    }
                )
            else:
                self.last_aux_losses["rasa"] = self._zero_aux(pred)
                self.last_aux_metrics.update(
                    {
                        "rasa_corr": float("nan"),
                        "num_pairs": int(d_brain.numel()),
                        "residual_alpha": self.residual_alpha,
                    }
                )

        return pred
