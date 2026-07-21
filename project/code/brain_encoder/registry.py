"""Encoder registry. `encoder.type` in the config selects the class.

This is what makes the encoder swappable (NV3). Nothing else in the pipeline
knows which encoder is in use; it only relies on the (B, T_e, D_enc) contract
and on `.out_dim`.

Usage.
    from project.code.brain_encoder.registry import build_encoder, available
    enc = build_encoder({"type": "e1_proj", "adapt": "full", "in_dim": 450})
"""

from __future__ import annotations

from typing import Callable

_ENCODERS: dict[str, Callable] = {}


def register_encoder(name: str):
    def deco(cls):
        if name in _ENCODERS:
            raise KeyError(f"encoder {name!r} already registered")
        _ENCODERS[name] = cls
        return cls
    return deco


def available() -> list[str]:
    _autoload()
    return sorted(_ENCODERS)


def _autoload() -> None:
    """Import encoder modules so their @register_encoder runs.

    Heavy dependencies (peft, transformers, Brain-JEPA) are imported lazily
    INSIDE each encoder's __init__, so importing the module itself is cheap.
    """
    import importlib
    # lineup (2026-07-20): ridge baseline, ViT (Encoder 1), BFM (Encoder 2).
    # simple projection (old E1) was discarded.
    for mod in ("e2_ridge_encoder", "e_vit", "e_bfm"):
        try:
            importlib.import_module(f"project.code.brain_encoder.{mod}")
        except ImportError:
            pass                                  # optional dependency missing


def build_encoder(cfg: dict):
    """cfg = {"type": ..., "adapt": frozen|lora|full, **encoder kwargs}."""
    _autoload()
    cfg = dict(cfg)
    name = cfg.pop("type", None)
    if name not in _ENCODERS:
        raise KeyError(f"unknown encoder {name!r}. available={sorted(_ENCODERS)}")
    return _ENCODERS[name](**cfg)
