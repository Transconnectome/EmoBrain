"""LLM-free label-query (Query2Label) decoder. The decisive "is the LLM worth it"
test.

34 emotion queries cross-attend to a brain feature map (450 ROI tokens) and,
optionally, video + caption tokens, inside a small transformer decoder. Each
query's contextualised state is projected by ONE shared scalar head to that
emotion's log1p_z score. This is exactly what the LLM prompt ("score each of
these 34 emotions") was meant to do, without a 4B model in the loop.

Same Horikawa split and per-clip 34D profile-Pearson metric as every other run,
so the output sits directly beside:
    ridge_brain 0.294 | A direct (pooled LLM) 0.154 | cheap MLP fusion 0.533 |
    LLM teacher (Qwen fusion) 0.553
If fusion here reaches ~0.55, the LLM backbone adds nothing. If brain-only clears
0.294, the query readout already beats what the ViT-pooled LLM student could not.

1a here uses RANDOM learnable queries (no text encoder / no download). Semantic
query init (for zero-shot and Emo-FilM cross-label transfer) is a later 1b.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/label_query_decoder.sh
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402
import torch.nn as nn  # noqa: E402

from project.data.datasets import HorikawaDataset  # noqa: E402
from project.evaluation.metrics import compute_metrics  # noqa: E402

FEAT = REPO_ROOT / "project" / "shared" / "data" / "stimulus_features"
OUT = REPO_ROOT / "project" / "output" / "label_query_decoder.json"
SEED = 0
N_ROI = 450
N_EMO = 34


def profile(pred, true):
    return compute_metrics(pred.astype(np.float32), true.astype(np.float32),
                           which=["profile"])["profile"]


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


class LabelQueryDecoder(nn.Module):
    """Query2Label. Brain ROI tokens (+ optional video/caption tokens) as memory,
    34 emotion queries as decoder targets, shared scalar readout."""

    def __init__(self, d=256, n_layers=3, n_heads=4, use_video=True, use_caption=True,
                 vid_dim=1408, cap_dim=768, dropout=0.1):
        super().__init__()
        self.use_video, self.use_caption = use_video, use_caption
        # brain feature map: each ROI scalar -> d, plus a learned per-ROI position.
        self.roi_val = nn.Linear(1, d)
        self.roi_pos = nn.Parameter(torch.randn(1, N_ROI, d) * 0.02)
        if use_video:
            self.vid_proj = nn.Linear(vid_dim, d)
        if use_caption:
            self.cap_proj = nn.Linear(cap_dim, d)
        self.queries = nn.Parameter(torch.randn(1, N_EMO, d) * 0.02)   # 1a: random init
        layer = nn.TransformerDecoderLayer(d, n_heads, d * 4, dropout, batch_first=True)
        self.dec = nn.TransformerDecoder(layer, n_layers)
        self.readout = nn.Linear(d, 1)                                 # SHARED across emotions

    def memory(self, b, v, c):
        toks = [self.roi_val(b.unsqueeze(-1)) + self.roi_pos]          # (B,450,d)
        if self.use_video:
            toks.append(self.vid_proj(v).unsqueeze(1))                 # (B,1,d)
        if self.use_caption:
            toks.append(self.cap_proj(c).unsqueeze(1))
        return torch.cat(toks, dim=1)

    def forward(self, b, v=None, c=None):
        mem = self.memory(b, v, c)
        q = self.queries.expand(b.shape[0], -1, -1)
        out = self.dec(q, mem)                                         # (B,34,d)
        return self.readout(out).squeeze(-1)                           # (B,34)


def to_t(x, device):
    return torch.as_tensor(x, dtype=torch.float32, device=device)


def train_eval(tr, va, te, use_video, use_caption, device, epochs=80, bs=256, lr=1e-3, wd=1e-4):
    torch.manual_seed(SEED)
    g = torch.Generator().manual_seed(SEED)
    net = LabelQueryDecoder(use_video=use_video, use_caption=use_caption).to(device)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=wd)
    lossf = nn.MSELoss()
    Btr, Vtr, Ctr, Ytr = (to_t(tr[k], "cpu") for k in ("brain", "video", "caption", "Y"))
    n = len(Ytr)
    best_v, best_state, best_ep = -1e9, None, -1
    for ep in range(epochs):
        net.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            b = Btr[idx].to(device)
            v = Vtr[idx].to(device) if use_video else None
            c = Ctr[idx].to(device) if use_caption else None
            opt.zero_grad()
            lossf(net(b, v, c), Ytr[idx].to(device)).backward()
            opt.step()
        net.eval()
        with torch.no_grad():
            pv = net(to_t(va["brain"], device),
                     to_t(va["video"], device) if use_video else None,
                     to_t(va["caption"], device) if use_caption else None).cpu().numpy()
        vpear = profile(pv, va["Y"])["pearson_mean"]
        if vpear > best_v:
            best_v, best_ep = vpear, ep
            best_state = {k: t.detach().cpu().clone() for k, t in net.state_dict().items()}
    net.load_state_dict(best_state)
    net.eval()
    with torch.no_grad():
        pt = net(to_t(te["brain"], device),
                 to_t(te["video"], device) if use_video else None,
                 to_t(te["caption"], device) if use_caption else None).cpu().numpy()
    m = profile(pt, te["Y"])
    return {"test": m, "best_val_pearson": best_v, "best_epoch": best_ep}


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tr, va, te = load_split("train"), load_split("val"), load_split("test")
    print(f"[data] train {len(tr['Y'])} val {len(va['Y'])} test {len(te['Y'])} device={device}")

    conditions = {
        "labelq_brain_only": dict(use_video=False, use_caption=False),
        "labelq_fusion": dict(use_video=True, use_caption=True),
    }
    results = {}
    for name, kw in conditions.items():
        r = train_eval(tr, va, te, device=device, **kw)
        results[name] = r
        print(f"[{name}] test pearson={r['test']['pearson_mean']:+.4f} "
              f"ccc={r['test']['ccc_mean']:+.4f} (best val {r['best_val_pearson']:+.4f} @ep{r['best_epoch']})")

    REF = {"ridge_brain": 0.294, "A_direct_pooledLLM": 0.154,
           "cheap_mlp_fusion": 0.533, "LLM_teacher_qwen": 0.553}
    print("\n===== label-query (no LLM) vs references (test profile pearson) =====")
    print(f"{'labelq_brain_only':24s} {results['labelq_brain_only']['test']['pearson_mean']:+.4f}"
          f"   (beat ridge 0.294? {results['labelq_brain_only']['test']['pearson_mean']>0.294})")
    print(f"{'labelq_fusion':24s} {results['labelq_fusion']['test']['pearson_mean']:+.4f}"
          f"   (match LLM 0.553? cheap 0.533)")
    for k, v in REF.items():
        print(f"  ref {k:22s} {v:+.4f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"results": results, "references": REF,
                               "device": device, "seed": SEED,
                               "note": "1a random-init queries; semantic init is 1b"}, indent=2))
    print(f"\n[done] -> {OUT}")


if __name__ == "__main__":
    main()
