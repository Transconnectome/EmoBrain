"""fMRI adapter. Load ROI time-series pt per subject and serve per-sample fMRI.

Sources one file per subject.
    project/shared/data/roi_timeseries/sub-XX.pt

Per pt content (built by scripts/build_roi_timeseries.py).
    roi_timeseries  (2185, T_max=47, 450)  float32   right zero-padded
    roi_mean        (2185, 450)            float32   time-mean using mask
    mask            (2185, T_max)          bool      True = valid, False = pad
    original_T      (2185,)                int32     valid T per stim
    stim_num        (2185,)                int32     1-based canonical stim id

Modes.
    "mean"        return (450,) tensor. No mask (all valid).
    "timeseries"  return (T_max, 450) tensor + (T_max,) bool mask.
                  Downstream models MUST honor mask (attention or masked mean).

Padding invariance CAUTION.
    Padding positions carry zeros; downstream code must attention-mask them.
    Test suggested. Replace pad values with noise; masked outputs must be
    identical to the zero-padded ones.

Usage.
    from project.data.fmri_adapter import FmriAdapter

    adapter = FmriAdapter()
    x = adapter.get("sub-01", stim_num=3, mode="mean")       # (450,)
    ts, mask = adapter.get("sub-01", stim_num=3, mode="timeseries")   # (T_max, 450), (T_max,)
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import torch


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO_ROOT / "project" / "shared" / "data" / "roi_timeseries"

SUBJECTS = ("sub-01", "sub-02", "sub-03", "sub-04", "sub-05")
Mode = Literal["mean", "timeseries"]


class FmriAdapter:
    """In-memory adapter for pooled 5-subject ROI fMRI.

    Args.
        root  directory holding sub-XX.pt files (default = project/shared/data/roi_timeseries/).
    """

    def __init__(self, root: str | Path = DEFAULT_ROOT):
        self.root = Path(root)
        self._data: dict[str, dict] = {}
        self._stim_index: dict[str, dict[int, int]] = {}
        for subj in SUBJECTS:
            p = self.root / f"{subj}.pt"
            assert p.exists(), f"missing {p}"
            d = torch.load(p, map_location="cpu", weights_only=True)
            self._data[subj] = d
            self._stim_index[subj] = {int(s): i for i, s in enumerate(d["stim_num"].tolist())}
        self.T_max = int(self._data[SUBJECTS[0]]["T_max"])
        self.n_roi = int(self._data[SUBJECTS[0]]["n_roi"])

    def get(self, subject_id: str, stim_num: int, mode: Mode = "mean"):
        """Return fMRI for one (subject, stim) pair.

        Args.
            subject_id  "sub-01" .. "sub-05".
            stim_num    1-based canonical stimulus number.
            mode        "mean" or "timeseries".

        Returns.
            mode="mean"        Tensor (450,)
            mode="timeseries"  Tensor (T_max, 450), Tensor (T_max,) bool mask
        """
        assert subject_id in self._data, f"unknown subject {subject_id}"
        idx_map = self._stim_index[subject_id]
        assert stim_num in idx_map, f"stim_num {stim_num} not in {subject_id}"
        row = idx_map[stim_num]
        d = self._data[subject_id]
        if mode == "mean":
            return d["roi_mean"][row]  # (450,)
        if mode == "timeseries":
            return d["roi_timeseries"][row], d["mask"][row]  # (T_max, 450), (T_max,)
        raise ValueError(f"unknown mode {mode!r}")

    def original_T(self, subject_id: str, stim_num: int) -> int:
        row = self._stim_index[subject_id][stim_num]
        return int(self._data[subject_id]["original_T"][row])
