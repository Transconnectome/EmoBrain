#!/usr/bin/env python3
"""
EmoBrain NeuroSTORM embedding extraction (resting-pretrained or scratch).

- Input: 4D volume per stimulus, frame_*.pt files (74, 91, 81, 1) each
- Spatial pad: (74,91,81) → (96,96,96) with background value
- Temporal pad: T → 20 frames via {replicate, zero, mean}
- Output: per-subject .npz with embeddings (2185, 288) + padding_ratio metadata

Usage:
    python extract_neurostorm.py --init resting --padding replicate --subject sub-01
"""
import argparse
import sys
import os
from collections import OrderedDict
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

# Inject EmoDe's NeuroSTORM codebase
NEUROSTORM_REPO = "/pscratch/sd/s/sjmoon/EmoBrain/external/NeuroSTORM"
sys.path.insert(0, NEUROSTORM_REPO)
from models.neurostorm import NeuroSTORM

# Paths
EmoBrain_ROOT = Path("/pscratch/sd/s/sjmoon/EmoBrain")
VOL_BASE = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img")
CHECKPOINT = EmoBrain_ROOT / "baseline/neurostorm/pt_neurostorm_mae_ratio0.5.ckpt"
CANONICAL_CSV = EmoBrain_ROOT / "data/feelin_canonical_stimuli.csv"

# Constants
NUM_FRAMES = 20
EMBED_DIM = 36  # NeuroSTORM base config, final output dim = 288


class EmoBrainHorikawaNeuroSTORMDataset(Dataset):
    """NeuroSTORM 4D volume dataset with configurable padding."""

    def __init__(self, subject: str, padding: str = "replicate", canonical_csv: Path = CANONICAL_CSV):
        self.subject = subject
        self.padding = padding
        assert padding in {"replicate", "zero", "mean", "spatial_only", "cyclic_replicate"}
        canonical = pd.read_csv(canonical_csv)
        self.stim_names = canonical["stimulus_name"].tolist()
        self.stim_nums = canonical["stimulus_num"].tolist()

    def __len__(self):
        return len(self.stim_names)

    def _load_volume(self, stim_name: str):
        """Load all frame_*.pt files in stim dir → tensor (T, H, W, D, 1) then (1, H, W, D, T)."""
        stim_dir = VOL_BASE / f"{self.subject}_{stim_name}"
        frame_files = sorted(stim_dir.glob("frame_*.pt"))
        frames = []
        for f in frame_files:
            frame = torch.load(str(f), weights_only=False)
            if hasattr(frame, "as_tensor"):
                frame = frame.as_tensor()
            frames.append(frame)  # (74, 91, 81, 1)
        y = torch.stack(frames, dim=0)        # (T, 74, 91, 81, 1)
        # squeeze channel and rearrange to (1, 74, 91, 81, T)
        y = y.squeeze(-1).permute(1, 2, 3, 0)  # (74, 91, 81, T)
        return y.unsqueeze(0)                   # (1, 74, 91, 81, T)

    def _spatial_pad(self, y: torch.Tensor) -> torch.Tensor:
        """(1, 74, 91, 81, T) → (1, 96, 96, 96, T) with background fill."""
        bg = float(y.flatten()[0].item())
        # Rearrange for F.pad: pad last 3 dims (D, W, H since order reversed)
        # current shape (1, 74, 91, 81, T) → permute to (1, T, 74, 91, 81) for spatial pad
        T = y.shape[-1]
        y = y.permute(0, 4, 1, 2, 3).contiguous()   # (1, T, 74, 91, 81)
        # F.pad order: (z_l, z_r, y_l, y_r, x_l, x_r) for last 3 dims = (81→96, 91→96, 74→96)
        y = F.pad(y, (7, 8, 2, 3, 11, 11), value=bg)
        # Back to (1, 96, 96, 96, T)
        return y.permute(0, 2, 3, 4, 1).contiguous()

    def _temporal_pad(self, y: torch.Tensor, original_T: int) -> torch.Tensor:
        """(1, 96, 96, 96, T) → (1, 96, 96, 96, NUM_FRAMES) via padding mode."""
        if original_T > NUM_FRAMES:
            return y[..., :NUM_FRAMES].contiguous()
        if original_T == NUM_FRAMES:
            return y
        pad_len = NUM_FRAMES - original_T
        if self.padding == "replicate":
            last = y[..., -1:]                          # (1, 96, 96, 96, 1)
            pad = last.expand(*last.shape[:-1], pad_len)
            return torch.cat([y, pad], dim=-1)
        if self.padding == "zero":
            return F.pad(y, (0, pad_len), value=0.0)
        if self.padding == "mean":
            # proper mean padding: real T frames + (NUM_FRAMES - T) copies of their mean
            mean_frame = y.mean(dim=-1, keepdim=True)   # (1, 96, 96, 96, 1)
            pad = mean_frame.expand(*mean_frame.shape[:-1], pad_len)
            return torch.cat([y, pad], dim=-1)
        if self.padding == "spatial_only":
            # spatial-only control (all NUM_FRAMES = mean of original T, no temporal info)
            mean_frame = y.mean(dim=-1, keepdim=True)
            return mean_frame.expand(*mean_frame.shape[:-1], NUM_FRAMES).contiguous()
        if self.padding == "cyclic_replicate":
            # cyclic: T frames 를 반복해서 N 길이로
            reps = (NUM_FRAMES + original_T - 1) // original_T
            tiled = y.repeat(*([1] * (y.dim() - 1)), reps)
            return tiled[..., :NUM_FRAMES].contiguous()
        raise ValueError(self.padding)

    def __getitem__(self, idx):
        stim_name = self.stim_names[idx]
        stim_num = self.stim_nums[idx]
        try:
            y = self._load_volume(stim_name)              # (1, 74, 91, 81, T)
            original_T = y.shape[-1]
            y = self._spatial_pad(y)                       # (1, 96, 96, 96, T)
            y = self._temporal_pad(y, original_T)          # (1, 96, 96, 96, 20)
        except Exception as e:
            print(f"[WARN] {self.subject}/{stim_name}: {e}")
            y = torch.zeros(1, 96, 96, 96, NUM_FRAMES)
            original_T = 0
        return {
            "fmri": y.to(torch.float32),
            "stim_num": stim_num,
            "original_T": original_T,
            "padding_ratio": max(0.0, (NUM_FRAMES - original_T) / NUM_FRAMES),
        }


def collate(batch):
    return {
        "fmri": torch.stack([b["fmri"] for b in batch], dim=0),  # (B, 1, 96, 96, 96, 20)
        "stim_num": np.array([b["stim_num"] for b in batch]),
        "original_T": np.array([b["original_T"] for b in batch]),
        "padding_ratio": np.array([b["padding_ratio"] for b in batch], dtype=np.float32),
    }


def build_neurostorm(embed_dim=36):
    return NeuroSTORM(
        img_size=(96, 96, 96, NUM_FRAMES),
        in_chans=1,
        embed_dim=embed_dim,
        window_size=(4, 4, 4, 4),
        first_window_size=(4, 4, 4, 4),
        patch_size=(6, 6, 6, 1),
        depths=(2, 2, 6, 2),
        num_heads=(3, 6, 12, 24),
        c_multiplier=2,
        last_layer_full_MSA=True,
    )


def load_pretrained(model, ckpt_path: Path):
    ckpt = torch.load(str(ckpt_path), map_location="cpu", weights_only=False)
    state = ckpt.get("state_dict", ckpt)
    new_state = OrderedDict()
    for k, v in state.items():
        if k.startswith("model."):
            new_state[k[len("model."):]] = v
        elif not k.startswith("output_head"):
            new_state[k] = v
    missing, unexpected = model.load_state_dict(new_state, strict=False)
    print(f"  Loaded {len(new_state)} keys | missing={len(missing)} unexpected={len(unexpected)}")
    return model


def pool_features(x):
    """[B, C, sx, sy, sz, T] → mean over spatial+temporal → [B, C]."""
    B, C = x.shape[:2]
    return x.flatten(start_dim=2).mean(dim=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", choices=["resting", "scratch"], required=True)
    ap.add_argument("--padding",
                    choices=["replicate", "zero", "mean", "spatial_only", "cyclic_replicate"],
                    default="replicate",
                    help="replicate / zero / mean (proper) / spatial_only (control) / cyclic_replicate")
    ap.add_argument("--subject", default="sub-01")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--batch_size", type=int, default=8)
    ap.add_argument("--num_workers", type=int, default=2)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--out_root", default=str(EmoBrain_ROOT / "output/embeddings"))
    ap.add_argument("--limit_n", type=int, default=None, help="Limit to N stimuli (test run).")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device(args.device)
    out_dir = Path(args.out_root) / f"neurostorm_{args.init}_pad-{args.padding}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== EmoBrain NeuroSTORM extraction ===")
    print(f"  init     : {args.init}")
    print(f"  padding  : {args.padding}")
    print(f"  subject  : {args.subject}")
    print(f"  device   : {args.device}")
    print(f"  output   : {out_dir}")

    dataset = EmoBrainHorikawaNeuroSTORMDataset(args.subject, padding=args.padding)
    if args.limit_n:
        dataset.stim_names = dataset.stim_names[:args.limit_n]
        dataset.stim_nums = dataset.stim_nums[:args.limit_n]
        print(f"  [LIMIT] processing {args.limit_n} stimuli only")

    loader = DataLoader(
        dataset, batch_size=args.batch_size, shuffle=False,
        num_workers=args.num_workers, pin_memory=True, collate_fn=collate,
    )

    print(f"\n[Model] building NeuroSTORM (embed_dim={EMBED_DIM})")
    model = build_neurostorm(embed_dim=EMBED_DIM)
    if args.init == "resting":
        print(f"[Model] loading resting-pretrained: {CHECKPOINT}")
        model = load_pretrained(model, CHECKPOINT)
    else:
        print(f"[Model] scratch random init (seed={args.seed})")
    model.to(device).eval()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[Model] params: {n_params/1e6:.2f}M")

    embeddings, stim_nums, padding_ratios, original_Ts = [], [], [], []
    print(f"\n[Extract] {len(dataset)} stimuli, batch_size={args.batch_size}")
    with torch.no_grad():
        for i, batch in enumerate(loader):
            fmri = batch["fmri"].to(device, non_blocking=True)
            features = model(fmri)               # [B, C, sx, sy, sz, T]
            emb = pool_features(features)        # [B, C]
            embeddings.append(emb.cpu().numpy().astype(np.float32))
            stim_nums.append(batch["stim_num"])
            padding_ratios.append(batch["padding_ratio"])
            original_Ts.append(batch["original_T"])
            if (i + 1) % 10 == 0 or i == len(loader) - 1:
                done = min((i + 1) * args.batch_size, len(dataset))
                print(f"  batch {i+1}/{len(loader)}  ~{done}/{len(dataset)}")

    embeddings = np.concatenate(embeddings, axis=0)
    stim_nums = np.concatenate(stim_nums)
    padding_ratios = np.concatenate(padding_ratios)
    original_Ts = np.concatenate(original_Ts)

    out_path = out_dir / f"{args.subject}.pt"
    payload = {
        "embeddings": torch.from_numpy(embeddings),
        "stim_num": torch.from_numpy(stim_nums),
        "padding_ratio": torch.from_numpy(padding_ratios),
        "original_T": torch.from_numpy(original_Ts),
        "init": args.init,
        "padding": args.padding,
        "seed": args.seed,
        "model": "neurostorm_mae_ratio0.5",
        "num_frames": NUM_FRAMES,
        "save_layers": "final",
    }
    torch.save(payload, out_path)
    print(f"\n[Saved] {out_path}")
    print(f"  embeddings shape : {embeddings.shape}")
    print(f"  padding_ratio    : min={padding_ratios.min():.3f} max={padding_ratios.max():.3f} mean={padding_ratios.mean():.3f}")
    print(f"  any NaN          : {np.isnan(embeddings).any()}")
    print(f"  embedding stats  : min={embeddings.min():.3f} max={embeddings.max():.3f} mean={embeddings.mean():.3f}")


if __name__ == "__main__":
    main()
