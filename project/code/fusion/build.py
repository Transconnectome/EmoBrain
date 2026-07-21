"""build_model(cfg) -> EmoBrainModel. The config factory (spec §10 schema).

Swapping encoder / projector / backbone is a config edit; dims flow so nothing
downstream hardcodes an upstream size.
    brain projector  in_dim = encoder.out_dim,   llm_dim = backbone.hidden_dim
    video projector  in_dim = video.dim,         llm_dim = backbone.hidden_dim
    head             hidden_dim = backbone.hidden_dim

cfg keys. encoder{type,adapt,...}, projector{type,n_tokens,...},
backbone{type,...}, modalities{brain,video,caption}, video{dim,n_tokens} (if video).
"""

from __future__ import annotations

from project.code.brain_encoder.registry import build_encoder
from project.code.adapters.projector import build_projector
from project.code.fusion.backbone import build_backbone
from project.code.fusion.head import Linear34
from project.code.fusion.model import EmoBrainModel


def build_model(cfg: dict) -> EmoBrainModel:
    backbone = build_backbone(cfg.get("backbone", {"type": "stub"}))
    D = backbone.hidden_dim

    encoder = build_encoder(cfg["encoder"])
    brain_projector = build_projector(cfg.get("projector", {"type": "mlp"}),
                                      in_dim=encoder.out_dim, llm_dim=D)

    mods = cfg.get("modalities", {"brain": True})
    video_projector = None
    if mods.get("video"):
        v = cfg["video"]
        video_projector = build_projector(
            {"type": v.get("type", "mlp"), "n_tokens": v.get("n_tokens", 16)},
            in_dim=v["dim"], llm_dim=D)

    head = Linear34(hidden_dim=D)
    return EmoBrainModel(encoder=encoder, brain_projector=brain_projector,
                         backbone=backbone, head=head,
                         video_projector=video_projector, modalities=mods)
