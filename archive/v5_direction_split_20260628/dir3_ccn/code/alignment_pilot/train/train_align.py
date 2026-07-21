"""Direction 2 alignment pilot trainer.

Loads frozen brain + V-JEPA2 embeddings, trains projection heads with
SigLIP + GRL adversarial loss, saves projected z_brain / z_video and the
projection weights. Single-GPU, fp32. CPU also works (small model).

Usage:
  python train_align.py --brain_variant resting --fold 1 --out_dir <path>
  python train_align.py --brain_variant scratch --fold 1 --out_dir <path>
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

# Allow `python train_align.py ...` from anywhere by making the dir2 code root importable.
CODE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_ROOT))

from data.dataset import BrainVideoDataset
from loss.grl import adversarial_loss
from loss.siglip import SigLIPLoss
from model.discriminator import ModalityDiscriminator
from model.projection import ProjBrain, ProjVideo


def set_seed(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed)


def evaluate(
    proj_brain: ProjBrain,
    proj_video: ProjVideo,
    siglip: SigLIPLoss,
    loader: DataLoader,
    device: torch.device,
) -> dict[str, float]:
    proj_brain.eval(); proj_video.eval(); siglip.eval()
    total_loss = 0.0
    n_batches = 0
    diag_minus_offdiag = 0.0
    with torch.no_grad():
        for batch in loader:
            brain = batch["brain"].to(device, non_blocking=True)
            video = batch["video"].to(device, non_blocking=True)
            z_b = proj_brain(brain)
            z_v = proj_video(video)
            loss = siglip(z_b, z_v)
            total_loss += loss.item()
            n_batches += 1
            # Diagonal sharpening proxy.
            zb_n = F.normalize(z_b, dim=-1)
            zv_n = F.normalize(z_v, dim=-1)
            sim = zb_n @ zv_n.t()
            diag = sim.diagonal().mean().item()
            mask = ~torch.eye(sim.size(0), dtype=torch.bool, device=device)
            offdiag = sim[mask].mean().item()
            diag_minus_offdiag += diag - offdiag
    return {
        "val_siglip_loss": total_loss / max(n_batches, 1),
        "val_diag_minus_offdiag": diag_minus_offdiag / max(n_batches, 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brain_variant", choices=["resting", "scratch"], required=True)
    ap.add_argument("--fold", type=int, default=1)
    ap.add_argument("--out_dir", required=True, type=str)
    ap.add_argument("--epoch", type=int, default=40)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--weight_decay", type=float, default=1e-4)
    ap.add_argument("--lambda_adv", type=float, default=0.1)
    ap.add_argument("--adv_warmup_epoch", type=int, default=5,
                    help="lambda_adv = 0 for first N epochs, then linear warmup to --lambda_adv.")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--smoke", action="store_true",
                    help="10 stim, 1 epoch, CPU OK. For local sanity test.")
    args = ap.parse_args()

    set_seed(args.seed)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "config.json").write_text(json.dumps(vars(args), indent=2))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device}, brain_variant={args.brain_variant}, fold={args.fold}", flush=True)

    train_ds = BrainVideoDataset(brain_variant=args.brain_variant, split="train", test_fold=args.fold)
    val_ds = BrainVideoDataset(brain_variant=args.brain_variant, split="val", test_fold=args.fold)
    print(f"train n={len(train_ds)}, val n={len(val_ds)}", flush=True)

    if args.smoke:
        # Restrict to ~10 stim by clipping the sample list.
        train_ds.samples = train_ds.samples[:50]
        val_ds.samples = val_ds.samples[:50]
        args.epoch = 1
        args.batch = 16
        print("SMOKE mode: 50 samples, 1 epoch, batch 16", flush=True)

    train_loader = DataLoader(train_ds, batch_size=args.batch, shuffle=True, num_workers=2, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch, shuffle=False, num_workers=2)

    proj_brain = ProjBrain().to(device)
    proj_video = ProjVideo().to(device)
    siglip = SigLIPLoss().to(device)
    discriminator = ModalityDiscriminator().to(device)

    params = list(proj_brain.parameters()) + list(proj_video.parameters()) + list(siglip.parameters()) + list(discriminator.parameters())
    optimizer = torch.optim.AdamW(params, lr=args.lr, weight_decay=args.weight_decay)
    n_params = sum(p.numel() for p in params)
    print(f"trainable params: {n_params/1e6:.2f}M", flush=True)

    best_val_loss = math.inf
    best_state = None
    stale = 0
    history = []
    for epoch in range(args.epoch):
        proj_brain.train(); proj_video.train(); siglip.train(); discriminator.train()
        if epoch < args.adv_warmup_epoch:
            lam = 0.0
        else:
            ramp = min(1.0, (epoch - args.adv_warmup_epoch + 1) / max(args.adv_warmup_epoch, 1))
            lam = args.lambda_adv * ramp
        running_siglip, running_adv, n = 0.0, 0.0, 0
        for batch in train_loader:
            brain = batch["brain"].to(device, non_blocking=True)
            video = batch["video"].to(device, non_blocking=True)
            z_b = proj_brain(brain)
            z_v = proj_video(video)
            loss_sig = siglip(z_b, z_v)
            if lam > 0:
                loss_adv = adversarial_loss(z_b, z_v, discriminator, lam)
                loss = loss_sig + loss_adv
            else:
                loss_adv = torch.tensor(0.0, device=device)
                loss = loss_sig
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params, max_norm=1.0)
            optimizer.step()
            running_siglip += loss_sig.item()
            running_adv += loss_adv.item()
            n += 1
        train_siglip = running_siglip / max(n, 1)
        train_adv = running_adv / max(n, 1)
        metrics = evaluate(proj_brain, proj_video, siglip, val_loader, device)
        row = {
            "epoch": epoch,
            "lambda_adv": lam,
            "train_siglip": train_siglip,
            "train_adv": train_adv,
            **metrics,
            "log_t": siglip.log_t.item(),
            "b": siglip.b.item(),
        }
        history.append(row)
        print(json.dumps(row), flush=True)

        if metrics["val_siglip_loss"] < best_val_loss:
            best_val_loss = metrics["val_siglip_loss"]
            best_state = {
                "proj_brain": proj_brain.state_dict(),
                "proj_video": proj_video.state_dict(),
                "siglip": siglip.state_dict(),
                "discriminator": discriminator.state_dict(),
            }
            stale = 0
        else:
            stale += 1
            if stale >= args.patience and not args.smoke:
                print(f"early stop at epoch {epoch}", flush=True)
                break

    # Save the best checkpoint and the per-epoch history.
    if best_state is not None:
        torch.save(best_state, out_dir / "best.pt")
    (out_dir / "history.json").write_text(json.dumps(history, indent=2))
    print(f"DONE. best val_siglip_loss={best_val_loss:.4f}", flush=True)


if __name__ == "__main__":
    main()
