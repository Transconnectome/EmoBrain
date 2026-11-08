"""CPU wiring smoke for the swappable model skeleton (no train, no download).

Verifies.
    - build_model(cfg) assembles encoder -> projector -> backbone -> head with
      dims flowing automatically (contract works).
    - forward with dummy tensors returns [B, 34].
    - config-driven SWAP works. Changing one value (n_tokens, encoder out_dim)
      or a toggle (modalities.brain) rebuilds a different model with no code
      change. This is the "script only names the model" property.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/model_build_smoke.sh
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402
import yaml  # noqa: E402

from project.models.build import build_model  # noqa: E402
from project.models.registry import available  # noqa: E402


def load_cfg(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run_once(cfg: dict, tag: str, b: int = 4, roi_dim: int = 450, seq_len: int = 6):
    model = build_model(cfg)
    model.eval()
    fmri = torch.randn(b, roi_dim)
    text_ids = torch.randint(0, 1000, (b, seq_len))
    text_mask = torch.ones(b, seq_len, dtype=torch.long)
    with torch.no_grad():
        out = model(fmri=fmri, text_ids=text_ids, text_mask=text_mask)
    n_params = sum(p.numel() for p in model.parameters())
    proj = cfg["projector"]
    print(
        f"[{tag:22s}] out={tuple(out.shape)} params={n_params:>9,} "
        f"| enc={cfg['encoder']['name']}(out={cfg['encoder'].get('out_dim')}) "
        f"proj={proj['name']}({proj.get('n_tokens')}tok) "
        f"bb={cfg['backbone']['name']}(H={cfg['backbone'].get('hidden_dim')}) "
        f"brain={cfg['modalities'].get('brain')}"
    )
    assert out.shape == (b, 34), f"expected (B,34), got {tuple(out.shape)}"
    assert torch.isfinite(out).all(), "non-finite output"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--config",
        default=str(REPO_ROOT / "project/configs/smoke_e1_stub.yaml"),
    )
    args = ap.parse_args()

    print("registered components:")
    for kind in ("encoder", "projector", "backbone", "head"):
        print(f"    {kind:10s}: {available(kind)}")
    print()

    cfg = load_cfg(args.config)
    run_once(cfg, tag="base")

    # swap 1: n_tokens 8 -> 16 (config-only change)
    c = copy.deepcopy(cfg)
    c["projector"]["n_tokens"] = 16
    run_once(c, tag="swap n_tokens=16")

    # swap 2: encoder capacity change (dims re-flow automatically)
    c = copy.deepcopy(cfg)
    c["encoder"]["hidden"] = 256
    c["encoder"]["out_dim"] = 256
    run_once(c, tag="swap enc out_dim=256")

    # swap 3: brain-ablated student (text only) for distillation sanity later
    c = copy.deepcopy(cfg)
    c["modalities"]["brain"] = False
    run_once(c, tag="brain OFF (ablation)")

    print("\nSMOKE OK")


if __name__ == "__main__":
    main()
