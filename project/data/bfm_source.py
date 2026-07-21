"""BFM (frozen brain foundation model) embedding source.

Serves precomputed FROZEN embeddings (SwiFT / Brain-JEPA / NeuroSTORM) as the
brain input, mirroring FmriAdapter.get so HorikawaDataset can swap ROI mean for
any BFM variant by name (data config brain_source). This is the E3 encoder path:
the "encoder" is the frozen foundation model, so only the downstream projector
trains (identity encoder).

Layout. project/shared/output/embeddings/<variant>/sub-XX.pt, each a dict with
    embeddings : (2185, dim) float   already deduped to the 2185 canonical stimuli
    stim_num   : (2185,)             stimulus number per row (for alignment)
Available variants (Phase 1): 20 swift, 8 brain_jepa, 6 neurostorm, 1 roi.
dim = 288 / 768 / 1536 depending on the model.
"""
from __future__ import annotations

from pathlib import Path

import torch

from project.data.fmri_adapter import SUBJECTS

DEFAULT_EMB_ROOT = Path(__file__).resolve().parents[2] / "project/shared/output/embeddings"


class BFMSource:
    """Frozen BFM embeddings, indexed by (subject, stim_num). get() mirrors
    FmriAdapter.get so the dataset can use either interchangeably."""

    def __init__(self, variant: str, root: str | Path = DEFAULT_EMB_ROOT):
        root = Path(root)
        self.variant = variant
        self._emb: dict[str, torch.Tensor] = {}
        self._stim_index: dict[str, dict[int, int]] = {}
        for subj in SUBJECTS:
            path = root / variant / f"{subj}.pt"
            d = torch.load(path, map_location="cpu", weights_only=False)
            self._emb[subj] = d["embeddings"].float()          # (2185, dim)
            self._stim_index[subj] = {
                int(s): i for i, s in enumerate(d["stim_num"].tolist())
            }
        self.dim = int(next(iter(self._emb.values())).shape[1])

    def get(self, subject_id: str, stim_num: int, mode: str = "mean"):
        # mode ignored: a BFM embedding is one frozen vector per stimulus.
        assert subject_id in self._emb, f"unknown subject {subject_id}"
        row = self._stim_index[subject_id][stim_num]
        return self._emb[subject_id][row]                       # (dim,)
