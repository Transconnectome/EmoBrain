"""Data <-> model wiring smoke. REAL Horikawa batch -> stub model -> loss.

Verifies.
    - HorikawaDataset (mean) + make_collate produce a model-ready batch
      (fmri [B,450], text_ids [B,L], label [B,34]) from real data.
    - build_model(stub cfg) forward on a REAL batch returns [B, 34], finite.
    - supervised_loss(pred, label) is a finite positive scalar.
    - student form (brain + question) runs end to end. Random weights, NO
      training. This validates the pipe from disk to loss, not accuracy.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/data_model_smoke.sh
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402
import yaml  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from project.data.datasets import HorikawaDataset  # noqa: E402
from project.models.build import build_model  # noqa: E402
from project.models.losses.supervised import supervised_loss  # noqa: E402
from project.models.prompt import TRACK_A_QUESTION  # noqa: E402
from project.training.collate import make_collate  # noqa: E402


def main():
    cfg = yaml.safe_load(
        open(REPO_ROOT / "project/configs/smoke_e1_stub.yaml")
    )
    model = build_model(cfg)
    model.eval()

    ds = HorikawaDataset(split="val", fmri_mode="mean")
    print(f"val dataset          : {len(ds)} samples (subject x stim pooled)")
    print(f"fixed Question chars  : {len(TRACK_A_QUESTION)}")

    collate = make_collate(TRACK_A_QUESTION, model.backbone)
    loader = DataLoader(ds, batch_size=8, shuffle=False, collate_fn=collate)
    batch = next(iter(loader))

    print(
        f"batch                : fmri={tuple(batch['fmri'].shape)} "
        f"label={tuple(batch['label'].shape)} "
        f"text_ids={tuple(batch['text_ids'].shape)}"
    )
    print(
        f"sample meta          : subj={batch['subject_id'][:3]} "
        f"stim={batch['stim_num'][:3]}"
    )

    with torch.no_grad():
        pred = model(
            fmri=batch["fmri"],
            text_ids=batch["text_ids"],
            text_mask=batch["text_mask"],
        )
    loss = supervised_loss(pred, batch["label"])

    print(
        f"forward              : pred={tuple(pred.shape)} "
        f"finite={bool(torch.isfinite(pred).all())} "
        f"loss={loss.item():.4f} (34-emotion MSE, z-space)"
    )
    assert pred.shape == (8, 34), pred.shape
    assert torch.isfinite(loss) and loss.item() > 0
    print("\nDATA-MODEL SMOKE OK")


if __name__ == "__main__":
    main()
