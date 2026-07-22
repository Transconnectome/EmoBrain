"""Horikawa ROI loading with explicit short-window perturbations."""

from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset


EMOBRAIN_ROOT = Path(__file__).resolve().parents[3]
ROI_BASE = Path(
    "/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/time_series"
)
NORM_PARAMS = Path(
    "/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/normalization_params.npz"
)
CANONICAL_CSV = EMOBRAIN_ROOT / "project/shared/data/feelin_canonical_stimuli.csv"
N_ROIS = 450
NUM_FRAMES = 16


class HorikawaShortWindowDataset(Dataset):
    def __init__(self, subject, perturbation="mean", seed=0):
        if perturbation not in {"mean", "zero", "spatial_only", "time_shuffle"}:
            raise ValueError(f"Unknown perturbation: {perturbation}")
        self.subject = subject
        self.perturbation = perturbation
        self.seed = seed
        self.subject_dir = ROI_BASE / subject
        canonical = pd.read_csv(CANONICAL_CSV)
        self.stim_names = canonical["stimulus_name"].tolist()
        self.stim_nums = canonical["stimulus_num"].to_numpy()
        params = np.load(NORM_PARAMS)
        self.medians = params["medians"].astype(np.float32)
        self.iqrs = params["iqrs"].astype(np.float32)
        if self.medians.shape != (N_ROIS,) or self.iqrs.shape != (N_ROIS,):
            raise ValueError("Normalization parameters do not match 450 ROIs")

    def __len__(self):
        return len(self.stim_names)

    def _load(self, stimulus):
        directory = self.subject_dir / stimulus
        cortex = pd.read_csv(directory / "fMRI.Schaefer17n400p.csv.gz")
        subcortex = pd.read_csv(directory / "fMRI.Tian_Subcortex_S3_3T.csv.gz")
        cortex_cols = [name for name in cortex if name.startswith("T")]
        subcortex_cols = [name for name in subcortex if name.startswith("T")]
        n_time = min(len(cortex_cols), len(subcortex_cols))
        return np.concatenate(
            [
                cortex[cortex_cols[:n_time]].to_numpy(dtype=np.float32),
                subcortex[subcortex_cols[:n_time]].to_numpy(dtype=np.float32),
            ],
            axis=0,
        )

    def _prepare(self, values, index):
        original_time = values.shape[1]
        if self.perturbation == "spatial_only":
            values = np.repeat(values.mean(axis=1, keepdims=True), NUM_FRAMES, axis=1)
        elif original_time >= NUM_FRAMES:
            start = (original_time - NUM_FRAMES) // 2
            values = values[:, start : start + NUM_FRAMES]
            if self.perturbation == "time_shuffle":
                permutation = np.random.default_rng(self.seed + index).permutation(NUM_FRAMES)
                values = values[:, permutation]
        else:
            if self.perturbation == "time_shuffle":
                permutation = np.random.default_rng(self.seed + index).permutation(original_time)
                values = values[:, permutation]
            pad_length = NUM_FRAMES - original_time
            if self.perturbation in {"mean", "time_shuffle"}:
                pad_frame = values.mean(axis=1, keepdims=True)
            elif self.perturbation == "zero":
                pad_frame = np.zeros((N_ROIS, 1), dtype=np.float32)
            else:
                raise RuntimeError("Unhandled perturbation")
            values = np.concatenate(
                [values, np.repeat(pad_frame, pad_length, axis=1)], axis=1
            )
        values = (values - self.medians[:, None]) / (self.iqrs[:, None] + 1e-8)
        return values.astype(np.float32), original_time

    def __getitem__(self, index):
        values = self._load(self.stim_names[index])
        values, original_time = self._prepare(values, index)
        return {
            "fmri": torch.from_numpy(values).unsqueeze(0).unsqueeze(0),
            "stim_num": self.stim_nums[index],
            "original_T": original_time,
            "padding_ratio": max(0.0, (NUM_FRAMES - original_time) / NUM_FRAMES),
        }


def collate(batch):
    return {
        "fmri": torch.cat([item["fmri"] for item in batch], dim=0),
        "stim_num": np.asarray([item["stim_num"] for item in batch]),
        "original_T": np.asarray([item["original_T"] for item in batch]),
        "padding_ratio": np.asarray([item["padding_ratio"] for item in batch], dtype=np.float32),
    }
