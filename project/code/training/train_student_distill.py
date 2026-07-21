"""Track B, step 3. Train the brain-only student with distillation (spec §8.6.1).

Student input = brain + question only (the inference form; final eval must use
this, spec §14). Loss = L_main (per-emotion MSE on the z-scored label) + lambda *
L_distill (per-emotion MSE on the cached teacher 34D). Teacher soft labels come
from step 2's cache keyed by (subject, stim), so the teacher never runs here.

The headline this enables is context lift = student-with-distillation minus the
Track A direct student, both brain-only. Positive, null or negative are all
reportable (spec §8.9.3), and the distillation checks (variance partitioning,
brain-ablated student) decide whether any lift is real brain use or video
leakage (spec §8.9.2).

Run.
    bash .../train_student_distill.sh <student_config.yaml>
    (config points at data.soft_labels for the cache and train.teacher_tag)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402
import yaml  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from project.data.datasets import HorikawaDataset  # noqa: E402
from project.code.fusion.build import build_model  # noqa: E402
from project.code.losses import total_student_loss  # noqa: E402
from project.code.training.trainer import (  # noqa: E402
    seed_all, make_collate, forward_batch, evaluate)
from project.code.training.cache_soft_labels import key  # noqa: E402


def load_soft(path):
    d = torch.load(REPO_ROOT / path, map_location="cpu", weights_only=False)
    d.pop("_meta", None)
    return d


def teacher_batch(soft, b, device):
    """Gather cached teacher 34D for this batch by (subject, stim). Any missing
    key drops to zeros with a masked-out flag so distill loss ignores it."""
    rows, have = [], []
    for subj, sn in zip(b["subject"], b["stim_num"]):
        k = key(subj, sn)
        if k in soft:
            rows.append(soft[k]); have.append(1.0)
        else:
            rows.append(torch.zeros(34)); have.append(0.0)
    T = torch.stack(rows).to(device)
    m = torch.tensor(have, device=device).view(-1, 1)
    return T, m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    cfg = yaml.safe_load(open(ap.parse_args().config))
    tr = cfg["train"]
    seed_all(int(tr.get("seed", 0)))
    device = tr.get("device", "cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    mods = {"brain": True, "video": False, "caption": False}   # student = brain-only
    model = build_model({**cfg, "modalities": mods}).to(device)
    soft = load_soft(cfg["data"]["soft_labels"])
    lam = cfg.get("loss", {})
    lambda_dist = float(lam.get("lambda_dist", 1.0))
    print(f"[student] enc={cfg['encoder']['type']} brain-only lambda_dist={lambda_dist} "
          f"soft_labels={len(soft)} device={device}")

    data = cfg.get("data", {})
    bsrc = data.get("brain_source", "roi_mean")
    train_ds = HorikawaDataset(split="train", fmri_mode="mean", brain_source=bsrc, caption_mode="off")
    val_ds = HorikawaDataset(split="val", fmri_mode="mean", brain_source=bsrc, caption_mode="off")
    collate = make_collate(None)
    tl = DataLoader(train_ds, batch_size=int(tr["batch_size"]), shuffle=True, collate_fn=collate)
    vl = DataLoader(val_ds, batch_size=int(tr["batch_size"]), shuffle=False, collate_fn=collate)

    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                            lr=float(tr["lr"]), weight_decay=float(tr.get("weight_decay", 0.01)))
    max_tb = tr.get("max_train_batches")
    hist = []
    for epoch in range(int(tr["epochs"])):
        model.train(); train_ds.set_epoch(epoch)
        run, nb = 0.0, 0
        for i, b in enumerate(tl):
            if max_tb and i >= max_tb:
                break
            pred = forward_batch(model, b, mods, device)
            T, have = teacher_batch(soft, b, device)
            loss = total_student_loss(pred, b["label"].to(device), teacher_pred=T,
                                      active_mask=have if lambda_dist > 0 else None,
                                      lambda_hard=lam.get("lambda_hard", 1.0),
                                      lambda_dist=lambda_dist,
                                      hard_kind=lam.get("hard_kind", "mse"))
            opt.zero_grad(); loss.backward(); opt.step()
            run += loss.item(); nb += 1
        prof = evaluate(model, vl, mods, device, tr.get("max_eval_batches"))
        print(f"[student e{epoch}] loss={run/max(nb,1):.4f} val pearson={prof['pearson_mean']:+.4f} "
              f"ccc={prof['ccc_mean']:+.4f}")
        hist.append({"epoch": epoch, "val_pearson": prof["pearson_mean"], "val_ccc": prof["ccc_mean"]})

    out = REPO_ROOT / tr.get("out_json", "project/output/student_distill.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"config": cfg, "history": hist}, indent=2))
    if hist:
        best = max(hist, key=lambda h: h["val_pearson"])
        print(f"[done] best pearson {best['val_pearson']:+.4f} (context lift = this - Track A direct)")


if __name__ == "__main__":
    main()
