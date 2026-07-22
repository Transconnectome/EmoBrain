"""
Extract V-JEPA2 video embeddings for 2196 Cowen emotion videos.
Output: /pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy
        shape: (2196, hidden_dim)  — stimulus_1..2196 order
"""

import os
import numpy as np
import torch
from pathlib import Path
from transformers import VJEPA2Model, VJEPA2VideoProcessor
from moviepy import VideoFileClip
import warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
VIDEO_DIR   = Path("/pscratch/sd/s/sjmoon/EmoFM/videos/CowenEmotionVideos")
OUTPUT_DIR  = Path("/pscratch/sd/s/sjmoon/EmoFM/video_embeddings")
OUTPUT_FILE = OUTPUT_DIR / "vjepa2_embeddings.npy"
OUTPUT_DIR.mkdir(exist_ok=True)

MODEL_NAME  = "facebook/vjepa2-vitg-fpc64-256"
NUM_FRAMES  = 16        # sample N frames per video (64 is default but heavy; 16 is faster)
BATCH_SIZE  = 8
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu"

# ── Load model ────────────────────────────────────────────────────────────────
print(f"Loading {MODEL_NAME} on {DEVICE}...")
processor = VJEPA2VideoProcessor.from_pretrained(MODEL_NAME)
model     = VJEPA2Model.from_pretrained(MODEL_NAME, torch_dtype=torch.float16)
model     = model.to(DEVICE).eval()
print(f"Model loaded. Hidden dim: {model.config.hidden_size}")

# ── Helper: load video frames ─────────────────────────────────────────────────
def load_frames(video_path: Path, n_frames: int) -> list:
    """Return list of n_frames RGB numpy arrays (H, W, 3), uniformly sampled."""
    clip = VideoFileClip(str(video_path))
    duration = clip.duration
    times = np.linspace(0, duration, n_frames, endpoint=False)
    frames = []
    for t in times:
        frame = clip.get_frame(t)   # (H, W, 3) uint8
        frames.append(frame)
    clip.close()
    return frames

# ── Collect stimulus paths in order 1..2196 ───────────────────────────────────
n_total = 2196
video_paths = [VIDEO_DIR / f"{i:04d}.mp4" for i in range(1, n_total + 1)]
missing = [p for p in video_paths if not p.exists()]
if missing:
    print(f"WARNING: {len(missing)} missing videos: {missing[:5]}")

# ── Extract embeddings in batches ─────────────────────────────────────────────
embeddings = np.zeros((n_total, model.config.hidden_size), dtype=np.float32)

print(f"Extracting embeddings for {n_total} videos (batch_size={BATCH_SIZE}, frames={NUM_FRAMES})...")

for batch_start in range(0, n_total, BATCH_SIZE):
    batch_end   = min(batch_start + BATCH_SIZE, n_total)
    batch_paths = video_paths[batch_start:batch_end]

    # Load frames for each video in the batch
    batch_frames = []
    valid_indices = []
    for idx, vp in enumerate(batch_paths):
        if not vp.exists():
            continue
        try:
            frames = load_frames(vp, NUM_FRAMES)
            batch_frames.append(frames)
            valid_indices.append(batch_start + idx)
        except Exception as e:
            print(f"  ERROR loading {vp.name}: {e}")
            continue

    if not batch_frames:
        continue

    # Processor expects list of lists: [[frame, ...], [frame, ...], ...]
    inputs = processor(
        videos=batch_frames,
        return_tensors="pt",
    )
    inputs = {k: v.to(DEVICE, dtype=torch.float16 if v.dtype == torch.float32 else v.dtype)
              for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        # last_hidden_state: (B, seq_len, hidden_dim)
        # mean pool over spatial+temporal tokens (exclude CLS if present)
        hidden = outputs.last_hidden_state   # (B, seq_len, D)
        emb    = hidden.mean(dim=1)          # (B, D)
        emb    = emb.float().cpu().numpy()

    for i, stim_idx in enumerate(valid_indices):
        embeddings[stim_idx] = emb[i]

    if (batch_start // BATCH_SIZE) % 10 == 0:
        print(f"  [{batch_end}/{n_total}] done")

# ── Save ──────────────────────────────────────────────────────────────────────
np.save(OUTPUT_FILE, embeddings)
print(f"\nSaved: {OUTPUT_FILE}  shape={embeddings.shape}")

# Quick sanity check
non_zero = np.sum(np.any(embeddings != 0, axis=1))
print(f"Non-zero rows: {non_zero}/{n_total}")
