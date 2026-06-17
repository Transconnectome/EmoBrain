"""Path A pilot training entry. Fold 1, 5 subj pooled, LoRA on Qwen3-VL.

design.md Section 6. Pilot config (lr 1e-4, batch 8, 5 epoch, LoRA r16 a32).

Smoke mode (--smoke) skips backbone load. Verifies dataset + heads + loss flow only.
Full mode requires brainvlm_qwen_env (transformers==5.3.0.dev0).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from ..loss.multitask import MultiTaskWeights, total_loss
from ..model.brainvlm_path_a import BrainVLMConfig, BrainVLMPathA


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest")
    p.add_argument("--roi-dir")
    p.add_argument("--captions")
    p.add_argument("--va-targets")
    p.add_argument("--cat34-targets")
    p.add_argument("--fold", type=int, default=1)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--epochs", type=int, default=5)
    p.add_argument("--smoke", action="store_true", help="skeleton-only run on synthetic batch")
    return p.parse_args()


def make_loader(args: argparse.Namespace, split: str) -> DataLoader:
    from ..data.dataset import BrainVQADataset
    ds = BrainVQADataset(
        manifest_csv=args.manifest,
        roi_dir=args.roi_dir,
        caption_jsonl=args.captions,
        va_targets_csv=args.va_targets,
        cat34_targets_csv=args.cat34_targets,
        fold=args.fold,
        split=split,
    )
    return DataLoader(ds, batch_size=args.batch_size, shuffle=(split == "train"), num_workers=2)


def smoke_main(out_dir: Path) -> None:
    cfg = BrainVLMConfig()
    model = BrainVLMPathA(cfg)
    weights = MultiTaskWeights()

    B = 4
    fake_pooled = torch.randn(B, cfg.d_llm)
    va_tgt = torch.randn(B, 2)
    cat_tgt = torch.rand(B, 34)
    cat_tgt = cat_tgt / cat_tgt.sum(dim=1, keepdim=True)

    va_pred = model.va_head(fake_pooled)
    cat34_logits = model.cat34_head(fake_pooled)
    fake_ce = torch.tensor(1.0, requires_grad=True)
    losses = total_loss(fake_ce, va_pred, va_tgt, cat34_logits, cat_tgt, weights)
    losses["total"].backward()
    print(
        f"[smoke d1] ce={losses['ce_cap'].item():.4f} mse_va={losses['mse_va'].item():.4f} "
        f"kl_cat34={losses['kl_cat34'].item():.4f} total={losses['total'].item():.4f}",
        flush=True,
    )
    proj_in = torch.randn(B, 256, cfg.d_vis)
    proj_out = model.projector(proj_in)
    print(f"[smoke d1] projector {tuple(proj_in.shape)} -> {tuple(proj_out.shape)}", flush=True)
    torch.save({"cfg": cfg.__dict__, "state": model.state_dict()}, out_dir / "smoke_ckpt.pt")


def main() -> None:
    args = parse_args()
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)

    if args.smoke:
        smoke_main(Path(args.out_dir))
        return

    raise NotImplementedError(
        "Full backbone load requires brainvlm_qwen_env + Qwen3VLForConditionalGeneration. "
        "Use --smoke until env is verified."
    )


if __name__ == "__main__":
    main()
