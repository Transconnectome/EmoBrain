"""Training loop. config -> build_model -> train -> eval (Pearson / CCC / MSE).

One config fully specifies an experiment (encoder x projector x backbone x head
+ modalities + data + train). Swapping the model is a config edit; this loop
never changes. Objective = supervised_loss (per-emotion MSE, z-space).
Headline = compute_metrics profile Pearson / CCC, compared to the ridge
baseline (0.30 / 0.17).

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/training/train.sh <config.yaml>

The real Qwen run is a config swap (backbone stub -> qwen, device cuda) and
goes through sbatch (prior approval).
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np  # noqa: E402
import torch  # noqa: E402
import yaml  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from project.data.datasets import HorikawaDataset  # noqa: E402
from project.data.labels import Cowen34Normalizer  # noqa: E402
from project.evaluation.metrics import compute_metrics  # noqa: E402
from project.models.build import build_model  # noqa: E402
from project.models.losses.supervised import supervised_loss  # noqa: E402
from project.models.prompt import TRACK_A_QUESTION  # noqa: E402
from project.training.collate import make_collate  # noqa: E402


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def resolve_device(name: str) -> str:
    if name == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return name


def move(batch: dict, device: str) -> dict:
    return {k: (v.to(device) if torch.is_tensor(v) else v) for k, v in batch.items()}


@torch.no_grad()
def evaluate(model, loader, device, normalizer, max_batches=None) -> dict:
    model.eval()
    preds, labels = [], []
    for i, batch in enumerate(loader):
        if max_batches and i >= max_batches:
            break
        b = move(batch, device)
        p = model(fmri=b["fmri"], text_ids=b["text_ids"], text_mask=b["text_mask"])
        preds.append(p.float().cpu().numpy())
        labels.append(b["label"].cpu().numpy())
    pred = np.concatenate(preds)
    true = np.concatenate(labels)
    return compute_metrics(pred, true, which=["profile", "error"], normalizer=normalizer)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    cfg = yaml.safe_load(open(ap.parse_args().config))
    tr = cfg["train"]

    seed_all(int(tr.get("seed", 0)))
    device = resolve_device(tr.get("device", "auto"))
    print(f"[cfg] enc={cfg['encoder']['name']} proj={cfg['projector']['name']} "
          f"bb={cfg['backbone']['name']} device={device}")

    model = build_model(cfg).to(device)
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[model] trainable params = {n_train:,}")

    fmri_mode = cfg.get("data", {}).get("fmri_mode", "mean")
    train_ds = HorikawaDataset(split="train", fmri_mode=fmri_mode)
    val_ds = HorikawaDataset(split="val", fmri_mode=fmri_mode)
    collate = make_collate(TRACK_A_QUESTION, model.backbone)
    train_loader = DataLoader(train_ds, batch_size=int(tr["batch_size"]),
                              shuffle=True, collate_fn=collate)
    val_loader = DataLoader(val_ds, batch_size=int(tr["batch_size"]),
                            shuffle=False, collate_fn=collate)
    print(f"[data] train {len(train_ds)} / val {len(val_ds)} (fmri_mode={fmri_mode})")

    norm = Cowen34Normalizer.load(
        REPO_ROOT / "project/shared/data/norm_stats/cowen34_train.pt"
    )
    opt = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=float(tr["lr"]), weight_decay=float(tr.get("weight_decay", 0.0)),
    )

    max_tb = tr.get("max_train_batches")
    max_eb = tr.get("max_eval_batches")
    log_every = int(tr.get("log_every", 10))
    history = []
    gstep = 0
    step_losses = []
    for epoch in range(int(tr["epochs"])):
        model.train()
        train_ds.set_epoch(epoch)
        running, nb = 0.0, 0
        for i, batch in enumerate(train_loader):
            if max_tb and i >= max_tb:
                break
            b = move(batch, device)
            pred = model(fmri=b["fmri"], text_ids=b["text_ids"],
                         text_mask=b["text_mask"])
            loss = supervised_loss(pred, b["label"])
            opt.zero_grad()
            loss.backward()
            opt.step()
            lv = loss.item()
            running += lv
            nb += 1
            step_losses.append(lv)
            if gstep % log_every == 0:
                print(f"  [e{epoch} step {gstep}] loss={lv:.4f}")
            gstep += 1
        train_loss = running / max(nb, 1)

        m = evaluate(model, val_loader, device, norm, max_eb)
        prof, err = m["profile"], m["error"]
        print(f"[epoch {epoch}] train_loss={train_loss:.4f} | "
              f"val pearson={prof['pearson_mean']:+.4f} ccc={prof['ccc_mean']:+.4f} "
              f"mse_z={err['mse_z']:.4f}")
        history.append({
            "epoch": epoch, "train_loss": train_loss,
            "val_pearson": prof["pearson_mean"], "val_ccc": prof["ccc_mean"],
            "val_mse_z": err["mse_z"],
        })

    out = REPO_ROOT / tr.get("out_json", "project/output/train_run.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"config": cfg, "history": history}, indent=2))
    print(f"[done] saved {out}")
    print("[ref] B1 ridge (no LLM) pearson ~0.30 / ccc ~0.17 = comparison anchor")
    # two separate questions, reported separately (do not conflate).
    # (1) did the TRAIN objective move? per-batch loss is noisy -> window-average.
    if step_losses:
        w = max(1, min(10, len(step_losses) // 2))
        first_avg = sum(step_losses[:w]) / w
        last_avg = sum(step_losses[-w:]) / w
        drop = first_avg - last_avg
        print(f"[train] loss {first_avg:.2f} -> {last_avg:.2f} (drop {drop:+.2f}, "
              f"{w}-step avg) => {'optimizes' if drop > 0.5 else 'flat'}")
    # (2) did it GENERALIZE? val_pearson is the real signal. Report best epoch
    #     and flag overfitting (last worse than best).
    if history:
        best = max(history, key=lambda h: h["val_pearson"])
        last = history[-1]
        print(f"[val] best epoch {best['epoch']}: pearson {best['val_pearson']:+.4f} "
              f"ccc {best['val_ccc']:+.4f} mse_z {best['val_mse_z']:.4f} "
              f"(ridge 0.30 / 0.17 / 0.91)")
        if last["val_pearson"] < best["val_pearson"] - 0.01:
            print(f"[val] OVERFIT after epoch {best['epoch']}: last pearson "
                  f"{last['val_pearson']:+.4f} < best {best['val_pearson']:+.4f} "
                  f"=> early stopping / regularize")


if __name__ == "__main__":
    main()
