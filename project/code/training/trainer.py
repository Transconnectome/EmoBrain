"""Config-driven trainer (spec §8-2). One loop for every encoder and modality.

Track A (direct supervised) runs now for any encoder x modality combination.
    student  modalities {brain} + question. The inference form.
    teacher  modalities {brain, video, caption}.
Track B (distillation) reuses this loop with a cached teacher soft label passed
as `teacher_pred`; the caching stage is a thin wrapper added on top and is not
required to run Track A.

Reuses the audited stage 1-3 modules unchanged (HorikawaDataset, Cowen34
normalizer via the dataset, profile_correlation). Swapping the model is a config
edit; this file never changes.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/trainer.sh <config.yaml>
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np  # noqa: E402
import torch  # noqa: E402
import yaml  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from project.data.datasets import HorikawaDataset  # noqa: E402
from project.evaluation.metrics import compute_metrics  # noqa: E402
from project.code.fusion.build import build_model  # noqa: E402
from project.code.losses import total_student_loss  # noqa: E402


def seed_all(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s)


def make_collate(video_npy):
    def collate(batch):
        out = {"fmri": torch.stack([torch.as_tensor(b["fmri"], dtype=torch.float32) for b in batch]),
               "label": torch.stack([torch.as_tensor(b["label"], dtype=torch.float32) for b in batch]),
               "stim_num": [int(b["stim_num"]) for b in batch],
               "subject": [b["subject_id"] for b in batch]}
        if "caption" in batch[0]:
            out["caption"] = [b["caption"] for b in batch]
        if video_npy is not None:
            out["video"] = torch.stack([torch.as_tensor(video_npy[int(b["stim_num"]) - 1],
                                                         dtype=torch.float32) for b in batch])
        return out
    return collate


def forward_batch(model, b, mods, device):
    kw = {}
    if mods.get("video"):
        kw["video"] = b["video"].to(device)
    if mods.get("caption"):
        kw["caption"] = b["caption"]
    return model(b["fmri"].to(device), **kw)


@torch.no_grad()
def evaluate(model, loader, mods, device, max_batches=None):
    model.eval()
    P, T = [], []
    for i, b in enumerate(loader):
        if max_batches and i >= max_batches:
            break
        P.append(forward_batch(model, b, mods, device).float().cpu().numpy())
        T.append(b["label"].numpy())
    m = compute_metrics(np.concatenate(P), np.concatenate(T), which=["profile"])
    return m["profile"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    cfg = yaml.safe_load(open(ap.parse_args().config))
    tr = cfg["train"]
    seed_all(int(tr.get("seed", 0)))
    device = tr.get("device", "cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    model = build_model(cfg).to(device)
    ntr = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[cfg] enc={cfg['encoder']['type']} adapt={cfg['encoder'].get('adapt')} "
          f"bb={cfg.get('backbone', {}).get('type', 'stub')} device={device} trainable={ntr:,}")

    mods = cfg.get("modalities", {"brain": True})
    data = cfg.get("data", {})
    brain_source = data.get("brain_source", "roi_mean")
    cap_mode = "human" if mods.get("caption") else "off"
    train_ds = HorikawaDataset(split="train", fmri_mode="mean",
                               brain_source=brain_source, caption_mode=cap_mode)
    val_ds = HorikawaDataset(split="val", fmri_mode="mean",
                             brain_source=brain_source, caption_mode=cap_mode)
    test_ds = HorikawaDataset(split="test", fmri_mode="mean",
                              brain_source=brain_source, caption_mode=cap_mode)
    video_npy = np.load(REPO_ROOT / cfg["video"]["path"]) if mods.get("video") else None
    collate = make_collate(video_npy)
    tl = DataLoader(train_ds, batch_size=int(tr["batch_size"]), shuffle=True, collate_fn=collate)
    vl = DataLoader(val_ds, batch_size=int(tr["batch_size"]), shuffle=False, collate_fn=collate)
    tel = DataLoader(test_ds, batch_size=int(tr["batch_size"]), shuffle=False, collate_fn=collate)
    print(f"[data] train {len(train_ds)} val {len(val_ds)} brain_source={brain_source}")

    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                            lr=float(tr["lr"]), weight_decay=float(tr.get("weight_decay", 0.01)))
    lam = cfg.get("loss", {})
    max_tb = tr.get("max_train_batches")
    hist = []
    best_v, best_state = -float("inf"), None
    for epoch in range(int(tr["epochs"])):
        model.train(); train_ds.set_epoch(epoch)
        run, nb = 0.0, 0
        for i, b in enumerate(tl):
            if max_tb and i >= max_tb:
                break
            pred = forward_batch(model, b, mods, device)
            loss = total_student_loss(pred, b["label"].to(device),
                                      lambda_hard=lam.get("lambda_hard", 1.0),
                                      lambda_dist=0.0,
                                      hard_kind=lam.get("hard_kind", "mse"),
                                      ccc_weight=lam.get("ccc_weight", 1.0))
            opt.zero_grad(); loss.backward(); opt.step()
            run += loss.item(); nb += 1
        prof = evaluate(model, vl, mods, device, tr.get("max_eval_batches"))
        print(f"[epoch {epoch}] train_loss={run/max(nb,1):.4f} | "
              f"val pearson={prof['pearson_mean']:+.4f} ccc={prof['ccc_mean']:+.4f}")
        hist.append({"epoch": epoch, "train_loss": run / max(nb, 1),
                     "val_pearson": prof["pearson_mean"], "val_ccc": prof["ccc_mean"]})
        if prof["pearson_mean"] > best_v:
            best_v = prof["pearson_mean"]
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state is None:
        raise RuntimeError("training produced no checkpoint")
    model.load_state_dict(best_state)
    test_profile = evaluate(model, tel, mods, device, tr.get("max_eval_batches"))

    out = REPO_ROOT / tr.get("out_json", "project/output/run.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    ckpt = REPO_ROOT / tr.get(
        "checkpoint", f"project/output/checkpoints/{out.stem}.pt"
    )
    ckpt.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": best_state, "config": cfg, "val_pearson": best_v,
                "test_profile": test_profile}, ckpt)
    out.write_text(json.dumps({"config": cfg, "history": hist,
                               "best_val_pearson": best_v,
                               "test_profile": test_profile,
                               "checkpoint": str(ckpt)}, indent=2))
    if hist:
        best = max(hist, key=lambda h: h["val_pearson"])
        print(f"[done] best epoch {best['epoch']} pearson {best['val_pearson']:+.4f} "
              f"test={test_profile['pearson_mean']:+.4f} -> {out}")


if __name__ == "__main__":
    main()
