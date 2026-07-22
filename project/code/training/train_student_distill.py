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
    meta = d.pop("_meta", None)
    if meta is None:
        raise ValueError(f"soft-label cache has no provenance metadata: {path}")
    return d, meta


def teacher_batch(soft, b, device):
    """Gather cached teacher 34D and fail loudly on incomplete caches."""
    rows, missing = [], []
    for subj, sn in zip(b["subject"], b["stim_num"]):
        k = key(subj, sn)
        if k in soft:
            rows.append(soft[k])
        else:
            missing.append(k)
    if missing:
        raise KeyError(f"teacher cache is missing {len(missing)} keys; first={missing[0]}")
    return torch.stack(rows).to(device)


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
    soft, soft_meta = load_soft(cfg["data"]["soft_labels"])
    lam = cfg.get("loss", {})
    lambda_dist = float(lam.get("lambda_dist", 1.0))
    print(f"[student] enc={cfg['encoder']['type']} brain-only lambda_dist={lambda_dist} "
          f"soft_labels={len(soft)} teacher={soft_meta.get('tag')} device={device}")

    data = cfg.get("data", {})
    bsrc = data.get("brain_source", "roi_mean")
    teacher_bsrc = soft_meta.get("brain_source")
    if teacher_bsrc != bsrc:
        raise ValueError(
            "teacher/student brain source mismatch: "
            f"teacher={teacher_bsrc!r}, student={bsrc!r}"
        )
    train_ds = HorikawaDataset(split="train", fmri_mode="mean", brain_source=bsrc, caption_mode="off")
    val_ds = HorikawaDataset(split="val", fmri_mode="mean", brain_source=bsrc, caption_mode="off")
    test_ds = HorikawaDataset(split="test", fmri_mode="mean", brain_source=bsrc, caption_mode="off")
    collate = make_collate(None)
    tl = DataLoader(train_ds, batch_size=int(tr["batch_size"]), shuffle=True, collate_fn=collate)
    vl = DataLoader(val_ds, batch_size=int(tr["batch_size"]), shuffle=False, collate_fn=collate)
    tel = DataLoader(test_ds, batch_size=int(tr["batch_size"]), shuffle=False, collate_fn=collate)

    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                            lr=float(tr["lr"]), weight_decay=float(tr.get("weight_decay", 0.01)))
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
            T = teacher_batch(soft, b, device)
            loss = total_student_loss(pred, b["label"].to(device), teacher_pred=T,
                                      lambda_hard=lam.get("lambda_hard", 1.0),
                                      lambda_dist=lambda_dist,
                                      hard_kind=lam.get("hard_kind", "mse"),
                                      distill_kind=lam.get("distill_kind", "mse"))
            opt.zero_grad(); loss.backward(); opt.step()
            run += loss.item(); nb += 1
        prof = evaluate(model, vl, mods, device, tr.get("max_eval_batches"))
        print(f"[student e{epoch}] loss={run/max(nb,1):.4f} val pearson={prof['pearson_mean']:+.4f} "
              f"ccc={prof['ccc_mean']:+.4f}")
        hist.append({"epoch": epoch, "val_pearson": prof["pearson_mean"], "val_ccc": prof["ccc_mean"]})
        if prof["pearson_mean"] > best_v:
            best_v = prof["pearson_mean"]
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state is None:
        raise RuntimeError("student training produced no checkpoint")
    model.load_state_dict(best_state)
    test_profile = evaluate(model, tel, mods, device, tr.get("max_eval_batches"))

    out = REPO_ROOT / tr.get("out_json", "project/output/student_distill.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    ckpt = REPO_ROOT / tr.get(
        "checkpoint", f"project/output/checkpoints/{out.stem}.pt"
    )
    ckpt.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": best_state, "config": cfg, "val_pearson": best_v,
                "test_profile": test_profile, "teacher_meta": soft_meta}, ckpt)
    out.write_text(json.dumps({"config": cfg, "history": hist,
                               "best_val_pearson": best_v,
                               "test_profile": test_profile,
                               "teacher_meta": soft_meta,
                               "checkpoint": str(ckpt)}, indent=2))
    if hist:
        best = max(hist, key=lambda h: h["val_pearson"])
        print(f"[done] best val={best['val_pearson']:+.4f} "
              f"test={test_profile['pearson_mean']:+.4f}")


if __name__ == "__main__":
    main()
