"""E2. Brain foundation model.

Two brain foundation models, selectable by config.
    brain_jepa  ROI based (450 parcels), ViT-B, emb 768.
    swift       whole-brain volume (96^3), Swin4D, emb 768.
    (neurostorm is also whole-brain volume, available as a config alternative.)

Adapt axis, and the cost asymmetry that comes with it.
    frozen    the dataset serves the PRECOMPUTED embedding (BFMSource), so this
              encoder is a pass-through and only the projector trains. Cheap; this
              is the linear-probing arm and needs no model in the loop.
    lora/full FINE-TUNE. The actual foundation model must run in the training loop
              on its raw input (ROI timeseries for brain_jepa, MNI volumes for
              swift). That integration is the heavy path; the loader hook is here
              and raises until a specific fine-tune is wired, so a frozen config
              never silently pulls in the model.

Contract. forward(x) -> (B, 1, out_dim). In frozen mode x is the (B, emb_dim)
precomputed embedding; out_dim = emb_dim.
"""

from __future__ import annotations

from pathlib import Path

import torch.nn as nn

from project.code.brain_encoder.base import BrainEncoder
from project.code.brain_encoder.registry import register_encoder

REPO_ROOT = Path(__file__).resolve().parents[3]
# emb dim per family, used only to declare out_dim in frozen mode.
_EMB_DIM = {"brain_jepa": 768, "swift": 768, "neurostorm": 288}
_CKPT = {
    "brain_jepa": REPO_ROOT / "external/checkpoints/brain_jepa/jepa-ep300.pth",
    "neurostorm": REPO_ROOT / "external/checkpoints/neurostorm/pt_neurostorm_mae_ratio0.5.ckpt",
    # swift checkpoint is not in external/checkpoints (empty dir); wire when chosen.
}


@register_encoder("bfm")
class BFMEncoder(BrainEncoder):
    def __init__(self, model: str = "brain_jepa", emb_dim: int | None = None,
                 adapt: str = "frozen", lora: dict | None = None,
                 pretrained_ckpt: str | None = None):
        super().__init__(adapt=adapt, lora=lora)
        self.model_name = model
        if adapt == "frozen":
            self.out_dim = int(emb_dim or _EMB_DIM.get(model, 768))
            self._passthrough = nn.Identity()          # only the projector trains
        else:
            self._backbone = self._load_finetune(model, pretrained_ckpt)

    def _load_finetune(self, model: str, ckpt: str | None):
        ckpt = Path(ckpt) if ckpt else _CKPT.get(model)
        raise NotImplementedError(
            f"BFM fine-tune for {model!r} is the heavy in-loop path and is not "
            f"wired yet. Frozen mode (precomputed embedding) works now. To enable "
            f"fine-tune, integrate the {model} forward from external/ and set "
            f"out_dim; checkpoint = {ckpt}."
        )

    def _encode(self, x):                               # frozen: (B, emb_dim) -> (B,1,emb_dim)
        if x.dim() == 3:
            x = x.mean(dim=1)
        return self._passthrough(x).unsqueeze(1)
