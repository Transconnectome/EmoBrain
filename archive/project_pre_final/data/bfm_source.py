"""BFM (frozen brain foundation model) embedding source.

Serves precomputed FROZEN embeddings (SwiFT / Brain-JEPA / NeuroSTORM) as the
brain input, mirroring FmriAdapter.get so HorikawaDataset can swap ROI mean for
any BFM variant by name (data config brain_source). This is the E2 encoder path:
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
            if not path.exists():
                hint = ""
                if variant == "brain_jepa_pretrained_native_mean":
                    hint = (
                        " Run: bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/"
                        "import_corrected_brain_jepa.sh"
                    )
                raise FileNotFoundError(f"missing BFM embedding {path}.{hint}")
            d = torch.load(path, map_location="cpu", weights_only=False)
            if variant == "brain_jepa_pretrained_native_mean":
                prov = d.get("provenance")
                if prov is None:
                    raise ValueError(f"corrected Brain-JEPA file lacks provenance: {path}")
                expected = {
                    "initialization": "pretrained",
                    "position_policy": "native",
                    "input_perturbation": "mean",
                    "n_stimuli": 2185,
                }
                bad = {k: (prov.get(k), v) for k, v in expected.items() if prov.get(k) != v}
                if bad:
                    raise ValueError(f"invalid corrected Brain-JEPA provenance in {path}: {bad}")
            embeddings = d["embeddings"].float()
            stim_num = d["stim_num"]
            if embeddings.ndim != 2 or embeddings.shape[0] != 2185:
                raise ValueError(f"unexpected BFM shape in {path}: {tuple(embeddings.shape)}")
            if sorted(int(s) for s in stim_num.tolist()) != list(range(1, 2186)):
                raise ValueError(f"stimulus IDs in {path} are not exactly 1..2185")
            self._emb[subj] = embeddings
            self._stim_index[subj] = {
                int(s): i for i, s in enumerate(stim_num.tolist())
            }
        self.dim = int(next(iter(self._emb.values())).shape[1])

    def get(self, subject_id: str, stim_num: int, mode: str = "mean"):
        # mode ignored: a BFM embedding is one frozen vector per stimulus.
        assert subject_id in self._emb, f"unknown subject {subject_id}"
        row = self._stim_index[subject_id][stim_num]
        return self._emb[subject_id][row]                       # (dim,)
