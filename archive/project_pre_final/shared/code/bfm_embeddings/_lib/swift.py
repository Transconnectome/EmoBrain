#!/usr/bin/env python3
"""
EmoBrain SwiFT_v2 embedding extraction.

Supports 7 lab pretrained models (and scratch init for each):
  - UAH_P1_5M   (ver9, embed_dim=36,  patch [6,6,6,2])  ~5M
  - UAH_P2_51M  (ver9, embed_dim=96,  patch [6,6,6,2])  ~51M
  - UAH_P3_202M (ver9, embed_dim=192, patch [6,6,6,2])  ~202M
  - UAH_P3_806M (ver9, embed_dim=384, patch [6,6,6,2])  ~806M (excluded from grid by user)
  - NewUAH_newE36  (ver11, embed_dim=36,  patch [6,6,6,1])  ~9M
  - NewUAH_newE96  (ver11, embed_dim=96,  patch [6,6,6,1])  ~66M
  - NewUAH_newE192 (ver11, embed_dim=192, patch [6,6,6,1])  ~264M

Input: Horikawa 4D volumes (74,91,81,T) → spatial pad to 96^3 → temporal pad to 20
Padding modes: replicate / zero / mean
Output: per-subject .npz with embeddings (2185, D) + padding_ratio metadata
"""
import argparse
import sys
from collections import OrderedDict
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

SWIFT_REPO = "/pscratch/sd/s/sjmoon/SwiFT_v2"
sys.path.insert(0, SWIFT_REPO)

EmoBrain_ROOT = Path("/pscratch/sd/s/sjmoon/EmoBrain")
VOL_BASE = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img")
CANONICAL_CSV = EmoBrain_ROOT / "data/feelin_canonical_stimuli.csv"
NUM_FRAMES = 20

# ============================================================
# Model configs per SwiFT variant
# ============================================================
# All use depths=[2,2,18,2], num_heads=[6,12,24,48], c_multiplier=2, last_layer_full_MSA=True,
# SL=20, window=(4,4,4,window_t)
MODEL_CONFIGS = {
    "UAH_P1_5M": dict(
        version="ver9",
        ckpt="/pscratch/sd/j/jubchoi/Newdata_Phase3_MR0p6/UAH_P1_5M_MR_0p6_L1e-3/best.pt",
        embed_dim=36,
        patch_size=(6, 6, 6, 2),
        window_size=(4, 4, 4, 4),         # lab reference: 4 (not 20)
        first_window_size=(4, 4, 4, 4),
    ),
    "UAH_P2_51M": dict(
        version="ver9",
        ckpt="/pscratch/sd/j/jubchoi/Newdata_Phase3_MR0p6/UAH_P2_51M_MR_0p6_L1e-4/best.pt",
        embed_dim=96,
        patch_size=(6, 6, 6, 2),
        window_size=(4, 4, 4, 4),         # lab reference (NEW_extract_embeddings_ver9_GARD_UAH.sh:70)
        first_window_size=(4, 4, 4, 4),
    ),
    "UAH_P3_202M": dict(
        version="ver9",
        ckpt="/pscratch/sd/j/jubchoi/Newdata_Phase3_MR0p6/UAH_P3_202M_MR_0p6_L1e-4/best.pt",
        embed_dim=192,
        patch_size=(6, 6, 6, 2),
        window_size=(4, 4, 4, 4),
        first_window_size=(4, 4, 4, 4),
    ),
    "UAH_P3_806M": dict(
        version="ver9",
        ckpt="/pscratch/sd/j/jubchoi/Newdata_Phase3_MR0p6/UAH_P3_806M_MR_0p6_L2e-4/best.pt",
        embed_dim=384,
        patch_size=(6, 6, 6, 2),
        window_size=(4, 4, 4, 20),
        first_window_size=(4, 4, 4, 4),
    ),
    "NewUAH_newE36": dict(
        version="ver11",
        ckpt="/pscratch/sd/j/jubchoi/260225_newmodel/NewUAH_newE36_TP1_SL20_MR_0p8_L1e-4/best.pt",
        embed_dim=36,
        patch_size=(6, 6, 6, 1),
        window_size=(4, 4, 4, 10),       # SL/2 = 10
        first_window_size=(4, 4, 4, 10),
    ),
    "NewUAH_newE96": dict(
        version="ver11",
        ckpt="/pscratch/sd/j/jubchoi/260225_newmodel/NewUAH_newE96_TP1_SL20_MR_0p8_L1e-4/best.pt",
        embed_dim=96,
        patch_size=(6, 6, 6, 1),
        window_size=(4, 4, 4, 10),
        first_window_size=(4, 4, 4, 10),
    ),
    "NewUAH_newE192": dict(
        version="ver11",
        ckpt="/pscratch/sd/j/jubchoi/260225_newmodel/NewUAH_newE192_TP1_SL20_MR_0p8_L1e-4/best.pt",
        embed_dim=192,
        patch_size=(6, 6, 6, 1),
        window_size=(4, 4, 4, 10),
        first_window_size=(4, 4, 4, 10),
    ),
}

COMMON = dict(
    depths=(2, 2, 18, 2),
    num_heads=(6, 12, 24, 48),
    c_multiplier=2,
)


# ============================================================
# Dataset (same shape as NeuroSTORM, configurable padding)
# ============================================================
class EmoBrainHorikawaSwiFTDataset(Dataset):
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
        stim_dir = VOL_BASE / f"{self.subject}_{stim_name}"
        frame_files = sorted(stim_dir.glob("frame_*.pt"))
        frames = []
        for f in frame_files:
            frame = torch.load(str(f), weights_only=False)
            if hasattr(frame, "as_tensor"):
                frame = frame.as_tensor()
            frames.append(frame)
        y = torch.stack(frames, dim=0)                       # (T, 74, 91, 81, 1)
        y = y.squeeze(-1).permute(1, 2, 3, 0)                # (74, 91, 81, T)
        return y.unsqueeze(0)                                # (1, 74, 91, 81, T)

    def _spatial_pad(self, y: torch.Tensor) -> torch.Tensor:
        bg = float(y.flatten()[0].item())
        T = y.shape[-1]
        y = y.permute(0, 4, 1, 2, 3).contiguous()   # (1, T, 74, 91, 81)
        y = F.pad(y, (7, 8, 2, 3, 11, 11), value=bg)
        return y.permute(0, 2, 3, 4, 1).contiguous()  # (1, 96, 96, 96, T)

    def _temporal_pad(self, y: torch.Tensor, T: int) -> torch.Tensor:
        if T > NUM_FRAMES:
            return y[..., :NUM_FRAMES].contiguous()
        if T == NUM_FRAMES:
            return y
        pad_len = NUM_FRAMES - T
        if self.padding == "replicate":
            last = y[..., -1:]
            pad = last.expand(*last.shape[:-1], pad_len)
            return torch.cat([y, pad], dim=-1)
        if self.padding == "zero":
            return F.pad(y, (0, pad_len), value=0.0)
        if self.padding == "mean":
            # proper mean padding: real T frames + (NUM_FRAMES - T) copies of their mean
            mean_frame = y.mean(dim=-1, keepdim=True)
            pad = mean_frame.expand(*mean_frame.shape[:-1], pad_len)
            return torch.cat([y, pad], dim=-1)
        if self.padding == "spatial_only":
            # spatial-only control (all NUM_FRAMES = mean of original T, no temporal info)
            mean_frame = y.mean(dim=-1, keepdim=True)
            return mean_frame.expand(*mean_frame.shape[:-1], NUM_FRAMES).contiguous()
        if self.padding == "cyclic_replicate":
            # cyclic: T frames 를 반복해서 N 길이로. e.g. T=5 -> [f0..f4, f0..f4, ...] cut at N
            reps = (NUM_FRAMES + T - 1) // T  # ceil
            # y shape: (..., T). repeat 만 마지막 axis 에.
            shape = list(y.shape)
            shape[-1] = -1  # placeholder
            rep_dims = [1] * (y.dim() - 1) + [reps]
            tiled = y.repeat(*rep_dims)
            return tiled[..., :NUM_FRAMES].contiguous()
        raise ValueError(self.padding)

    def __getitem__(self, idx):
        stim_name = self.stim_names[idx]
        stim_num = self.stim_nums[idx]
        try:
            y = self._load_volume(stim_name)
            T = y.shape[-1]
            y = self._spatial_pad(y)
            y = self._temporal_pad(y, T)
        except Exception as e:
            print(f"[WARN] {self.subject}/{stim_name}: {e}")
            y = torch.zeros(1, 96, 96, 96, NUM_FRAMES)
            T = 0
        return {
            "fmri": y.to(torch.float32),
            "stim_num": stim_num,
            "original_T": T,
            "padding_ratio": max(0.0, (NUM_FRAMES - T) / NUM_FRAMES),
        }


def collate(batch):
    return {
        "fmri": torch.stack([b["fmri"] for b in batch], dim=0),
        "stim_num": np.array([b["stim_num"] for b in batch]),
        "original_T": np.array([b["original_T"] for b in batch]),
        "padding_ratio": np.array([b["padding_ratio"] for b in batch], dtype=np.float32),
    }


# ============================================================
# Model builder (dispatch by version)
# ============================================================
def build_model(model_name: str):
    cfg = MODEL_CONFIGS[model_name]
    version = cfg["version"]
    common_kwargs = dict(
        img_size=(96, 96, 96, NUM_FRAMES),
        in_chans=1,
        embed_dim=cfg["embed_dim"],
        window_size=cfg["window_size"],
        patch_size=cfg["patch_size"],
        depths=COMMON["depths"],
        num_heads=COMMON["num_heads"],
        c_multiplier=COMMON["c_multiplier"],
        last_layer_full_MSA=True,
    )
    if version == "ver11":
        from project.module.models.simmim_swin4d_transformer_ver11 import Simmim_RoPE4DSwinTransformer as ModelCls
        model = ModelCls(**common_kwargs, use_MuTransfer=True)
    elif version == "ver9":
        from project.module.models.simmim_swin4d_transformer_ver9 import SimmimSwinTransformer4D as ModelCls
        # ver9 requires first_window_size as separate arg, no use_MuTransfer
        model = ModelCls(
            **common_kwargs,
            first_window_size=cfg["first_window_size"],
        )
    else:
        raise ValueError(version)
    return model, cfg


def load_pretrained(model, ckpt_path: str):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    state = ckpt.get("state_dict", ckpt.get("model", ckpt))
    new_state = OrderedDict()
    # Strip lab prefixes in order: _forward_module., module., model.
    prefixes = ["_forward_module.", "module.", "model."]
    for k, v in state.items():
        nk = k
        # Strip prefixes (possibly stacked, e.g. "_forward_module.model.")
        changed = True
        while changed:
            changed = False
            for p in prefixes:
                if nk.startswith(p):
                    nk = nk[len(p):]
                    changed = True
                    break
        if nk.startswith("output_head") or nk.startswith("decoder"):
            continue
        new_state[nk] = v
    missing, unexpected = model.load_state_dict(new_state, strict=False)
    print(f"  Loaded {len(new_state)} keys | missing={len(missing)} unexpected={len(unexpected)}")
    if missing[:5]:
        print(f"  Sample missing: {missing[:5]}")
    if unexpected[:5]:
        print(f"  Sample unexpected: {unexpected[:5]}")
    return model


def forward_embedding(model, fmri, return_all=False):
    """Extract embedding via model._forward_hook_embedding.

    Input fmri shape : (B, C=1, D=96, H=96, W=96, T=20)  ← ST order (model outer contract)
    Returns:
      return_all=False -> final layer feature tensor (B, C_final, D', H', W', T')
      return_all=True  -> dict {layer_0, layer_1, ..., layer_{N-1}} of raw stage outputs
    """
    layer_dict = model._forward_hook_embedding(fmri)
    if return_all:
        return layer_dict
    final_key = f"layer_{model.num_layers - 1}"
    return layer_dict[final_key]


def pool_features(x):
    """Output shape can be:
       - (B, L, C): mean over L → (B, C)
       - (B, C, D, H, W, T): flatten spatial-temporal, mean → (B, C)
    """
    if x.ndim == 3:
        return x.mean(dim=1)
    if x.ndim >= 4:
        B, C = x.shape[:2]
        return x.flatten(start_dim=2).mean(dim=2)
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_name", choices=list(MODEL_CONFIGS.keys()), required=True,
                    help="Internal config key in MODEL_CONFIGS (e.g. NewUAH_newE96, UAH_P2_51M)")
    ap.add_argument("--output_tag", required=True,
                    help="Output folder tag (e.g. NewE96_SL20). Output: swift_{output_tag}_{init}_pad-{padding}/")
    ap.add_argument("--init", choices=["resting", "scratch"], required=True)
    ap.add_argument("--padding",
                    choices=["replicate", "zero", "mean", "spatial_only", "cyclic_replicate"],
                    default="replicate",
                    help="replicate: 마지막 frame 만 (N-T) 번 복제; "
                         "zero: 0 으로 (N-T) 채움; "
                         "mean: 실제 T + (N-T) 를 T frames 평균으로 채움 (proper); "
                         "spatial_only: 전체 N frames 모두 평균값 (시간정보 0, control); "
                         "cyclic_replicate: T frames 를 N 길이까지 반복 (e.g. T=5 → 5+5+5+5)")
    ap.add_argument("--subject", default="sub-01")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--batch_size", type=int, default=4)
    ap.add_argument("--num_workers", type=int, default=2)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--out_root", default=str(EmoBrain_ROOT / "output/embeddings"))
    ap.add_argument("--limit_n", type=int, default=None)
    ap.add_argument("--save_layers", choices=["final", "all"], default="final",
                    help="final: (N, D_final) pooled only; "
                         "all: final + per-layer pooled (N, D_layer) for each Swin stage "
                         "(matches SwiFT downstream --layer_key convention)")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device(args.device)

    out_dir = Path(args.out_root) / f"swift_{args.output_tag}_{args.init}_pad-{args.padding}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== EmoBrain SwiFT extraction ===")
    print(f"  model    : {args.model_name}  (output_tag: {args.output_tag})")
    print(f"  init     : {args.init}")
    print(f"  padding  : {args.padding}")
    print(f"  subject  : {args.subject}")
    print(f"  output   : {out_dir}")

    dataset = EmoBrainHorikawaSwiFTDataset(args.subject, padding=args.padding)
    if args.limit_n:
        dataset.stim_names = dataset.stim_names[:args.limit_n]
        dataset.stim_nums = dataset.stim_nums[:args.limit_n]
        print(f"  [LIMIT] processing {args.limit_n} stimuli only")
    loader = DataLoader(
        dataset, batch_size=args.batch_size, shuffle=False,
        num_workers=args.num_workers, pin_memory=True, collate_fn=collate,
    )

    print(f"\n[Model] building {args.model_name}")
    model, cfg = build_model(args.model_name)
    if args.init == "resting":
        ckpt_path = cfg["ckpt"]
        print(f"[Model] loading resting-pretrained: {ckpt_path}")
        model = load_pretrained(model, ckpt_path)
    else:
        print(f"[Model] scratch random init (seed={args.seed})")
    model.to(device).eval()
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[Model] params: {n_params/1e6:.2f}M")

    save_all_layers = (args.save_layers == "all")
    embeddings, stim_nums, padding_ratios, original_Ts = [], [], [], []
    per_layer = {}  # layer_key -> list of (B, D_layer) pooled tensors
    print(f"\n[Extract] {len(dataset)} stimuli, batch_size={args.batch_size}, "
          f"save_layers={args.save_layers}")
    with torch.no_grad():
        for i, batch in enumerate(loader):
            fmri = batch["fmri"].to(device, non_blocking=True)
            if save_all_layers:
                layer_dict = forward_embedding(model, fmri, return_all=True)
                for k, v in layer_dict.items():
                    if isinstance(v, tuple):
                        v = v[0]
                    per_layer.setdefault(k, []).append(
                        pool_features(v).cpu().numpy().astype(np.float32))
                final_key = f"layer_{model.num_layers - 1}"
                final = layer_dict[final_key]
                if isinstance(final, tuple):
                    final = final[0]
                emb = pool_features(final)
            else:
                out = forward_embedding(model, fmri)
                if isinstance(out, tuple):
                    out = out[0]
                emb = pool_features(out)
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

    payload = {
        "embeddings": torch.from_numpy(embeddings),
        "stim_num": torch.from_numpy(stim_nums),
        "padding_ratio": torch.from_numpy(padding_ratios),
        "original_T": torch.from_numpy(original_Ts),
        "init": args.init,
        "padding": args.padding,
        "seed": args.seed,
        "model": args.model_name,
        "embed_dim": cfg["embed_dim"],
        "version": cfg["version"],
        "save_layers": args.save_layers,
    }
    if save_all_layers:
        for k, chunks in per_layer.items():
            payload[k] = torch.from_numpy(np.concatenate(chunks, axis=0))

    out_path = out_dir / f"{args.subject}.pt"
    torch.save(payload, out_path)
    print(f"\n[Saved] {out_path}")
    print(f"  embeddings shape : {embeddings.shape}")
    if save_all_layers:
        for k in per_layer:
            print(f"  {k:10s} shape : {payload[k].shape}")
    print(f"  padding_ratio    : min={padding_ratios.min():.3f} max={padding_ratios.max():.3f} mean={padding_ratios.mean():.3f}")
    print(f"  any NaN          : {np.isnan(embeddings).any()}")
    print(f"  embedding stats  : min={embeddings.min():.3f} max={embeddings.max():.3f} mean={embeddings.mean():.3f}")


if __name__ == "__main__":
    main()
