"""Horikawa 2020 dataset (pooled 5-subject × 2185-stimulus).

Implementation of `docs/notes/implementation_spec_20260702.md` §5-1, §5-3.

Pooled sample convention.
    Each (subject, stimulus) pair is one sample. Label is stimulus-level
    (subject-invariant), fMRI is subject-specific.

    train  = 5 subj × 1748 train stim = 8740 samples
    val    = 5 subj × 217  val   stim = 1085 samples
    test   = 5 subj × 220  test  stim = 1100 samples

Label pipeline.
    Raw 34D scores from cowen_horikawa_labels.csv are z-scored once at load
    time using the fitted Cowen34Normalizer. Test / val statistics are never
    used to fit.

fMRI pipeline.
    Actual ROI values loaded via FmriAdapter (project/data/fmri_adapter.py).
    Two modes.
        fmri_mode="mean"        -> sample["fmri"] shape (450,)
        fmri_mode="timeseries"  -> sample["fmri"] shape (T_max, 450)
                                   sample["mask"] shape (T_max,) bool
                                   sample["original_T"] int

Downstream models MUST honor the mask when mode="timeseries". Padding zeros
must not leak into computations.

Usage.
    from project.data.datasets import HorikawaDataset

    train = HorikawaDataset(split="train", fmri_mode="mean")
    train[0]        # dict(subject_id, stim_num, label (34,), fmri (450,))

    train_ts = HorikawaDataset(split="train", fmri_mode="timeseries")
    train_ts[0]     # + mask (T_max,), + original_T
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from project.data.labels import Cowen34Normalizer
from project.data.fmri_adapter import FmriAdapter
from project.data.caption_map import CaptionMap


C = 34
N_ROI = 450

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "project" / "shared" / "data"

DEFAULT_LABELS_CSV = DATA_DIR / "cowen_horikawa_labels.csv"
DEFAULT_SPLIT_CSV = DATA_DIR / "horikawa_split.csv"
DEFAULT_NORM_STATS = DATA_DIR / "norm_stats" / "cowen34_train.pt"

SCORE_COLS = [f"score_{k}" for k in range(C)]

Split = Literal["train", "val", "test"]
FmriMode = Literal["mean", "timeseries"]
CaptionMode = Literal["off", "human"]


@dataclass(frozen=True)
class _Sample:
    subject_id: str
    stim_idx: int
    stim_num: int


class HorikawaDataset(Dataset):
    """Pooled 5-subject Horikawa fMRI dataset.

    Args.
        split          "train" | "val" | "test".
        fmri_mode      "mean" or "timeseries".
        labels_csv     Cowen 34D scores per stimulus.
        split_csv      (subject, stimulus_num, split) rows.
        norm_stats     Path to Cowen34Normalizer save file.
        fmri_adapter   Optional pre-loaded FmriAdapter (shared across splits).
    """

    def __init__(
        self,
        split: Split,
        fmri_mode: FmriMode = "mean",
        caption_mode: CaptionMode = "off",
        labels_csv: str | Path = DEFAULT_LABELS_CSV,
        split_csv: str | Path = DEFAULT_SPLIT_CSV,
        norm_stats: str | Path = DEFAULT_NORM_STATS,
        fmri_adapter: FmriAdapter | None = None,
        caption_map: CaptionMap | None = None,
    ):
        assert split in ("train", "val", "test"), f"unknown split: {split}"
        assert fmri_mode in ("mean", "timeseries"), f"unknown fmri_mode: {fmri_mode}"
        assert caption_mode in ("off", "human"), f"unknown caption_mode: {caption_mode}"
        self.split = split
        self.fmri_mode = fmri_mode
        self.caption_mode = caption_mode
        self._epoch: int = 0

        labels_df = pd.read_csv(labels_csv)
        split_df = pd.read_csv(split_csv)

        rows = split_df.loc[split_df["split"] == split].reset_index(drop=True)
        self._samples: list[_Sample] = [
            _Sample(subject_id=r["subject"], stim_idx=int(r["stimulus_num"]) - 1, stim_num=int(r["stimulus_num"]))
            for _, r in rows.iterrows()
        ]

        stim_to_row = labels_df.set_index("stim_num_int")
        raw_labels = np.stack(
            [stim_to_row.loc[s.stim_num, SCORE_COLS].values.astype(np.float32) for s in self._samples],
            axis=0,
        )
        self._label_z = Cowen34Normalizer.load(norm_stats).transform(raw_labels)
        assert self._label_z.shape == (len(self._samples), C)

        self._fmri = fmri_adapter if fmri_adapter is not None else FmriAdapter()

        if self.caption_mode == "off":
            self._captions: CaptionMap | None = None
        else:
            self._captions = caption_map if caption_map is not None else CaptionMap()

    def set_epoch(self, epoch: int) -> None:
        """Trainer must call this at the start of every epoch (rater rotation)."""
        assert epoch >= 0
        self._epoch = int(epoch)

    def __len__(self) -> int:
        return len(self._samples)

    def __getitem__(self, idx: int) -> dict:
        s = self._samples[idx]
        item: dict = {
            "subject_id": s.subject_id,
            "stim_idx": s.stim_idx,
            "stim_num": s.stim_num,
            "label": self._label_z[idx],
        }
        if self.fmri_mode == "mean":
            item["fmri"] = self._fmri.get(s.subject_id, s.stim_num, mode="mean")
        else:  # timeseries
            ts, mask = self._fmri.get(s.subject_id, s.stim_num, mode="timeseries")
            item["fmri"] = ts
            item["mask"] = mask
            item["original_T"] = self._fmri.original_T(s.subject_id, s.stim_num)

        if self._captions is not None:
            item["caption"] = self._captions.get(
                s.stim_num,
                split=self.split,
                epoch=self._epoch if self.split == "train" else None,
            )
        return item
