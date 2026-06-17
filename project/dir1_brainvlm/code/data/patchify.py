"""L1 Schaefer 2D grid patchifier.

Horikawa fMRI ROI time series (T, 450) -> 2D image (3, 224, 224) for Qwen3-VL ViT.

design.md Section 3 (Path A) L1 layout:
  - 450 ROI -> 23x20 (=460) grid, pad last 10 cells with 0
  - time axis mean (Phase 1 baseline equivalent)
  - resize to 224x224
  - 3-channel broadcast
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F

ROI_N = 450
GRID_H, GRID_W = 23, 20
IMG_SIZE = 224


def roi_to_grid(roi_ts: np.ndarray) -> np.ndarray:
    """(T, 450) -> (23, 20) by time-mean + pad."""
    assert roi_ts.shape[-1] == ROI_N, f"expected 450 ROI, got {roi_ts.shape}"
    mean_roi = roi_ts.mean(axis=0)
    pad = GRID_H * GRID_W - ROI_N
    padded = np.concatenate([mean_roi, np.zeros(pad, dtype=mean_roi.dtype)])
    return padded.reshape(GRID_H, GRID_W)


def zscore_per_roi(roi_ts_all: np.ndarray) -> np.ndarray:
    """Per-ROI z-score across stim axis. roi_ts_all: (N_stim, T, 450) variable T per stim handled outside."""
    raise NotImplementedError("apply at fit-time on training fold only, use precomputed mean/std")


def grid_to_image(grid: np.ndarray) -> torch.Tensor:
    """(23, 20) -> (3, 224, 224) float32 tensor in [0, 1] approx after normalization."""
    t = torch.from_numpy(grid.astype(np.float32))[None, None]
    t = F.interpolate(t, size=(IMG_SIZE, IMG_SIZE), mode="bilinear", align_corners=False)
    t = t.squeeze(0).repeat(3, 1, 1)
    return t


def patchify_stim(roi_ts: np.ndarray) -> torch.Tensor:
    """End-to-end (T, 450) -> (3, 224, 224)."""
    return grid_to_image(roi_to_grid(roi_ts))
