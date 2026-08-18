"""EmoBrainModel — Cross-Subject Consensus-Gated Alignment (CGA).

Drop-in-oriented variant for the original EmoBrainModel.

Core idea
---------
Video/caption are stimulus-level privileged modalities; fMRI is subject-specific.
Therefore privileged modalities should supervise only neural structure that is
reproducibly evoked across subjects, not all individual variability.

The model learns a shared brain code. For each sample it computes a
leave-one-subject-out same-clip consensus and:

  - makes the shared code agree with that consensus,
  - aligns the shared code to the privileged teacher only in proportion to
    cross-subject reproducibility,
  - keeps a complementary private component unconstrained by privileged input.

Inference remains brain + question only.

Exact grouping
--------------
Best usage:

    pred = model(
        fmri,
        video=video,
        caption=caption,
        clip_id=batch["clip_id"],
        subject_id=batch.get("subject_id"),
    )

clip_id can be a tensor or a Python list/tuple of strings/ints.

Fallback when clip_id is absent:
    the model detects repeated stimuli from near-identical pooled video features
    within the current batch. This is convenient for a first test but exact
    clip_id is strongly recommended.

Training integration
--------------------
After the ordinary task loss:

    loss = model.loss_with_aux(loss)

Diagnostics:
    model.last_aux_losses
    model.last_aux_metrics
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pad_sequence

from project.code.fusion.prompt import question_text, caption_field, token_order


def compact_valid_tokens(embeds: torch.Tensor, mask: torch.Tensor):
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


def cosine_per_row(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return F.cosine_similarity(a.float(), b.float(), dim=-1, eps=1e-8)


class EmoBrainModel(nn.Module):
    """Original EmoBrainModel + cross-subject consensus-gated alignment."""

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
        consensus_weight: float = 1.0,
        privileged_weight: float = 1.0,
        orth_weight: float = 0.05,
        video_match_threshold: float = 0.9999,
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

        # Soft decomposition. The raw brain tokens still go to the backbone;
        # this branch only decides what privileged alignment is allowed to shape.
        self.shared_gate = nn.Sequential(
            nn.LayerNorm(D),
            nn.Linear(D, D),
            nn.Sigmoid(),
        )

        self.aux_weight = float(aux_weight)
        self.consensus_weight = float(consensus_weight)
        self.privileged_weight = float(privileged_weight)
        self.orth_weight = float(orth_weight)
        self.video_match_threshold = float(video_match_threshold)

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

    @staticmethod
    def _normalize_ids(values, B, name):
        if values is None:
            return None
        if torch.is_tensor(values):
            if values.ndim == 0:
                values = values.view(1)
            if len(values) != B:
                raise ValueError(f"{name} length {len(values)} != batch {B}")
            vals = values.detach().cpu().tolist()
            return [str(v) for v in vals]
        if isinstance(values, (list, tuple)):
            if len(values) != B:
                raise ValueError(f"{name} length {len(values)} != batch {B}")
            return [str(v) for v in values]
        raise TypeError(f"{name} must be tensor/list/tuple or None")

    def _peer_masks_from_ids(self, clip_ids, B, device):
        peer = torch.zeros(B, B, dtype=torch.bool, device=device)
        groups = defaultdict(list)
        for i, key in enumerate(clip_ids):
            groups[key].append(i)
        for idxs in groups.values():
            if len(idxs) < 2:
                continue
            ix = torch.tensor(idxs, device=device, dtype=torch.long)
            peer[ix[:, None], ix[None, :]] = True
        peer.fill_diagonal_(False)
        return peer

    def _peer_masks_from_video(self, video_repr):
        """Fallback: repeated stimulus if pooled video embeddings are almost equal."""
        x = F.normalize(video_repr.float().detach(), dim=-1, eps=1e-8)
        sim = x @ x.transpose(0, 1)
        peer = sim >= self.video_match_threshold
        peer.fill_diagonal_(False)
        return peer

    def loss_with_aux(self, base_loss: torch.Tensor) -> torch.Tensor:
        if not self.last_aux_losses:
            return base_loss
        total = base_loss.sum() * 0.0
        if "consensus" in self.last_aux_losses:
            total = total + self.consensus_weight * self.last_aux_losses["consensus"]
        if "privileged" in self.last_aux_losses:
            total = total + self.privileged_weight * self.last_aux_losses["privileged"]
        if "orth" in self.last_aux_losses:
            total = total + self.orth_weight * self.last_aux_losses["orth"]
        return base_loss + self.aux_weight * total

    def forward(
        self,
        fmri,
        video=None,
        caption=None,
        clip_id=None,
        subject_id=None,  # kept for logging/future subject-aware extensions
    ):
        # subject_id is used only to exclude same-subject peers; it is never
        # embedded or provided to the prediction path.
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

        ordered = [(name, *raw[name]) for name in token_order(self.modalities)]
        pooled = self._run_backbone_from_segments(ordered, B, device, dt)
        pred = self.head(pooled.to(self.head.fc.weight.dtype))

        if self.training and "brain" in raw and ("video" in raw or "caption" in raw):
            brain_repr = masked_mean(*raw["brain"]).float()
            gate = self.shared_gate(brain_repr)
            shared = gate * brain_repr
            private = (1.0 - gate) * brain_repr

            # Exact grouping is preferred.
            clip_ids = self._normalize_ids(clip_id, B, "clip_id")
            subject_ids = self._normalize_ids(subject_id, B, "subject_id")
            if clip_ids is not None:
                peer_mask = self._peer_masks_from_ids(clip_ids, B, device)
                grouping_source = "clip_id"
            elif "video" in raw:
                video_repr = masked_mean(*raw["video"])
                peer_mask = self._peer_masks_from_video(video_repr)
                grouping_source = "video_similarity_fallback"
            else:
                peer_mask = torch.zeros(B, B, dtype=torch.bool, device=device)
                grouping_source = "none"

            # A consensus peer must come from a different subject whenever
            # subject identity is available. This avoids treating repeated
            # windows/trials from the same person as cross-subject evidence.
            if subject_ids is not None:
                same_subject = torch.zeros(B, B, dtype=torch.bool, device=device)
                groups = defaultdict(list)
                for i, sid in enumerate(subject_ids):
                    groups[sid].append(i)
                for idxs in groups.values():
                    ix = torch.tensor(idxs, device=device, dtype=torch.long)
                    same_subject[ix[:, None], ix[None, :]] = True
                peer_mask = peer_mask & (~same_subject)

            peer_count = peer_mask.sum(dim=1)
            valid = peer_count > 0

            if valid.any():
                weights = peer_mask.to(shared.dtype)
                consensus = (weights @ shared) / peer_count.clamp_min(1).to(shared.dtype).unsqueeze(-1)

                # Leave-one-out consensus agreement.
                cons_cos = cosine_per_row(shared[valid], consensus[valid].detach())
                loss_consensus = (1.0 - cons_cos).mean()

                # Privileged-only teacher.
                priv = []
                if "video" in raw:
                    priv.append(("video", *raw["video"]))
                if "caption" in raw:
                    priv.append(("caption", *raw["caption"]))
                priv.append(("question", *raw["question"]))
                # The privileged representation is a fixed target for this
                # auxiliary objective. Relational matching avoids assuming that
                # backbone pooled features and brain-token features share the
                # same coordinate system or even the same dimensionality.
                with torch.no_grad():
                    teacher_repr = self._run_backbone_from_segments(
                        priv, B, device, dt
                    )

                # Reproducibility is a *gate*, not a target. Map cosine [-1,1]
                # to [0,1] and detach so the model cannot game its own weights.
                reliability = ((cosine_per_row(
                    shared.detach(), consensus.detach()
                ) + 1.0) * 0.5).clamp(0.0, 1.0)

                shared_n = F.normalize(shared.float(), dim=-1, eps=1e-8)
                teacher_n = F.normalize(teacher_repr.float(), dim=-1, eps=1e-8)
                shared_sim = shared_n @ shared_n.transpose(0, 1)
                teacher_sim = teacher_n @ teacher_n.transpose(0, 1)

                ij = torch.triu_indices(B, B, offset=1, device=device)
                pair_valid = valid[ij[0]] & valid[ij[1]]
                if pair_valid.any():
                    pair_rel = torch.sqrt(
                        reliability[ij[0]] * reliability[ij[1]]
                    ).detach()
                    per_pair = F.smooth_l1_loss(
                        shared_sim[ij[0], ij[1]],
                        teacher_sim[ij[0], ij[1]].detach(),
                        reduction="none",
                    )
                    w = pair_rel * pair_valid.to(pair_rel.dtype)
                    loss_privileged = (per_pair * w).sum() / w.sum().clamp_min(1e-6)
                else:
                    loss_privileged = pred.sum() * 0.0

                # Discourage the gate from putting the exact same information
                # into both paths. This is intentionally weak.
                shared_n = F.normalize(shared.float(), dim=-1, eps=1e-8)
                private_n = F.normalize(private.float(), dim=-1, eps=1e-8)
                loss_orth = (shared_n * private_n).sum(dim=-1).abs().mean()

                self.last_aux_losses = {
                    "consensus": loss_consensus,
                    "privileged": loss_privileged,
                    "orth": loss_orth,
                }
                self.last_aux_metrics = {
                    "grouping_source": grouping_source,
                    "subject_filter": subject_ids is not None,
                    "valid_consensus_samples": int(valid.sum().item()),
                    "mean_peer_count": float(peer_count[valid].float().mean().cpu()),
                    "mean_reliability": float(reliability[valid].mean().cpu()),
                    "mean_shared_gate": float(gate.mean().detach().cpu()),
                }
            else:
                zero = pred.sum() * 0.0
                self.last_aux_losses = {
                    "consensus": zero,
                    "privileged": zero,
                    "orth": zero,
                }
                self.last_aux_metrics = {
                    "grouping_source": grouping_source,
                    "subject_filter": subject_ids is not None,
                    "valid_consensus_samples": 0,
                    "mean_peer_count": 0.0,
                    "mean_reliability": float("nan"),
                    "mean_shared_gate": float(gate.mean().detach().cpu()),
                }

        return pred
