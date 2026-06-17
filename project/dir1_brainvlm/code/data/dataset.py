"""BrainVQADataset for Path A pilot.

Returns per-stim dict:
  image:    (3, 224, 224)            patchified fMRI
  va:       (2,) float32             V/A continuous (standardized)
  cat34:    (34,) float32            soft distribution (sum to 1)
  caption:  str                      Qwen-VL caption of stimulus video
  prompt:   str                      instruction template
  stim_id:  str
  subject:  int
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from .patchify import patchify_stim

PROMPT = (
    "You are an expert in affective neuroscience. Based on the fMRI activity "
    "pattern, predict the emotional response.\n"
    "Question: What is the valence, arousal, and emotion distribution?"
)


class BrainVQADataset(Dataset):
    def __init__(
        self,
        manifest_csv: str,
        roi_dir: str,
        caption_jsonl: str,
        va_targets_csv: str,
        cat34_targets_csv: str,
        fold: int,
        split: str,
    ):
        self.manifest = pd.read_csv(manifest_csv)
        self.manifest = self.manifest[self.manifest[f"fold{fold}_split"] == split].reset_index(drop=True)
        self.roi_dir = Path(roi_dir)
        self.captions = self._load_captions(caption_jsonl)
        self.va = pd.read_csv(va_targets_csv).set_index("stim_id")
        self.cat34 = pd.read_csv(cat34_targets_csv).set_index("stim_id")

    @staticmethod
    def _load_captions(path: str) -> dict:
        d = {}
        with open(path) as f:
            for line in f:
                obj = json.loads(line)
                d[obj["stim_id"]] = obj["caption"]
        return d

    def __len__(self) -> int:
        return len(self.manifest)

    def __getitem__(self, idx: int) -> dict:
        row = self.manifest.iloc[idx]
        stim_id, subject = row["stim_id"], int(row["subject"])
        roi_ts = np.load(self.roi_dir / f"sub-{subject:02d}_{stim_id}.npy")
        image = patchify_stim(roi_ts)
        va = self.va.loc[stim_id, ["valence_z", "arousal_z"]].to_numpy(dtype=np.float32)
        cat34 = self.cat34.loc[stim_id].to_numpy(dtype=np.float32)
        cat34 = cat34 / max(cat34.sum(), 1e-8)
        return {
            "image": image,
            "va": torch.from_numpy(va),
            "cat34": torch.from_numpy(cat34),
            "caption": self.captions.get(stim_id, ""),
            "prompt": PROMPT,
            "stim_id": stim_id,
            "subject": subject,
        }
