"""build_model(cfg) -> EmoBrainModel. Config-driven assembly (the factory).

A script names components in a config and this wires them. Dims flow so no
downstream component hardcodes an upstream dim.
    projector gets in_dim = encoder.out_dim, llm_dim = backbone.hidden_dim
    head      gets hidden_dim = backbone.hidden_dim
Swapping encoder / projector / backbone / head is therefore a one-line config
edit with no other code change.

cfg (dict).
    encoder   : {name, <hyperparams>}
    projector : {name, <hyperparams>}      # in_dim / llm_dim injected
    backbone  : {name, <hyperparams>}
    head      : {name, <hyperparams>}      # hidden_dim injected
    modalities: {brain, video, caption}    # optional, default brain-only

Importing this module registers the CPU-safe components (encoder, mlp
projector, stub backbone, linear34 head). The qwen backbone imports
transformers, so it is imported lazily only when selected.
"""
from __future__ import annotations

# side-effect imports register the components (no transformers dependency)
import project.models.encoders.identity  # noqa: F401
import project.models.encoders.ridge_latent  # noqa: F401
import project.models.encoders.vec_mlp  # noqa: F401
import project.models.encoders.vit_fmri  # noqa: F401  (transformers lazy)
import project.models.projectors.mlp  # noqa: F401
import project.models.backbones.stub  # noqa: F401
import project.models.heads.linear34  # noqa: F401
from project.models.emobrain_model import EmoBrainModel
from project.models.registry import build


def build_model(cfg: dict) -> EmoBrainModel:
    if cfg["backbone"]["name"] == "qwen":
        import project.models.backbones.qwen  # noqa: F401  (lazy: transformers)

    backbone = build("backbone", cfg["backbone"])
    encoder = build("encoder", cfg["encoder"])
    projector = build(
        "projector", cfg["projector"],
        in_dim=encoder.out_dim, llm_dim=backbone.hidden_dim,
    )
    head = build("head", cfg["head"], hidden_dim=backbone.hidden_dim)

    # optional video projector (vector modality, teacher path)
    video_projector = None
    mods = cfg.get("modalities", {"brain": True})
    if mods.get("video"):
        vcfg = cfg["video"]
        video_projector = build(
            "projector", {"name": "mlp", "n_tokens": vcfg.get("n_tokens", 8)},
            in_dim=vcfg["dim"], llm_dim=backbone.hidden_dim,
        )

    return EmoBrainModel(
        encoder=encoder,
        projector=projector,
        backbone=backbone,
        head=head,
        modalities=mods,
        video_projector=video_projector,
    )
