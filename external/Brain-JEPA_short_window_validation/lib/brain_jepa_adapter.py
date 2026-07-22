"""Audited Brain-JEPA construction and checkpoint adaptation."""

import hashlib
import sys
from pathlib import Path

import numpy as np
import torch


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
EMOBRAIN_ROOT = PACKAGE_ROOT.parents[1]
BRAIN_JEPA_REPO = EMOBRAIN_ROOT / "external/Brain-JEPA"
CHECKPOINT = EMOBRAIN_ROOT / "external/checkpoints/brain_jepa/jepa-ep300.pth"
GRADIENT_CSV = BRAIN_JEPA_REPO / "data/gradient_mapping_450.csv"
N_ROIS = 450
PATCH_SIZE = 16
EMBED_DIM = 768

sys.path.insert(0, str(BRAIN_JEPA_REPO))
from downstream_tasks.models_vit_embedding_extraction import VisionTransformer


class ModelArgs:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def tensor_hash(tensor):
    values = tensor.detach().cpu().contiguous().numpy()
    return hashlib.sha256(values.tobytes()).hexdigest()


def build_model(num_frames, device="cpu"):
    if num_frames % PATCH_SIZE:
        raise ValueError(f"num_frames must be divisible by patch size {PATCH_SIZE}")
    args = ModelArgs(
        model_name="vit_base",
        attn_mode="normal",
        nb_classes=2,
        global_pool=True,
        add_w="mapping",
        crop_size=(N_ROIS, num_frames),
        patch_size=PATCH_SIZE,
        pred_depth=12,
        pred_emb_dim=384,
        use_normalization=True,
        gradient_checkpointing=False,
    )
    return VisionTransformer(
        args,
        model_name=args.model_name,
        attn_mode=args.attn_mode,
        num_classes=args.nb_classes,
        global_pool=args.global_pool,
        device=torch.device(device),
        add_w=args.add_w,
    )


def _adapt_temporal_code(checkpoint_code, model_code, policy):
    n_rois = model_code.shape[0]
    if checkpoint_code.shape[0] % n_rois:
        raise ValueError("Checkpoint temporal code is not divisible by the ROI count")
    n_time = checkpoint_code.shape[0] // n_rois
    reshaped = checkpoint_code.reshape(n_rois, n_time, -1)
    if policy == "temporal_mean":
        return reshaped.mean(dim=1), n_time
    if policy == "temporal_center":
        center = [n_time // 2] if n_time % 2 else [n_time // 2 - 1, n_time // 2]
        return reshaped[:, center].mean(dim=1), n_time
    raise ValueError(f"Unsupported temporal adaptation policy: {policy}")


def load_pretrained(model, position_policy):
    checkpoint = torch.load(CHECKPOINT, map_location="cpu")
    state = {
        key.replace("module.", "encoder."): value
        for key, value in checkpoint["encoder"].items()
    }
    model_state = model.state_dict()
    position_key = "encoder.pos_embed_proj.emb_h"
    patch_key = "encoder.patch_embed.proj.weight"

    if state[patch_key].shape != model_state[patch_key].shape:
        raise RuntimeError(
            "Patch embedding mismatch. Validation code refuses pretrained-weight interpolation: "
            f"checkpoint={tuple(state[patch_key].shape)}, model={tuple(model_state[patch_key].shape)}"
        )

    checkpoint_position_shape = tuple(state[position_key].shape)
    model_position_shape = tuple(model_state[position_key].shape)
    native_hash = tensor_hash(model_state[position_key])
    if checkpoint_position_shape == model_position_shape:
        if position_policy not in {"checkpoint", "native"}:
            raise ValueError("Temporal adaptation is only defined for a shorter target grid")
        applied_policy = "checkpoint"
        n_checkpoint_time = checkpoint_position_shape[0] // N_ROIS
    elif position_policy == "native":
        del state[position_key]
        applied_policy = "native"
        n_checkpoint_time = checkpoint_position_shape[0] // N_ROIS
    else:
        state[position_key], n_checkpoint_time = _adapt_temporal_code(
            state[position_key], model_state[position_key], position_policy
        )
        applied_policy = position_policy

    message = model.load_state_dict(state, strict=False)
    allowed_missing = {"head.weight", "head.bias", "fc_norm.weight", "fc_norm.bias"}
    if applied_policy == "native" and checkpoint_position_shape != model_position_shape:
        allowed_missing.add(position_key)
    unexpected_missing = sorted(set(message.missing_keys) - allowed_missing)
    if unexpected_missing or message.unexpected_keys:
        raise RuntimeError(
            f"Checkpoint mismatch: missing={unexpected_missing}, unexpected={message.unexpected_keys}"
        )
    if applied_policy == "native" and tensor_hash(model.state_dict()[position_key]) != native_hash:
        raise RuntimeError("Native target-grid positional code changed during checkpoint loading")

    loaded_parameters = sum(
        value.numel() for key, value in state.items() if key in model_state
    )
    return {
        "checkpoint": str(CHECKPOINT),
        "requested_position_policy": position_policy,
        "applied_position_policy": applied_policy,
        "checkpoint_position_shape": checkpoint_position_shape,
        "model_position_shape": model_position_shape,
        "checkpoint_time_patches": int(n_checkpoint_time),
        "model_time_patches": int(model_position_shape[0] // N_ROIS),
        "checkpoint_patch_shape": tuple(state[patch_key].shape),
        "model_patch_shape": tuple(model_state[patch_key].shape),
        "position_code_trainable": bool(model_state[position_key].requires_grad),
        "position_code_sha256": tensor_hash(model.state_dict()[position_key]),
        "loaded_parameter_count": int(loaded_parameters),
        "missing_keys": list(message.missing_keys),
        "unexpected_keys": list(message.unexpected_keys),
    }


def create_encoder(init, num_frames, position_policy, device, seed=0):
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = build_model(num_frames=num_frames, device=device)
    if init == "pretrained":
        audit = load_pretrained(model, position_policy=position_policy)
    elif init == "scratch":
        if position_policy not in {"native", "checkpoint"}:
            raise ValueError("Scratch has no checkpoint temporal code to adapt")
        state = model.state_dict()
        audit = {
            "checkpoint": None,
            "requested_position_policy": position_policy,
            "applied_position_policy": "native",
            "checkpoint_position_shape": None,
            "model_position_shape": tuple(state["encoder.pos_embed_proj.emb_h"].shape),
            "checkpoint_time_patches": None,
            "model_time_patches": num_frames // PATCH_SIZE,
            "checkpoint_patch_shape": None,
            "model_patch_shape": tuple(state["encoder.patch_embed.proj.weight"].shape),
            "position_code_trainable": False,
            "position_code_sha256": tensor_hash(state["encoder.pos_embed_proj.emb_h"]),
            "loaded_parameter_count": 0,
            "missing_keys": [],
            "unexpected_keys": [],
        }
    else:
        raise ValueError(f"Unknown initialization: {init}")
    model.head = torch.nn.Identity()
    model.to(device).eval()
    return model, audit


def embed_batches(model, loader, device):
    embeddings, metadata = [], {"stim_num": [], "original_T": [], "padding_ratio": []}
    with torch.no_grad():
        for batch_i, batch in enumerate(loader):
            output = model(batch["fmri"].to(device, non_blocking=True))
            if isinstance(output, tuple):
                output = output[0]
            embeddings.append(output.detach().cpu().numpy().astype(np.float32))
            for key in metadata:
                if key in batch:
                    metadata[key].append(np.asarray(batch[key]))
            if (batch_i + 1) % 10 == 0 or batch_i + 1 == len(loader):
                print(f"batch {batch_i + 1}/{len(loader)}")
    embeddings = np.concatenate(embeddings)
    if not np.isfinite(embeddings).all():
        raise ValueError("Non-finite values in embeddings")
    metadata = {
        key: np.concatenate(parts) for key, parts in metadata.items() if parts
    }
    return embeddings, metadata
