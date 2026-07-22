"""Stimulus caption mapping.

Sources.
    project/shared/data/caption_ck20.csv
        MindCaptioning Cowen-Keltner 2020 human descriptive caption.
        43920 rows = 2196 video × 20 raters. video_id 1-based, matches our
        stim_num (both index Cowen source filenames 0001.mp4 .. 2196.mp4).
        These captions describe visual content but are not assumed to be
        affect-neutral; emotion terms are allowed and must be controlled
        empirically in downstream analyses.

    project/shared/data/stimulus_features/captions.json  (SKIPPED for now)
        Our Qwen-VL generated caption. Verified inaccurate on several checked
        stimuli (e.g., stim 457 has guns but Qwen described seashells).
        Not usable until regenerated / verified in a separate cycle.

Rater policy (option 3).
    Training split.   rater index = f(stim_num, epoch, base_seed).
                      Varies per epoch (augmentation) but fully reproducible.
    Val / test split. rater index = f(stim_num, base_seed) only.
                      Deterministic per stim, independent of epoch.

Both selections use a stable hash of (stim, epoch, seed) so no rng state leaks
between processes. rater_idx in [0, 19].

Usage.
    from project.data.caption_map import CaptionMap

    cm = CaptionMap()
    cm.get(stim_num=3, split="train", epoch=0)     # deterministic per epoch
    cm.get(stim_num=3, split="val")                # fixed regardless of epoch
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HUMAN_CSV = REPO_ROOT / "project" / "shared" / "data" / "caption_ck20.csv"

RATERS_PER_STIM = 20
DEFAULT_BASE_SEED = 42

Split = Literal["train", "val", "test"]


def _rater_idx(stim_num: int, epoch: int | None, base_seed: int, split: Split) -> int:
    """Stable deterministic rater index in [0, RATERS_PER_STIM).

    Training uses epoch as an additional dimension so the rater varies across
    epochs while remaining reproducible. Val / test ignore epoch so the choice
    is fixed regardless of when it is called.
    """
    if split == "train":
        assert epoch is not None, "epoch must be provided for split='train'"
        key = (base_seed, stim_num, epoch)
    else:
        key = (base_seed, stim_num)
    return hash(key) % RATERS_PER_STIM


class CaptionMap:
    """Map stim_num -> caption string with a rater selection policy.

    Args.
        human_csv    Path to caption_ck20.csv.
        base_seed    Seed for deterministic rater selection.
    """

    def __init__(self, human_csv: str | Path = DEFAULT_HUMAN_CSV, base_seed: int = DEFAULT_BASE_SEED):
        self.base_seed = int(base_seed)
        df = pd.read_csv(human_csv)
        assert list(df.columns) == ["video_id", "description"], (
            f"unexpected caption CSV schema: {list(df.columns)}"
        )
        # group by video_id -> ordered list of 20 rater descriptions.
        # Preserve original file order to keep rater_idx reproducible.
        self._by_stim: dict[int, list[str]] = {}
        for stim_num, sub in df.groupby("video_id", sort=True):
            captions = sub["description"].tolist()
            assert len(captions) == RATERS_PER_STIM, (
                f"stim {stim_num}: got {len(captions)} raters, expected {RATERS_PER_STIM}"
            )
            self._by_stim[int(stim_num)] = captions

    def num_stims(self) -> int:
        return len(self._by_stim)

    def covers(self, stim_num: int) -> bool:
        return int(stim_num) in self._by_stim

    def get(self, stim_num: int, split: Split, epoch: int | None = None) -> str:
        """Return caption string for one stim under the rater policy.

        Args.
            stim_num  1-based canonical stimulus number.
            split     "train" -> epoch-varied random rater.
                      "val" / "test" -> fixed rater (epoch ignored).
            epoch     current training epoch. Required if split="train".
        """
        assert self.covers(stim_num), f"stim {stim_num} not in caption map"
        idx = _rater_idx(int(stim_num), epoch, self.base_seed, split)
        return self._by_stim[int(stim_num)][idx]

    def all_captions(self, stim_num: int) -> list[str]:
        """Return all 20 rater captions for one stim (for inspection)."""
        assert self.covers(stim_num), f"stim {stim_num} not in caption map"
        return list(self._by_stim[int(stim_num)])
