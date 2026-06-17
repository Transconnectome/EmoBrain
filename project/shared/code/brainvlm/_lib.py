"""
EmoBrain BrainVLM helpers — shared utilities for Path B (hybrid) and Path C (decoupled).

- Horikawa fMRI volume loading + reshape to BrainVLM (B,C,D,H,W,T) format
- PatchEmbedQwen instantiation with the upstream-bug workaround
- Conversation JSON building helpers
- Video feature loading (EmoViS symlinks)

Paths
  Path B (hybrid):   fMRI → BrainVLM PatchEmbedQwen.fMRI + Qwen3-VL ViT
                     video → Qwen3-VL native vision tower (image/video patcher)
                     both stream LLM tokens together.
  Path C (decoupled): fMRI → BrainVLM PatchEmbedQwen.fMRI + Qwen3-VL ViT
                     video → EmoViS pre-extracted features (V-JEPA2 / CLIP / DINOv2)
                              injected via lightweight cross-attention OR text-prefix
                              (no Qwen3-VL native vision tower for video).
"""
from pathlib import Path
import sys
import warnings

import numpy as np
import torch
import torch.nn.functional as F

warnings.filterwarnings("ignore")

EmoBrain_ROOT = Path("/pscratch/sd/s/sjmoon/EmoBrain")
BRAINVLM_ROOT = Path("/pscratch/sd/s/sjmoon/BrainVLM/UMBRELLA_qwen")
HORIKAWA_VOL_BASE = Path("/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img")
CANONICAL_CSV = EmoBrain_ROOT / "data/feelin_canonical_stimuli.csv"
EMOVIS_FEATURES = EmoBrain_ROOT / "data/stimulus_features"

# Default BrainVLM fMRI config matching Horikawa post-spatial-pad shape (96^3 × 20)
FMRI_IMG_SIZE = (96, 96, 96, 20)
FMRI_PATCH_SIZE = (16, 16, 16, 5)

if str(BRAINVLM_ROOT) not in sys.path:
    sys.path.insert(0, str(BRAINVLM_ROOT))


# ============================================================
# fMRI loading and reshape
# ============================================================
def load_horikawa_fmri(subject: str, stim_name: str, T_target: int = 20,
                       padding: str = "zero") -> torch.Tensor:
    """
    Load one Horikawa fMRI stimulus and reshape to BrainVLM input (1, 1, 96, 96, 96, T).
    Applies spatial pad to 96^3 + temporal pad to T_target using `padding` mode.
    """
    stim_dir = HORIKAWA_VOL_BASE / f"{subject}_{stim_name}"
    frame_files = sorted(stim_dir.glob("frame_*.pt"))
    frames = []
    for f in frame_files:
        frame = torch.load(str(f), weights_only=False)
        if hasattr(frame, "as_tensor"):
            frame = frame.as_tensor()
        frames.append(frame)
    y = torch.stack(frames, dim=0)                       # (T, 74, 91, 81, 1)
    y = y.squeeze(-1).permute(1, 2, 3, 0)                # (74, 91, 81, T)
    y = y.unsqueeze(0)                                   # (1, 74, 91, 81, T)

    # Spatial pad to (96, 96, 96)
    bg = float(y.flatten()[0].item())
    T = y.shape[-1]
    y = y.permute(0, 4, 1, 2, 3).contiguous()            # (1, T, 74, 91, 81)
    y = F.pad(y, (7, 8, 2, 3, 11, 11), value=bg)         # (1, T, 96, 96, 96)
    y = y.permute(0, 2, 3, 4, 1).contiguous()            # (1, 96, 96, 96, T)

    # Temporal pad
    if T > T_target:
        y = y[..., :T_target].contiguous()
    elif T < T_target:
        pad_len = T_target - T
        if padding == "zero":
            y = F.pad(y, (0, pad_len), value=0.0)
        elif padding == "mean":
            mf = y.mean(dim=-1, keepdim=True)
            y = torch.cat([y, mf.expand(*mf.shape[:-1], pad_len)], dim=-1)
        elif padding == "replicate":
            last = y[..., -1:]
            y = torch.cat([y, last.expand(*last.shape[:-1], pad_len)], dim=-1)
        else:
            raise ValueError(padding)
    # add channel dim → (1, 1, 96, 96, 96, T_target)
    return y.unsqueeze(0)


# ============================================================
# PatchEmbedQwen with bug workaround
# ============================================================
def make_patch_embed(embed_dim: int = 1152,
                     fMRI_size=FMRI_IMG_SIZE,
                     fMRI_patch_size=FMRI_PATCH_SIZE,
                     dtype=torch.float32):
    """Instantiate PatchEmbedQwen + monkey-patch fMRI_patch_size attribute (upstream bug)."""
    from project.model.patch_embed_qwen_NoPool import PatchEmbedQwen
    pe = PatchEmbedQwen(
        sMRI_size=[128, 128, 128], sMRI_patch_size=[18, 18, 18],
        dMRI_size=[128, 128, 128], dMRI_patch_size=[18, 18, 18],
        fMRI_size=list(fMRI_size), fMRI_patch_size=list(fMRI_patch_size),
        embed_dim=embed_dim, dtype=dtype,
    )
    # Workaround for upstream bug
    pe.fMRI_patch_size = tuple(fMRI_patch_size)
    pe.sMRI_patch_size = (18, 18, 18)
    pe.dMRI_patch_size = (18, 18, 18)
    return pe


# ============================================================
# Conversation format
# ============================================================
def build_emotion_query_conversation(fmri_path: str, question: str = None) -> dict:
    """
    Build a one-turn ABCD-style conversation for a single (subject, stim) fMRI.
    fmri_path: path to a .nii.gz or .pt file that the BrainVLM dataset loader will read.
    """
    if question is None:
        question = ("Given the following fMRI activity recorded while a subject viewed a short "
                    "video clip, describe the emotional experience evoked in the subject. "
                    "Provide the valence (negative to positive) and arousal (calm to intense), "
                    "as well as a brief affective caption.")
    return {
        "task_type": "Emotion_VQA_Horikawa",
        "conversations": [
            {
                "role": "user",
                "content": [
                    {"type": "image", "modality": "fMRI", "image_path": fmri_path},
                    {"type": "text", "text": question},
                ],
            },
        ],
    }


# ============================================================
# Video feature loading (Path C)
# ============================================================
def load_video_feature(name: str = "vjepa2_pretrained") -> tuple[np.ndarray, np.ndarray]:
    """Load EmoViS pre-extracted video feature (Path C).
    Returns (features, stim_idx). features shape: (N_stim, D)."""
    feats = np.load(EMOVIS_FEATURES / f"{name}.npy")
    stim_idx = np.load(EMOVIS_FEATURES / "stim_idx.npy")
    return feats, stim_idx
