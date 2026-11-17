"""LLM-free label-query emotion decoder (Query2Label for brain emotion).

N emotion queries cross-attend to brain (+video +semantic) tokens through a small
transformer decoder; a shared scalar head reads each query into that emotion's
log1p_z score. No LLM in the loop.

The design point that carries the science: queries are SEMANTIC. Each emotion enters
as its name's sentence embedding (all-mpnet-base-v2, the same encoder that produced
the caption embeddings), mapped into the model space by a SHARED learned projection.
Because that projection and the decoder are shared across emotions, an emotion never
seen in training can still be queried at test time by instantiating its name
embedding. A fixed-taxonomy decoder cannot do this by construction, which is what
makes the held-out-emotion test a real test rather than a demonstration.

query_mode
    frozen    queries are the fixed semantic embeddings. Cleanest zero-shot claim:
              no per-emotion learned parameter exists at all.
    residual  fixed semantic embedding + a learnable per-emotion delta. Seen emotions
              may adapt; unseen emotions get delta = 0, so zero-shot still works.
              This is the disciplined form given EmoGrowth's (ICML 2025) finding that
              naive frozen LLM label embeddings can hurt.
    free      fully learnable queries (semantic or random init). Zero-shot is
              impossible for unseen emotions; this is the control arm.

Brain tokens: roi_mean (B, N_ROI) -> one token per ROI (shared value embedding of the
scalar + a learned per-ROI positional embedding), so ROI identity survives and
per-emotion -> ROI attention is available for later interpretation.
"""

from __future__ import annotations

import torch
import torch.nn as nn

QUERY_MODES = ("frozen", "residual", "free")


class LabelQueryDecoder(nn.Module):
    def __init__(self, n_emotions: int = 34, d_model: int = 256, n_layers: int = 3,
                 n_heads: int = 8, n_roi: int = 450, video_dim: int = 1408,
                 caption_dim: int = 768, use_video: bool = False,
                 use_caption: bool = False, query_init: torch.Tensor | None = None,
                 query_mode: str = "residual", dropout: float = 0.1):
        super().__init__()
        if query_mode not in QUERY_MODES:
            raise ValueError(f"query_mode must be one of {QUERY_MODES}, got {query_mode!r}")
        if query_mode in ("frozen", "residual") and query_init is None:
            raise ValueError(f"query_mode={query_mode!r} requires semantic query_init")
        self.n_emotions = n_emotions
        self.use_video = use_video
        self.use_caption = use_caption
        self.query_mode = query_mode

        # --- memory side: brain (+ optional stimulus modalities) -----------------
        self.roi_value = nn.Linear(1, d_model)
        self.roi_pos = nn.Parameter(torch.randn(n_roi, d_model) * 0.02)
        self.type_brain = nn.Parameter(torch.zeros(1, 1, d_model))
        if use_video:
            self.video_proj = nn.Linear(video_dim, d_model)
            self.type_video = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)
        if use_caption:
            self.caption_proj = nn.Linear(caption_dim, d_model)
            self.type_caption = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)

        # --- query side ----------------------------------------------------------
        if query_init is not None:
            qi = query_init.detach().float().clone()
            if qi.shape[0] != n_emotions:
                raise ValueError(f"query_init has {qi.shape[0]} rows, expected {n_emotions}")
            d_sem = qi.shape[1]
        else:
            qi = torch.randn(n_emotions, d_model) * 0.02
            d_sem = d_model

        if query_mode == "free":
            # No frozen anchor: the queries themselves are the parameters.
            self.register_buffer("query_base", torch.zeros(n_emotions, d_sem))
            self.query_delta = nn.Parameter(qi)
        else:
            # Frozen semantic anchor; "residual" adds a learnable per-emotion delta.
            self.register_buffer("query_base", qi)
            if query_mode == "residual":
                self.query_delta = nn.Parameter(torch.zeros(n_emotions, d_sem))
            else:
                self.query_delta = None

        # SHARED semantic -> model-space map. This is what lets an unseen emotion be
        # queried: it is trained on seen emotions only but applies to any embedding.
        self.query_in = nn.Identity() if d_sem == d_model else nn.Linear(d_sem, d_model)

        layer = nn.TransformerDecoderLayer(d_model, n_heads, d_model * 4, dropout,
                                           batch_first=True)
        self.decoder = nn.TransformerDecoder(layer, n_layers)
        self.head = nn.Linear(d_model, 1)          # shared scalar readout

    # ------------------------------------------------------------------ queries
    def queries(self, query_idx: torch.Tensor | None = None) -> torch.Tensor:
        """(n_active, d_sem) query vectors. Unseen emotions keep delta = 0."""
        q = self.query_base
        if self.query_delta is not None:
            q = q + self.query_delta
        return q if query_idx is None else q[query_idx]

    def freeze_query_delta(self, held_out_idx) -> None:
        """Zero and detach the learnable delta for held-out emotions.

        Indexing already prevents gradient flow to unused rows, but optimisers with
        weight decay or momentum can still move them, which would silently leak
        training into a supposedly unseen emotion. This makes the guarantee explicit.
        """
        if self.query_delta is None:
            return
        with torch.no_grad():
            self.query_delta[held_out_idx] = 0.0

    # ------------------------------------------------------------------- forward
    def forward(self, brain, video=None, caption=None, query_idx=None):
        B = brain.shape[0]
        toks = [self.roi_value(brain.unsqueeze(-1)) + self.roi_pos[None] + self.type_brain]
        if self.use_video and video is not None:
            toks.append(self.video_proj(video)[:, None, :] + self.type_video)
        if self.use_caption and caption is not None:
            toks.append(self.caption_proj(caption)[:, None, :] + self.type_caption)
        memory = torch.cat(toks, dim=1)                              # (B, T, d)

        q = self.query_in(self.queries(query_idx))                   # (n_active, d)
        q = q[None].expand(B, -1, -1)
        out = self.decoder(q, memory)                                # (B, n_active, d)
        return self.head(out).squeeze(-1)                            # (B, n_active)
