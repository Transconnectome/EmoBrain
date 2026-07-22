#!/usr/bin/env python3
"""
EmoBrain Brain-JEPA embedding extraction (resting-pretrained or scratch)

- Input: ROI time series (Schaefer 400 + Tian S3 50 = 450 ROIs), variable T
- Padding: replicate last frame to 20 frames (T<20), first 20 frames (T>20)
- Output: per-subject .npz with embeddings (2185, 768) + padding_ratio metadata

Usage:
    python extract_brain_jepa.py --init resting --subject sub-01
    python extract_brain_jepa.py --init scratch --subject sub-01 --seed 0
"""
import argparse
import sys
import os
from pathlib import Path
import gzip
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

# Inject EmoDe's Brain-JEPA codebase
BRAIN_JEPA_REPO = "/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA"
sys.path.insert(0, BRAIN_JEPA_REPO)
from downstream_tasks.models_vit_embedding_extraction import VisionTransformer

# Paths
EmoBrain_ROOT = Path("/pscratch/sd/s/sjmoon/EmoBrain")
ROI_BASE = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/time_series")
NORM_PARAMS = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/normalization_params.npz")
CHECKPOINT = EmoBrain_ROOT / "external/checkpoints/brain_jepa/jepa-ep300.pth"
CANONICAL_CSV = EmoBrain_ROOT / "data/feelin_canonical_stimuli.csv"

# Constants
N_ROIS = 450
NUM_FRAMES = 16  # BJ patch_size=16, NUM_FRAMES=16 정확히 1 time patch.
                 # T >= 16 자극은 center-crop (앞/뒤 trim) → middle 16 TR 사용,
                 # initial hemodynamic transient 회피.
                 # T < 16 자극은 padding 필요 (mean default).


class EmoBrainHorikawaJEPADataset(Dataset):
    """Brain-JEPA ROI dataset with configurable padding (replicate / zero / mean)."""

    def __init__(self, subject: str, padding: str = "replicate", canonical_csv: Path = CANONICAL_CSV):
        self.subject = subject
        self.padding = padding
        assert padding in {"replicate", "zero", "mean", "spatial_only", "cyclic_replicate"}, f"unknown padding {padding}"
        self.sub_dir = ROI_BASE / subject
        canonical = pd.read_csv(canonical_csv)
        self.stim_names = canonical["stimulus_name"].tolist()
        self.stim_nums = canonical["stimulus_num"].tolist()

        # Load normalization parameters (per-ROI medians / IQRs)
        if NORM_PARAMS.exists():
            npz = np.load(NORM_PARAMS)
            self.medians = npz["medians"].astype(np.float32)  # (450,)
            self.iqrs = npz["iqrs"].astype(np.float32)        # (450,)
            assert self.medians.shape[0] == N_ROIS
        else:
            self.medians = np.zeros(N_ROIS, dtype=np.float32)
            self.iqrs = np.ones(N_ROIS, dtype=np.float32)

    def __len__(self):
        return len(self.stim_names)

    def _load_concat(self, stim_name: str) -> np.ndarray:
        """Load cortical + subcortical CSVs, concat to (450, T)."""
        stim_dir = self.sub_dir / stim_name
        df_c = pd.read_csv(stim_dir / "fMRI.Schaefer17n400p.csv.gz")
        df_s = pd.read_csv(stim_dir / "fMRI.Tian_Subcortex_S3_3T.csv.gz")
        t_cols_c = [c for c in df_c.columns if c.startswith("T")]
        t_cols_s = [c for c in df_s.columns if c.startswith("T")]
        # take min in case lengths differ
        T = min(len(t_cols_c), len(t_cols_s))
        cortex = df_c[t_cols_c[:T]].values.astype(np.float32)      # (400, T)
        subcort = df_s[t_cols_s[:T]].values.astype(np.float32)     # (50,  T)
        return np.concatenate([cortex, subcort], axis=0)            # (450, T)

    def _pad_or_crop(self, ts: np.ndarray, mode: str = "replicate") -> tuple[np.ndarray, int]:
        """Padding / cropping for Brain-JEPA.

        T >= NUM_FRAMES (16): center-crop to middle NUM_FRAMES TR,
            dropping (T-NUM_FRAMES)//2 from start and remainder from end.
            예: T=20 → drop 2 head + 2 tail, keep TR 2..17.
        T < NUM_FRAMES: pad to NUM_FRAMES using `mode`.
        """
        original_T = ts.shape[1]
        if original_T >= NUM_FRAMES:
            start = (original_T - NUM_FRAMES) // 2
            return ts[:, start:start + NUM_FRAMES].astype(np.float32), original_T
        # T < NUM_FRAMES, need to pad
        pad_len = NUM_FRAMES - original_T
        if mode == "replicate":
            # Repeat last frame
            pad = np.repeat(ts[:, -1:], pad_len, axis=1)
            ts = np.concatenate([ts, pad], axis=1)
        elif mode == "zero":
            # Zero pad after
            pad = np.zeros((ts.shape[0], pad_len), dtype=ts.dtype)
            ts = np.concatenate([ts, pad], axis=1)
        elif mode == "mean":
            # proper mean padding: real T frames + (NUM_FRAMES - T) copies of their mean
            mean_frame = ts.mean(axis=1, keepdims=True)  # (n_rois, 1)
            pad = np.repeat(mean_frame, pad_len, axis=1)
            ts = np.concatenate([ts, pad], axis=1)
        elif mode == "spatial_only":
            # spatial-only control (all NUM_FRAMES = mean of original T, no temporal info)
            mean_frame = ts.mean(axis=1, keepdims=True)
            ts = np.repeat(mean_frame, NUM_FRAMES, axis=1)
        elif mode == "cyclic_replicate":
            # cyclic: T frames 를 반복해서 N 길이로
            reps = (NUM_FRAMES + original_T - 1) // original_T
            ts = np.tile(ts, (1, reps))[:, :NUM_FRAMES]
        else:
            raise ValueError(f"Unknown padding mode: {mode}")
        return ts.astype(np.float32), original_T

    def _normalize(self, ts: np.ndarray) -> np.ndarray:
        """Robust scaling per ROI (median / IQR)."""
        return ((ts - self.medians[:, None]) / (self.iqrs[:, None] + 1e-8)).astype(np.float32)

    def __getitem__(self, idx):
        stim_name = self.stim_names[idx]
        stim_num = self.stim_nums[idx]
        try:
            ts = self._load_concat(stim_name)
        except Exception as e:
            print(f"[WARN] {self.subject}/{stim_name}: {e}")
            ts = np.zeros((N_ROIS, NUM_FRAMES), dtype=np.float32)
            original_T = 0
        else:
            ts, original_T = self._pad_or_crop(ts, mode=self.padding)
        ts = self._normalize(ts)
        # Model expects (1, 1, n_rois, num_frames)
        fmri = torch.from_numpy(ts).unsqueeze(0).unsqueeze(0)
        return {
            "fmri": fmri,
            "stim_num": stim_num,
            "original_T": original_T,
            "padding_ratio": max(0.0, (NUM_FRAMES - original_T) / NUM_FRAMES),
        }


def collate(batch):
    return {
        "fmri": torch.cat([b["fmri"] for b in batch], dim=0),
        "stim_num": np.array([b["stim_num"] for b in batch]),
        "original_T": np.array([b["original_T"] for b in batch]),
        "padding_ratio": np.array([b["padding_ratio"] for b in batch], dtype=np.float32),
    }


class _Args:
    """Mimic argparse object that VisionTransformer expects."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def build_model(device, attn_mode="normal"):
    args = _Args(
        model_name="vit_base",
        attn_mode=attn_mode,
        nb_classes=2,
        global_pool=True,
        add_w="mapping",
        crop_size=(N_ROIS, NUM_FRAMES),
        patch_size=16,
        pred_depth=12,
        pred_emb_dim=384,
        use_normalization=True,
        gradient_checkpointing=False,
    )
    model = VisionTransformer(
        args,
        model_name=args.model_name,
        attn_mode=args.attn_mode,
        num_classes=args.nb_classes,
        global_pool=args.global_pool,
        device=device,
        add_w=args.add_w,
    )
    return model


def load_pretrained(model, ckpt_path: Path):
    ckpt = torch.load(str(ckpt_path), map_location="cpu")
    encoder_state = ckpt["encoder"]
    state_dict = model.state_dict()
    new_state = {k.replace("module.", "encoder."): v for k, v in encoder_state.items()}

    # Temporal position code (emb_h / emb_w) is a NON-LEARNED fixed sinusoidal
    # buffer (requires_grad=False), regenerated by the model from its grid_size at
    # construction. Our model is built with 1 time patch, so it already holds the
    # correct sin/cos for a one-patch grid. We must NOT overwrite it with the
    # checkpoint's 10-patch values: the previous code averaged them, which is an
    # off-manifold blur of a non-learned buffer (short-window transfer, decision
    # 2026-07-21 (4)). Drop these keys so the model keeps its own regenerated code.
    # The LEARNED spatial gradient positioning (predictor_pos_embed_proj) is not a
    # sincos buffer and loads normally below; it carries the transferable spatial
    # network organization.
    for key in ("encoder.pos_embed_proj.emb_h", "encoder.pos_embed_proj.emb_w"):
        if new_state.pop(key, None) is not None:
            print(f"  [pos_embed] skip {key} (non-learned sin/cos; model regenerates for its 1-patch grid)")

    # Handle patch_embed kernel mismatch
    key = "encoder.patch_embed.proj.weight"
    if key in new_state:
        ckpt_w = new_state[key]
        model_w = state_dict[key]
        if ckpt_w.shape != model_w.shape:
            import torch.nn.functional as F
            squeezed = ckpt_w.squeeze(1).squeeze(1)  # (768, p)
            interp = F.interpolate(squeezed.unsqueeze(0), size=model_w.shape[-1], mode="linear", align_corners=False).squeeze(0)
            new_state[key] = interp.unsqueeze(1).unsqueeze(1)
            print(f"  [patch_embed] interpolated {ckpt_w.shape[-1]} → {model_w.shape[-1]}")

    msg = model.load_state_dict(new_state, strict=False)
    print(f"  Missing keys: {len(msg.missing_keys)}, Unexpected keys: {len(msg.unexpected_keys)}")
    return model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", choices=["resting", "scratch"], required=True)
    ap.add_argument("--padding",
                    choices=["replicate", "zero", "mean", "spatial_only", "cyclic_replicate"],
                    default="replicate",
                    help="replicate / zero / mean (proper) / spatial_only (control) / cyclic_replicate")
    ap.add_argument("--subject", default="sub-01")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--batch_size", type=int, default=32)
    ap.add_argument("--num_workers", type=int, default=4)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--attn_mode", default="normal", choices=["normal", "flash_attn"])
    ap.add_argument("--out_root", default=str(EmoBrain_ROOT / "project/shared/output/embeddings"))
    ap.add_argument("--out_tag", default="",
                    help="suffix on the variant dir so re-extraction never overwrites "
                         "existing embeddings (e.g. _posfix for the emb_h-skip fix).")
    ap.add_argument("--smoke_test_n", type=int, default=None, help="If set, only process N stimuli for smoke test.")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device(args.device)
    out_dir = Path(args.out_root) / f"brain_jepa_{args.init}_pad-{args.padding}{args.out_tag}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== EmoBrain Brain-JEPA extraction ===")
    print(f"  init     : {args.init}")
    print(f"  padding  : {args.padding}")
    print(f"  subject  : {args.subject}")
    print(f"  device   : {args.device}")
    print(f"  output   : {out_dir}")
    print(f"  seed     : {args.seed}")

    # Dataset / Loader
    dataset = EmoBrainHorikawaJEPADataset(args.subject, padding=args.padding)
    if args.smoke_test_n:
        dataset.stim_names = dataset.stim_names[:args.smoke_test_n]
        dataset.stim_nums = dataset.stim_nums[:args.smoke_test_n]
        print(f"  [SMOKE] limited to {args.smoke_test_n} stimuli")

    loader = DataLoader(
        dataset, batch_size=args.batch_size, shuffle=False,
        num_workers=args.num_workers, pin_memory=True, collate_fn=collate,
    )

    # Model
    print(f"\n[Model] building Brain-JEPA ViT-Base ...")
    model = build_model(device, attn_mode=args.attn_mode)
    if args.init == "resting":
        print(f"[Model] loading resting-pretrained checkpoint: {CHECKPOINT}")
        model = load_pretrained(model, CHECKPOINT)
    else:
        print(f"[Model] scratch init (random weights, seed={args.seed})")

    model.head = torch.nn.Identity()
    model.to(device).eval()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[Model] params: {n_params/1e6:.2f}M")

    # Extract
    embeddings, stim_nums, padding_ratios, original_Ts = [], [], [], []
    print(f"\n[Extract] {len(dataset)} stimuli, batch_size={args.batch_size}")
    with torch.no_grad():
        for i, batch in enumerate(loader):
            fmri = batch["fmri"].to(device, non_blocking=True)
            emb = model(fmri)  # (B, 768)
            if isinstance(emb, tuple):
                emb = emb[0]
            embeddings.append(emb.cpu().numpy().astype(np.float32))
            stim_nums.append(batch["stim_num"])
            padding_ratios.append(batch["padding_ratio"])
            original_Ts.append(batch["original_T"])
            if (i + 1) % 10 == 0 or i == len(loader) - 1:
                done = (i + 1) * args.batch_size
                print(f"  batch {i+1}/{len(loader)}  ~{min(done, len(dataset))}/{len(dataset)}")

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
        "model": "brain_jepa_vit_base",
        "n_rois": N_ROIS,
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
