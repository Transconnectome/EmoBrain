"""Track B, step 1. Train the teacher and save it (spec §8.6.1).

Teacher = brain + video + caption + question, trained on the 34D labels with the
same per-emotion loss as Track A. On convergence its weights are frozen and
saved so step 2 can cache soft labels without re-training.

This is deliberately a thin wrapper over the shared trainer loop; only the
modality set (video + caption on) and the checkpoint save differ. The student
inference form is never used here.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/train_teacher.sh <teacher_config.yaml>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np  # noqa: E402
import torch  # noqa: E402
import yaml  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from project.data.datasets import HorikawaDataset  # noqa: E402
from project.code.fusion.build import build_model  # noqa: E402
from project.code.losses import total_student_loss  # noqa: E402
from project.code.training.trainer import (  # noqa: E402
    seed_all, make_collate, forward_batch, evaluate)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    cfg = yaml.safe_load(open(ap.parse_args().config))
    tr = cfg["train"]
    seed_all(int(tr.get("seed", 0)))
    device = tr.get("device", "cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    mods = cfg.get("modalities", {"brain": True, "video": True, "caption": True})
    assert mods.get("video") or mods.get("caption"), \
        "teacher must have video and/or caption; use train_student for brain-only"

    model = build_model(cfg).to(device)
    print(f"[teacher] enc={cfg['encoder']['type']} modalities={mods} device={device} "
          f"trainable={sum(p.numel() for p in model.parameters() if p.requires_grad):,}")

    data = cfg.get("data", {})
    train_ds = HorikawaDataset(split="train", fmri_mode="mean",
                               brain_source=data.get("brain_source", "roi_mean"),
                               caption_mode="human" if mods.get("caption") else "off")
    val_ds = HorikawaDataset(split="val", fmri_mode="mean",
                             brain_source=data.get("brain_source", "roi_mean"),
                             caption_mode="human" if mods.get("caption") else "off")
    test_ds = HorikawaDataset(split="test", fmri_mode="mean",
                              brain_source=data.get("brain_source", "roi_mean"),
                              caption_mode="human" if mods.get("caption") else "off")
    video_npy = np.load(REPO_ROOT / cfg["video"]["path"]) if mods.get("video") else None
    collate = make_collate(video_npy)
    tl = DataLoader(train_ds, batch_size=int(tr["batch_size"]), shuffle=True, collate_fn=collate)
    vl = DataLoader(val_ds, batch_size=int(tr["batch_size"]), shuffle=False, collate_fn=collate)
    tel = DataLoader(test_ds, batch_size=int(tr["batch_size"]), shuffle=False, collate_fn=collate)

    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                            lr=float(tr["lr"]), weight_decay=float(tr.get("weight_decay", 0.01)))
    lam = cfg.get("loss", {})
    max_tb = tr.get("max_train_batches")
    best_v, best_state = -1e9, None
    for epoch in range(int(tr["epochs"])):
        model.train(); train_ds.set_epoch(epoch)
        run, nb = 0.0, 0
        for i, b in enumerate(tl):
            if max_tb and i >= max_tb:
                break
            pred = forward_batch(model, b, mods, device)
            loss = total_student_loss(pred, b["label"].to(device),
                                      lambda_hard=lam.get("lambda_hard", 1.0), lambda_dist=0.0,
                                      hard_kind=lam.get("hard_kind", "mse"),
                                      ccc_weight=lam.get("ccc_weight", 1.0))
            opt.zero_grad(); loss.backward(); opt.step()
            run += loss.item(); nb += 1
        prof = evaluate(model, vl, mods, device, tr.get("max_eval_batches"))
        print(f"[teacher e{epoch}] loss={run/max(nb,1):.4f} val pearson={prof['pearson_mean']:+.4f}")
        if prof["pearson_mean"] > best_v:
            best_v = prof["pearson_mean"]
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    ckpt = REPO_ROOT / tr.get("teacher_ckpt", "project/output/checkpoints/teacher.pt")
    ckpt.parent.mkdir(parents=True, exist_ok=True)
    model.load_state_dict(best_state)
    test_profile = evaluate(model, tel, mods, device, tr.get("max_eval_batches"))
    torch.save({"state_dict": best_state, "config": cfg, "val_pearson": best_v,
                "test_profile": test_profile}, ckpt)
    result = REPO_ROOT / tr.get(
        "out_json", "project/output/e2_brain_jepa_teacher_qwen3vl4b.json"
    )
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_text(json.dumps({"config": cfg, "best_val_pearson": best_v,
                                  "test_profile": test_profile,
                                  "checkpoint": str(ckpt)}, indent=2))
    print(f"[teacher] best val={best_v:+.4f} "
          f"test={test_profile['pearson_mean']:+.4f} -> {ckpt}")


if __name__ == "__main__":
    main()
