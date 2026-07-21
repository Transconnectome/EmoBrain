"""
Step 5: Extract CLIP (ViT-B/32) embeddings for all 2196 videos.

Strategy: extract 8 frames per video (uniformly sampled), encode each with CLIP,
          then mean-pool across frames → 512-dim embedding per video.

Output: /pscratch/sd/s/sjmoon/EmoFM/video_embeddings/clip_embeddings.npy
        shape: (2196, 512)
"""

import numpy as np
import torch
from pathlib import Path
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
from moviepy import VideoFileClip
import warnings
warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
VIDEO_DIR   = Path("/pscratch/sd/s/sjmoon/EmoFM/videos/CowenEmotionVideos")
OUTPUT_DIR  = Path("/pscratch/sd/s/sjmoon/EmoFM/video_embeddings")
OUTPUT_FILE = OUTPUT_DIR / "clip_embeddings.npy"
OUTPUT_DIR.mkdir(exist_ok=True)

CLIP_MODEL_ID = "openai/clip-vit-base-patch32"
N_FRAMES   = 8
BATCH_SIZE = 32  # number of videos per batch
DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Device: {DEVICE}")

# ── Load CLIP ─────────────────────────────────────────────────────────────────
print("Loading CLIP...")
model     = CLIPModel.from_pretrained(CLIP_MODEL_ID).to(DEVICE)
processor = CLIPProcessor.from_pretrained(CLIP_MODEL_ID)
model.eval()
print("CLIP loaded.")

# ── Frame extraction helper ────────────────────────────────────────────────────
def sample_frames(video_path: Path, n_frames: int = N_FRAMES):
    """Return n_frames uniformly sampled PIL Images from video."""
    try:
        clip   = VideoFileClip(str(video_path))
        times  = np.linspace(0, clip.duration, n_frames, endpoint=False)
        frames = [Image.fromarray(clip.get_frame(t).astype(np.uint8)) for t in times]
        clip.close()
        return frames
    except Exception as e:
        print(f"  ERROR reading {video_path.name}: {e}")
        return None

# ── Extract embeddings ─────────────────────────────────────────────────────────
video_files = sorted(VIDEO_DIR.glob("*.mp4"))
N = len(video_files)
print(f"Found {N} videos")

embeddings = np.zeros((N, 512), dtype=np.float32)
failed     = []

with torch.no_grad():
    for batch_start in range(0, N, BATCH_SIZE):
        batch_files = video_files[batch_start:batch_start + BATCH_SIZE]
        batch_frames_flat = []   # all frames across batch
        frame_counts      = []   # how many frames per video

        for vf in batch_files:
            frames = sample_frames(vf, N_FRAMES)
            if frames is None:
                frame_counts.append(0)
                failed.append(vf.stem)
            else:
                batch_frames_flat.extend(frames)
                frame_counts.append(len(frames))

        if not batch_frames_flat:
            continue

        # Encode all frames at once
        inputs = processor(images=batch_frames_flat, return_tensors="pt", padding=True)
        pixel_values = inputs["pixel_values"].to(DEVICE)
        out    = model.vision_model(pixel_values=pixel_values)
        pooled = out.pooler_output                          # (total_frames, 768)
        feats  = model.visual_projection(pooled)            # (total_frames, 512)
        feats  = feats / feats.norm(dim=-1, keepdim=True)  # L2 normalize
        feats  = feats.cpu().numpy()

        # Pool frames per video
        ptr = 0
        for vi, (vf, fc) in enumerate(zip(batch_files, frame_counts)):
            idx = batch_start + vi
            stim_num = int(vf.stem) - 1   # 0001.mp4 → index 0
            if fc == 0:
                embeddings[stim_num] = 0.0
            else:
                emb = feats[ptr:ptr + fc].mean(axis=0)
                emb = emb / (np.linalg.norm(emb) + 1e-8)
                embeddings[stim_num] = emb
                ptr += fc

        if (batch_start // BATCH_SIZE) % 10 == 0:
            print(f"  Processed {min(batch_start + BATCH_SIZE, N)}/{N}")

print(f"\nFailed videos: {len(failed)} {failed[:5] if failed else ''}")
np.save(OUTPUT_FILE, embeddings)
print(f"Saved: {OUTPUT_FILE}")
print(f"Shape: {embeddings.shape}")
print(f"Non-zero rows: {int(np.any(embeddings != 0, axis=1).sum())}")
