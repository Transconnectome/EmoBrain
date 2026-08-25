"""Train the LLM-free label-query decoder and put it head-to-head with the
numbers we already have, on the SAME test split and metric (per-clip 34D profile
Pearson).

Settled by this run.
  brain_only  vs ridge 0.294 and vs LLM-as-encoder student 0.154
              -> does a 3.8M label-query decoder beat linear ridge and the 4B LLM?
  full_3modal vs LLM teacher 0.553 and cheap MLP fusion 0.533
              -> does LLM-free fusion match the LLM as a fusion engine?

Queries are RANDOM-initialised here (the architecture test). Semantic emotion-word
init is the follow-up ablation that carries the zero-shot / cross-dataset story.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/train_label_query.sh
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402

from project.data.datasets import HorikawaDataset  # noqa: E402
from project.evaluation.metrics import compute_metrics  # noqa: E402
from project.code.decoder.label_query_decoder import LabelQueryDecoder  # noqa: E402

FEAT = REPO_ROOT / "project" / "shared" / "data" / "stimulus_features"
OUT = REPO_ROOT / "project" / "output" / "label_query_decoder.json"
SEED = 0


def load_split(split):
    ds = HorikawaDataset(split=split, fmri_mode="mean", brain_source="roi_mean", caption_mode="off")
    brain, Y, stim = [], [], []
    for i in range(len(ds)):
        s = ds[i]
        brain.append(np.asarray(s["fmri"], dtype=np.float32))
        Y.append(np.asarray(s["label"], dtype=np.float32))
        stim.append(int(s["stim_num"]))
    brain = np.stack(brain); Y = np.stack(Y); stim = np.asarray(stim)
    vid = np.load(FEAT / "vjepa2_pretrained.npy")[stim - 1].astype(np.float32)
    cap = np.load(FEAT / "caption_embed.npy")[stim - 1].astype(np.float32)
    return {"brain": brain, "video": vid, "caption": cap, "Y": Y}


class Std:
    def __init__(self, X): self.mu = X.mean(0, keepdims=True); self.sd = X.std(0, keepdims=True) + 1e-6
    def __call__(self, X): return (X - self.mu) / self.sd


def profile(pred, true):
    return compute_metrics(pred.astype(np.float32), true.astype(np.float32), which=["profile"])["profile"]


def train_one(setting, tr, va, te, sc, device, epochs=200, bs=256, lr=1e-3, wd=1e-4):
    use_video = setting != "brain_only"
    use_caption = setting != "brain_only"
    torch.manual_seed(SEED)
    g = torch.Generator().manual_seed(SEED)

    def pack(d, dev):
        out = {"brain": torch.as_tensor(sc["brain"](d["brain"]), dtype=torch.float32, device=dev),
               "Y": torch.as_tensor(d["Y"], dtype=torch.float32, device=dev)}
        if use_video:
            out["video"] = torch.as_tensor(sc["video"](d["video"]), dtype=torch.float32, device=dev)
            out["caption"] = torch.as_tensor(sc["caption"](d["caption"]), dtype=torch.float32, device=dev)
        return out

    TR = pack(tr, "cpu"); VA = pack(va, device); TE = pack(te, device)
    net = LabelQueryDecoder(use_video=use_video, use_caption=use_caption).to(device)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=wd)
    lossf = torch.nn.MSELoss()
    n = TR["Y"].shape[0]
    best_v, best_state, best_ep = -np.inf, None, -1
    for ep in range(epochs):
        net.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = TR["brain"][idx].to(device); yb = TR["Y"][idx].to(device)
            kw = {}
            if use_video:
                kw["video"] = TR["video"][idx].to(device); kw["caption"] = TR["caption"][idx].to(device)
            opt.zero_grad(); lossf(net(xb, **kw), yb).backward(); opt.step()
        net.eval()
        with torch.no_grad():
            kw = {"video": VA.get("video"), "caption": VA.get("caption")} if use_video else {}
            pv = net(VA["brain"], **kw).cpu().numpy()
        v = profile(pv, va["Y"])["pearson_mean"]
        if v > best_v:
            best_v, best_ep = v, ep
            best_state = {k: t.detach().cpu().clone() for k, t in net.state_dict().items()}
    net.load_state_dict(best_state); net.eval()
    with torch.no_grad():
        kw = {"video": TE.get("video"), "caption": TE.get("caption")} if use_video else {}
        pt = net(TE["brain"], **kw).cpu().numpy()
    return {"test": profile(pt, te["Y"]), "best_val": best_v, "best_epoch": best_ep}


def main():
    tr, va, te = load_split("train"), load_split("val"), load_split("test")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sc = {k: Std(tr[k]) for k in ("brain", "video", "caption")}
    print(f"[data] train {len(tr['Y'])} val {len(va['Y'])} test {len(te['Y'])} device={device}")

    ref = {"mean_floor": 0.002, "ridge_brain": 0.294, "kernel_ridge": 0.313,
           "cheap_mlp_fusion": 0.533, "LLM_teacher": 0.553,
           "LLM_direct_student": 0.154}

    results = {}
    for setting in ("brain_only", "full_3modal"):
        r = train_one(setting, tr, va, te, sc, device)
        results[setting] = r
        print(f"[{setting}] test_pearson={r['test']['pearson_mean']:.4f} "
              f"ccc={r['test']['ccc_mean']:.4f} (best_val={r['best_val']:.4f} @ep{r['best_epoch']})")

    print("\n===== HEAD-TO-HEAD (per-clip 34D profile Pearson) =====")
    bo = results["brain_only"]["test"]["pearson_mean"]
    fm = results["full_3modal"]["test"]["pearson_mean"]
    print(f"  label-query brain-only : {bo:.4f}   vs ridge {ref['ridge_brain']} , LLM-student {ref['LLM_direct_student']}")
    print(f"  label-query 3-modal    : {fm:.4f}   vs cheap-MLP {ref['cheap_mlp_fusion']} , LLM-teacher {ref['LLM_teacher']}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"results": results, "reference": ref, "device": device}, indent=2))
    print(f"\n[done] -> {OUT}")


if __name__ == "__main__":
    main()
