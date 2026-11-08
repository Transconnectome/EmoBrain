"""Unified embedding loader for clustering exploration.

Returns per source a (N_stim=2185, D) np.ndarray + 1-D stim_idx (0..N-1) order.

Sources covered (alias -> path):
  video.vjepa2     stimulus_features/vjepa2_pretrained.npy   (D=1408)
  video.clip       stimulus_features/clip_pretrained.npy     (D=1024)
  video.dinov2     stimulus_features/dinov2_pretrained.npy   (D=?)
  video.videomae   stimulus_features/videomae_pretrained.npy (D=?)
  video.caption    stimulus_features/caption_embed.npy       (D=?)
  brain.roi_mean   embeddings/roi_schaefer400tian50_mean/sub-XX.pt   (D=450, pooled over 5 subj)
  brain.brain_jepa embeddings/brain_jepa_resting_pad-mean/sub-XX.pt  (D=768, pooled)
  brain.swift      embeddings/swift_NewE96_SL20_resting_pad-mean/sub-XX.pt (D=768, pooled)

Pooled = mean across 5 subjects (per-stim). exploratory simplification.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

REPO = Path("/pscratch/sd/s/sjmoon/EmoBrain")
SHARED = REPO / "project" / "shared"
N_STIM = 2185
N_SUBJ = 5

VIDEO_SOURCES = {
    "vjepa2":   "vjepa2_pretrained.npy",
    "clip":     "clip_pretrained.npy",
    "dinov2":   "dinov2_pretrained.npy",
    "videomae": "videomae_pretrained.npy",
    "caption":  "caption_embed.npy",
}

BRAIN_SOURCES = {
    "roi_mean":   "roi_schaefer400tian50_mean",
    "brain_jepa": "brain_jepa_resting_pad-mean",
    "swift":      "swift_NewE96_SL20_resting_pad-mean",
}


def load_video(name: str) -> np.ndarray:
    if name not in VIDEO_SOURCES:
        raise KeyError(f"unknown video source: {name}")
    arr = np.load(SHARED / "data" / "stimulus_features" / VIDEO_SOURCES[name])
    assert arr.shape[0] == N_STIM, f"{name}: expected N={N_STIM}, got {arr.shape}"
    return arr.astype(np.float32)


def load_brain(name: str, subjects: tuple[int, ...] = (1, 2, 3, 4, 5)) -> np.ndarray:
    """Load and average per-subject brain embedding to a single (N_stim, D) array."""
    if name not in BRAIN_SOURCES:
        raise KeyError(f"unknown brain source: {name}")
    base = SHARED / "output" / "embeddings" / BRAIN_SOURCES[name]
    arrs = []
    for s in subjects:
        d = torch.load(base / f"sub-{s:02d}.pt", weights_only=False, map_location="cpu")
        e = d["embeddings"].detach().cpu().numpy().astype(np.float32)
        assert e.shape[0] == N_STIM, f"{name} sub-{s}: expected N={N_STIM}, got {e.shape}"
        arrs.append(e)
    return np.stack(arrs, axis=0).mean(axis=0)


def load_brain_single_subject(name: str, subject: int) -> np.ndarray:
    """Load one subject's brain embedding as (N_stim, D)."""
    if name not in BRAIN_SOURCES:
        raise KeyError(f"unknown brain source: {name}")
    base = SHARED / "output" / "embeddings" / BRAIN_SOURCES[name]
    d = torch.load(base / f"sub-{subject:02d}.pt", weights_only=False, map_location="cpu")
    e = d["embeddings"].detach().cpu().numpy().astype(np.float32)
    assert e.shape[0] == N_STIM, f"{name} sub-{subject}: expected N={N_STIM}, got {e.shape}"
    return e


def load_cowen_labels() -> dict:
    """Cowen 34 cat probabilities + valence/arousal/dominance + 11 extra dims."""
    import pandas as pd
    df = pd.read_csv(SHARED / "data" / "cowen_horikawa_labels.csv")
    df = df.sort_values("stim_idx").reset_index(drop=True)
    assert len(df) == N_STIM, f"expected {N_STIM} stim, got {len(df)}"
    cat34 = df[[f"score_{i}" for i in range(34)]].to_numpy(dtype=np.float32)
    va = df[["valence_score", "arousal_score"]].to_numpy(dtype=np.float32)
    cat_norm = cat34 / np.clip(cat34.sum(axis=1, keepdims=True), 1e-8, None)
    entropy = -(cat_norm * np.log(cat_norm + 1e-12)).sum(axis=1)  # high = mixed, low = dominant top1
    top1 = cat34.argmax(axis=1)
    second = cat34.copy()
    second[np.arange(len(second)), top1] = -np.inf
    top2 = second.argmax(axis=1)
    return {
        "cat34_soft": cat34,
        "cat34_top1": top1,
        "cat34_top2": top2,
        "cat34_entropy": entropy,
        "va": va,
        "valence": va[:, 0],
        "arousal": va[:, 1],
        "stim_idx": df["stim_idx"].to_numpy(),
    }


ALL_SOURCES = {f"video.{k}": ("video", k) for k in VIDEO_SOURCES} | {f"brain.{k}": ("brain", k) for k in BRAIN_SOURCES}


def load(source: str) -> np.ndarray:
    side, name = ALL_SOURCES[source]
    return load_video(name) if side == "video" else load_brain(name)
