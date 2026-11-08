"""Name -> class registry and config-driven build for model components.

Every component registers under one of four kinds (encoder, projector,
backbone, head). build() instantiates by name, merging config hyperparams
with dims injected by the factory (in_dim, llm_dim, hidden_dim). This is what
lets a script swap a component by changing one config line.

Usage.
    from project.models.registry import register, build

    @register("encoder", "e1_raw_roi")
    class E1RawROI(BrainEncoder): ...

    enc = build("encoder", {"name": "e1_raw_roi", "roi_dim": 450})
    proj = build("projector", {"name": "mlp", "n_tokens": 8},
                 in_dim=enc.out_dim, llm_dim=64)   # injected dims
"""
from __future__ import annotations

_KINDS = ("encoder", "projector", "backbone", "head")
_REGISTRY: dict[str, dict[str, type]] = {k: {} for k in _KINDS}


def register(kind: str, name: str):
    """Decorator. Register a component class under (kind, name)."""
    if kind not in _REGISTRY:
        raise KeyError(f"unknown kind {kind!r}, expected one of {_KINDS}")

    def deco(cls):
        if name in _REGISTRY[kind]:
            raise KeyError(f"{kind}:{name} already registered")
        _REGISTRY[kind][name] = cls
        return cls

    return deco


def build(kind: str, cfg: dict, **injected):
    """Instantiate a registered component. cfg = {name, <hyperparams>}.

    injected dims (in_dim / llm_dim / hidden_dim) come from the factory so
    downstream components never hardcode upstream dims.
    """
    if kind not in _REGISTRY:
        raise KeyError(f"unknown kind {kind!r}")
    cfg = dict(cfg)
    name = cfg.pop("name")
    if name not in _REGISTRY[kind]:
        raise KeyError(
            f"{kind}:{name!r} not registered. available = {available(kind)}"
        )
    return _REGISTRY[kind][name](**cfg, **injected)


def available(kind: str) -> list[str]:
    """Sorted names registered under a kind."""
    return sorted(_REGISTRY[kind])
