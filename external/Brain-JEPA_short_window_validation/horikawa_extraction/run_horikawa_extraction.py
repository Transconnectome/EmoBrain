#!/usr/bin/env python3
"""Extract one audited Brain-JEPA Horikawa embedding condition."""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.brain_jepa_adapter import create_encoder, embed_batches
from lib.horikawa_data import HorikawaShortWindowDataset, collate


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject", choices=[f"sub-{index:02d}" for index in range(1, 6)], required=True)
    parser.add_argument("--init", choices=["pretrained", "scratch"], required=True)
    parser.add_argument(
        "--position-policy",
        choices=["native", "temporal_mean", "temporal_center"],
        default="native",
    )
    parser.add_argument(
        "--perturbation",
        choices=["mean", "zero", "spatial_only", "time_shuffle"],
        default="mean",
    )
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    return parser.parse_args()


def main():
    args = parse_args()
    device = torch.device(args.device)
    dataset = HorikawaShortWindowDataset(
        subject=args.subject, perturbation=args.perturbation, seed=args.seed
    )
    if args.limit is not None:
        dataset.stim_names = dataset.stim_names[: args.limit]
        dataset.stim_nums = dataset.stim_nums[: args.limit]
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=device.type == "cuda",
        collate_fn=collate,
    )
    model, audit = create_encoder(
        init=args.init,
        num_frames=16,
        position_policy=args.position_policy,
        device=device,
        seed=args.seed,
    )
    embeddings, arrays = embed_batches(model, loader, device)

    condition = (
        f"init-{args.init}_pos-{args.position_policy}_input-{args.perturbation}"
    )
    output_root = ROOT / "outputs/horikawa_embeddings"
    if args.limit is not None:
        output_root = ROOT / "outputs/smoke/horikawa_embeddings"
    output_dir = output_root / condition
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = output_dir / args.subject
    np.savez_compressed(stem.with_suffix(".npz"), embeddings=embeddings, **arrays)
    metadata = {
        "subject": args.subject,
        "condition": condition,
        "initialization": args.init,
        "position_policy": args.position_policy,
        "input_perturbation": args.perturbation,
        "seed": args.seed,
        "n_stimuli": int(len(embeddings)),
        "embedding_shape": list(embeddings.shape),
        "mean_padding_ratio": float(arrays["padding_ratio"].mean()),
        "audit": audit,
    }
    with open(stem.with_suffix(".json"), "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
    print(f"Saved: {stem.with_suffix('.npz')}")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
