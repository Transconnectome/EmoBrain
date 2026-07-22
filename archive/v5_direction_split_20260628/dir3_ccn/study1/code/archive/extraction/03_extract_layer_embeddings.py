"""
Step 3: Extract V-JEPA2 per-layer embeddings for 2196 Cowen emotion videos.

Output: /pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_layer_embeddings.npy
        shape: (41, 2196, 1408)
        axis 0: layer index 0 = initial patch embedding, 1~40 = transformer blocks
"""

import numpy as np
import torch
from pathlib import Path
from transformers import VJEPA2Model, VJEPA2VideoProcessor
from moviepy import VideoFileClip
import warnings
warnings.filterwarnings("ignore")

VIDEO_DIR   = Path("/pscratch/sd/s/sjmoon/EmoFM/videos/CowenEmotionVideos")
OUTPUT_DIR  = Path("/pscratch/sd/s/sjmoon/EmoFM/video_embeddings")
OUTPUT_FILE = OUTPUT_DIR / "vjepa2_layer_embeddings.npy"
OUTPUT_DIR.mkdir(exist_ok=True)

MODEL_NAME = "facebook/vjepa2-vitg-fpc64-256"
NUM_FRAMES = 16
BATCH_SIZE = 4      # smaller batch: all hidden states × B held in memory
DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading {MODEL_NAME} on {DEVICE}...")
processor = VJEPA2VideoProcessor.from_pretrained(MODEL_NAME)
model     = VJEPA2Model.from_pretrained(MODEL_NAME, torch_dtype=torch.float16)
model     = model.to(DEVICE).eval()

NUM_LAYERS  = model.config.num_hidden_layers   # 40
HIDDEN_SIZE = model.config.hidden_size          # 1408
TOTAL_REPS  = NUM_LAYERS + 1                    # +1 for initial embedding (layer 0)

print(f"V-JEPA2: {NUM_LAYERS} transformer blocks, hidden_size={HIDDEN_SIZE}")
print(f"Output shape will be ({TOTAL_REPS}, 2196, {HIDDEN_SIZE})")

def load_frames(video_path: Path, n_frames: int) -> list:
    clip   = VideoFileClip(str(video_path))
    times  = np.linspace(0, clip.duration, n_frames, endpoint=False)
    frames = [clip.get_frame(t) for t in times]
    clip.close()
    return frames

N = 2196
video_paths = [VIDEO_DIR / f"{i:04d}.mp4" for i in range(1, N + 1)]

layer_embeddings = np.zeros((TOTAL_REPS, N, HIDDEN_SIZE), dtype=np.float32)

print(f"\nExtracting per-layer embeddings: {N} videos, batch_size={BATCH_SIZE}")

for batch_start in range(0, N, BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, N)

    batch_frames  = []
    valid_indices = []

    for idx in range(batch_start, batch_end):
        vp = video_paths[idx]
        if not vp.exists():
            continue
        try:
            frames = load_frames(vp, NUM_FRAMES)
            batch_frames.append(frames)
            valid_indices.append(idx)
        except Exception as e:
            print(f"  ERROR {vp.name}: {e}")

    if not batch_frames:
        continue

    inputs = processor(videos=batch_frames, return_tensors="pt")
    inputs = {k: v.to(DEVICE, dtype=torch.float16 if v.is_floating_point() else v.dtype)
              for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)
        # hidden_states: tuple of (TOTAL_REPS,) each (B, seq_len, hidden_size)
        hidden_states = outputs.hidden_states

    for layer_idx, hs in enumerate(hidden_states):
        # hs: (B, seq_len, hidden_size) — mean pool over sequence
        pooled = hs.float().mean(dim=1).cpu().numpy()  # (B, hidden_size)
        for i, stim_idx in enumerate(valid_indices):
            layer_embeddings[layer_idx, stim_idx] = pooled[i]

    if batch_end % 100 == 0 or batch_end == N:
        print(f"  [{batch_end}/{N}] done")

np.save(OUTPUT_FILE, layer_embeddings)
print(f"\nSaved: {OUTPUT_FILE}")
print(f"Shape: {layer_embeddings.shape}")
print(f"Non-zero stimuli (layer 0): {np.any(layer_embeddings[0] != 0, axis=1).sum()}/{N}")
