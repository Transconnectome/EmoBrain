"""BrainVideoDataset.

Pairs frozen brain embeddings (5 subj x 2185 stim x 768) with the per-stim
V-JEPA2 video feature (2185 x 1408). One sample = (brain vector, video vector,
stim_num, subj_idx). Same stim is paired with the same video across all
subjects, so the same video co-occurs 5 times within a fold.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset


SHARED = Path("/pscratch/sd/s/sjmoon/EmoBrain/project/shared")
EMB_ROOT = SHARED / "output/embeddings"
DATA_ROOT = SHARED / "data"

BRAIN_VARIANTS = {
    "resting": EMB_ROOT / "brain_jepa_resting_pad-zero",
    "scratch": EMB_ROOT / "brain_jepa_scratch_pad-zero",
}
VIDEO_PATH = DATA_ROOT / "stimulus_features/vjepa2_pretrained.npy"
FOLD_CSV = DATA_ROOT / "horikawa_5fold.csv"

SUBJECTS = ["sub-01", "sub-02", "sub-03", "sub-04", "sub-05"]


class BrainVideoDataset(Dataset):
    """Stim-paired brain + video dataset.

    Parameters
    ----------
    brain_variant : {"resting", "scratch"}
        Which Brain-JEPA frozen embedding to use.
    split : {"train", "val", "test"}
        Which fold subset.
    test_fold : int in 1..5
        The fold used as test. val = (test_fold % 5) + 1, train = rest.
    subjects : optional list of subject ids; defaults to all 5.
    """

    def __init__(
        self,
        brain_variant: str = "resting",
        split: str = "train",
        test_fold: int = 1,
        subjects: List[str] | None = None,
    ) -> None:
        if brain_variant not in BRAIN_VARIANTS:
            raise ValueError(f"unknown brain_variant {brain_variant}")
        if split not in {"train", "val", "test"}:
            raise ValueError(f"unknown split {split}")
        if test_fold not in {1, 2, 3, 4, 5}:
            raise ValueError(f"unknown test_fold {test_fold}")

        self.brain_variant = brain_variant
        self.split = split
        self.test_fold = test_fold
        self.subjects = subjects or SUBJECTS

        val_fold = (test_fold % 5) + 1
        fold_df = pd.read_csv(FOLD_CSV)
        if split == "train":
            stim_nums = fold_df[~fold_df["fold"].isin([test_fold, val_fold])]["stimulus_num"].tolist()
        elif split == "val":
            stim_nums = fold_df[fold_df["fold"] == val_fold]["stimulus_num"].tolist()
        else:
            stim_nums = fold_df[fold_df["fold"] == test_fold]["stimulus_num"].tolist()
        self.stim_nums = sorted(stim_nums)

        # Load all brain embeddings (5 subj x 2185 stim x 768) keyed by stim_num.
        brain_dir = BRAIN_VARIANTS[brain_variant]
        self.brain_by_subj: dict[str, np.ndarray] = {}
        self.stim_to_row: dict[int, int] | None = None
        for subj in self.subjects:
            payload = torch.load(brain_dir / f"{subj}.pt", map_location="cpu", weights_only=False)
            emb = payload["embeddings"].numpy().astype(np.float32)  # (2185, 768)
            stim = payload["stim_num"].numpy().astype(np.int64)
            if self.stim_to_row is None:
                self.stim_to_row = {int(s): i for i, s in enumerate(stim)}
            self.brain_by_subj[subj] = emb

        # Video features keyed by stim_num. The npy file is row i = stim_num (i+1) per
        # the Phase 1 audit (1B).
        video = np.load(VIDEO_PATH).astype(np.float32)  # (2185, 1408)
        # Row 0 corresponds to stim_num 1, etc.
        self.video = video

        # Build the (subj_idx, stim_num) sample index.
        self.samples: list[tuple[int, int]] = []
        for s_i, subj in enumerate(self.subjects):
            for stim in self.stim_nums:
                self.samples.append((s_i, stim))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        subj_idx, stim_num = self.samples[idx]
        subj = self.subjects[subj_idx]
        row = self.stim_to_row[stim_num]
        brain = torch.from_numpy(self.brain_by_subj[subj][row])  # (768,)
        video = torch.from_numpy(self.video[stim_num - 1])  # (1408,)
        return {
            "brain": brain,
            "video": video,
            "stim_num": torch.tensor(stim_num, dtype=torch.long),
            "subj_idx": torch.tensor(subj_idx, dtype=torch.long),
        }
