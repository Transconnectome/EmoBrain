"""Track B, step 2. Cache the frozen teacher's 34D soft labels (spec §8.6.1).

Load the teacher checkpoint, run it over every (subject, stimulus) in the train
and val splits with its full modality set, and store the raw 34D output (NO
softmax, spec §8.4). The student then reads these cached vectors by (subject,
stim) instead of running the teacher every step, so student throughput matches a
single model.

Output.
    project/shared/output/teacher_soft_labels/<tag>/soft_labels.pt
    { "(subject, stim)": tensor(34) , ..., "_meta": {...} }

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/cache_soft_labels.sh <teacher_config.yaml>
"""

from __future__ import annotations

import argparse
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
from project.code.training.trainer import make_collate, forward_batch  # noqa: E402


def key(subject, stim):
    return f"{subject}|{int(stim)}"


@torch.no_grad()
def cache_split(model, ds, collate, mods, device, batch_size):
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False, collate_fn=collate)
    out = {}
    for b in loader:
        pred = forward_batch(model, b, mods, device).float().cpu()   # raw 34D, no softmax
        for j, sn in enumerate(b["stim_num"]):
            out[key(b["subject"][j], sn)] = pred[j].clone()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    cfg = yaml.safe_load(open(ap.parse_args().config))
    tr = cfg["train"]
    device = tr.get("device", "cpu")
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    model = build_model(cfg).to(device)
    ckpt_path = REPO_ROOT / tr.get("teacher_ckpt", "project/output/checkpoints/teacher.pt")
    state = torch.load(ckpt_path, map_location=device, weights_only=False)["state_dict"]
    model.load_state_dict(state)
    model.eval()
    print(f"[cache] loaded teacher {ckpt_path}")

    mods = cfg.get("modalities", {"brain": True, "video": True, "caption": True})
    data = cfg.get("data", {})
    bs = int(tr["batch_size"])
    video_npy = np.load(REPO_ROOT / cfg["video"]["path"]) if mods.get("video") else None
    collate = make_collate(video_npy)

    soft = {}
    for split in ("train", "val"):
        ds = HorikawaDataset(split=split, fmri_mode="mean",
                             brain_source=data.get("brain_source", "roi_mean"),
                             caption_mode="human" if mods.get("caption") else "off")
        part = cache_split(model, ds, collate, mods, device, bs)
        soft.update(part)
        print(f"[cache] {split}: {len(part)} soft labels")

    tag = cfg.get("run", {}).get("name", "teacher")
    out = REPO_ROOT / "project/shared/output/teacher_soft_labels" / tag / "soft_labels.pt"
    out.parent.mkdir(parents=True, exist_ok=True)
    soft["_meta"] = {
        "tag": tag,
        "modalities": mods,
        "n": len(soft),
        "teacher_checkpoint": str(ckpt_path),
        "brain_source": data.get("brain_source"),
        "key_schema": "subject|stimulus_num",
        "splits": ["train", "val"],
        "note": "raw 34D teacher output in log1p_z space; no softmax",
    }
    torch.save(soft, out)
    print(f"[cache] {len(soft)-1} total -> {out}")


if __name__ == "__main__":
    main()
