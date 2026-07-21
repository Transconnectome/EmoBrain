"""
Step 2: Extract V-JEPA2 embeddings for 2196 Cowen emotion videos.
Requires Step 1 (model already downloaded).

Output: /pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy
        shape: (2196, 1408)  — row i corresponds to stimulus_(i+1)
"""

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
NUM_FRAMES  = 16      # sample 16 frames per video uniformly
BATCH_SIZE  = 8
DEVICE      = "cuda" if torch.cuda.is_available() else "cpu"

# ── Load model (from cache) ───────────────────────────────────────────────────
print(f"Loading {MODEL_NAME} from cache on {DEVICE}...")
processor = VJEPA2VideoProcessor.from_pretrained(MODEL_NAME)
model     = VJEPA2Model.from_pretrained(MODEL_NAME, torch_dtype=torch.float16)
model     = model.to(DEVICE).eval()
print(f"Model loaded. Hidden dim: {model.config.hidden_size}")

# ── Helper: load video frames ─────────────────────────────────────────────────
def load_frames(video_path: Path, n_frames: int) -> list:
    """Return list of n_frames RGB numpy arrays (H, W, 3), uniformly sampled."""
    clip   = VideoFileClip(str(video_path))
    times  = np.linspace(0, clip.duration, n_frames, endpoint=False)
    frames = [clip.get_frame(t) for t in times]
    clip.close()
    return frames

# ── Stimulus paths: stimulus_1 → 0001.mp4, ..., stimulus_2196 → 2196.mp4 ─────
N = 2196
video_paths = [VIDEO_DIR / f"{i:04d}.mp4" for i in range(1, N + 1)]

missing = [p for p in video_paths if not p.exists()]
if missing:
    print(f"WARNING: {len(missing)} missing video files: {[p.name for p in missing[:5]]}")

# ── Extract embeddings ────────────────────────────────────────────────────────
hidden_dim = model.config.hidden_size
embeddings = np.zeros((N, hidden_dim), dtype=np.float32)

print(f"Extracting embeddings: {N} videos, batch_size={BATCH_SIZE}, frames_per_video={NUM_FRAMES}")

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
        hidden = model(**inputs).last_hidden_state  # (B, seq_len, D)
        emb    = hidden.mean(dim=1).float().cpu().numpy()  # (B, D)

    for i, stim_idx in enumerate(valid_indices):
        embeddings[stim_idx] = emb[i]

    if batch_end % 200 == 0 or batch_end == N:
        print(f"  [{batch_end}/{N}] done")

# ── Save ──────────────────────────────────────────────────────────────────────
np.save(OUTPUT_FILE, embeddings)
print(f"\nSaved: {OUTPUT_FILE}")
print(f"Shape: {embeddings.shape}")
print(f"Non-zero rows: {np.sum(np.any(embeddings != 0, axis=1))}/{N}")
