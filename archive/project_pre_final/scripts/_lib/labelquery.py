"""Shared plumbing for the label-query decoder gates (Phase 0).

Both gates train the same brain-only decoder on the same split with the same
metric, and differ only in which emotions are visible during training. Keeping the
data loading, standardisation, metric and training loop here means the two gate
scripts cannot silently diverge in a way that would make their numbers
incomparable.

Everything here is brain-only by design: the stimulus decodes emotion far better
than the brain does (0.493 vs 0.294, brain marginal +0.028), so any claim about the
BRAIN has to be read out from brain alone at test time.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from project.data.datasets import HorikawaDataset  # noqa: E402
from project.evaluation.metrics import compute_metrics  # noqa: E402
from project.code.decoder.label_query_decoder import LabelQueryDecoder  # noqa: E402

QUERY_NPY = REPO_ROOT / "project" / "shared" / "data" / "emotion_query" / "emotion_query_mpnet.npy"
ORDER_TXT = REPO_ROOT / "project" / "shared" / "data" / "cowen34_order.txt"

# Reference numbers on this exact split/metric, for interpreting any new result.
REFERENCE = {
    "mean_profile_floor": 0.002,
    "ridge_brain": 0.294,          # the bar the decoder must clear (same roi_mean input)
    "kernel_ridge_brain": 0.313,
    "cheap_mlp_fusion_3modal": 0.533,
    "llm_teacher_3modal": 0.553,
    "llm_encoder_student_brain_only": 0.154,
}


def emotion_names() -> list[str]:
    return [l.strip() for l in ORDER_TXT.read_text().splitlines() if l.strip()]


def load_query_init() -> torch.Tensor:
    if not QUERY_NPY.exists():
        raise FileNotFoundError(
            f"{QUERY_NPY} missing. Run project/scripts/build_emotion_query_embeddings.sh first."
        )
    return torch.as_tensor(np.load(QUERY_NPY))


def load_split(split: str) -> dict:
    """brain (N,450) roi_mean + Y (N,34) log1p_z, in the canonical stimulus split."""
    ds = HorikawaDataset(split=split, fmri_mode="mean", brain_source="roi_mean",
                         caption_mode="off")
    brain, Y, stim = [], [], []
    for i in range(len(ds)):
        s = ds[i]
        brain.append(np.asarray(s["fmri"], dtype=np.float32))
        Y.append(np.asarray(s["label"], dtype=np.float32))
        stim.append(int(s["stim_num"]))
    return {"brain": np.stack(brain), "Y": np.stack(Y), "stim": np.asarray(stim)}


class Standardizer:
    """z-score fitted on train only."""

    def __init__(self, X):
        self.mu = X.mean(0, keepdims=True)
        self.sd = X.std(0, keepdims=True) + 1e-6

    def __call__(self, X):
        return (X - self.mu) / self.sd


def profile_metrics(pred: np.ndarray, true: np.ndarray) -> dict:
    """Per-clip profile metric, identical to the trainer's headline metric."""
    return compute_metrics(pred.astype(np.float32), true.astype(np.float32),
                           which=["profile"])["profile"]


def per_clip_pearson(pred: np.ndarray, true: np.ndarray) -> np.ndarray:
    """Per-clip Pearson across emotion dimensions -> (N,), for bootstrap CIs."""
    p = pred - pred.mean(1, keepdims=True)
    t = true - true.mean(1, keepdims=True)
    num = (p * t).sum(1)
    den = np.sqrt((p ** 2).sum(1) * (t ** 2).sum(1)) + 1e-8
    return num / den


def per_emotion_pearson(pred: np.ndarray, true: np.ndarray) -> np.ndarray:
    """Across-clip Pearson for each emotion column -> (n_emotions,).

    This is the interpretable readout for the held-out test: "can this emotion be
    decoded across clips, having never been trained on?"
    """
    p = pred - pred.mean(0, keepdims=True)
    t = true - true.mean(0, keepdims=True)
    num = (p * t).sum(0)
    den = np.sqrt((p ** 2).sum(0) * (t ** 2).sum(0)) + 1e-8
    return num / den


def bootstrap_diff(a: np.ndarray, b: np.ndarray, n_boot: int = 2000, seed: int = 0):
    """95% CI on mean(a - b) resampling the shared unit (clips or emotions)."""
    rng = np.random.default_rng(seed)
    d = a - b
    n = len(d)
    boots = np.array([d[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    return float(d.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def build_decoder(query_init, query_mode: str, d_model: int = 256, n_layers: int = 3,
                  seed: int = 0) -> LabelQueryDecoder:
    torch.manual_seed(seed)
    return LabelQueryDecoder(n_emotions=34, d_model=d_model, n_layers=n_layers,
                             use_video=False, use_caption=False,
                             query_init=query_init, query_mode=query_mode)


def train_decoder(net, tr, va, scaler, device, active_idx=None, epochs: int = 150,
                  bs: int = 256, lr: float = 1e-3, wd: float = 1e-4, seed: int = 0,
                  verbose_every: int = 0):
    """Train brain-only on `active_idx` emotions; select the best epoch on val.

    active_idx=None trains on all 34. When a subset is given, the loss and the val
    selection both see only those emotions, so held-out emotions influence nothing.
    """
    g = torch.Generator().manual_seed(seed)
    Xtr = torch.as_tensor(scaler(tr["brain"]), dtype=torch.float32)
    Ytr = torch.as_tensor(tr["Y"], dtype=torch.float32)
    Xva = torch.as_tensor(scaler(va["brain"]), dtype=torch.float32, device=device)
    Yva = va["Y"]

    idx_t = None if active_idx is None else torch.as_tensor(active_idx, dtype=torch.long)
    held = None
    if idx_t is not None:
        mask = np.ones(34, dtype=bool)
        mask[np.asarray(active_idx)] = False
        held = torch.as_tensor(np.where(mask)[0], dtype=torch.long)
        net.freeze_query_delta(held)

    net = net.to(device)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=wd)
    lossf = torch.nn.MSELoss()
    n = Xtr.shape[0]
    best_v, best_state, best_ep = -np.inf, None, -1

    for ep in range(epochs):
        net.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            b = perm[i:i + bs]
            xb = Xtr[b].to(device)
            yb = Ytr[b].to(device) if idx_t is None else Ytr[b][:, idx_t].to(device)
            opt.zero_grad()
            lossf(net(xb, query_idx=idx_t), yb).backward()
            opt.step()
            if held is not None:
                net.freeze_query_delta(held)   # re-assert after every optimiser step
        net.eval()
        with torch.no_grad():
            pv = net(Xva, query_idx=idx_t).cpu().numpy()
        yv = Yva if idx_t is None else Yva[:, np.asarray(active_idx)]
        v = profile_metrics(pv, yv)["pearson_mean"]
        if v > best_v:
            best_v, best_ep = v, ep
            best_state = {k: t.detach().cpu().clone() for k, t in net.state_dict().items()}
        if verbose_every and (ep % verbose_every == 0 or ep == epochs - 1):
            print(f"    ep{ep:3d} val={v:+.4f} (best {best_v:+.4f} @ep{best_ep})")

    net.load_state_dict(best_state)
    net.eval()
    return net, {"best_val": float(best_v), "best_epoch": int(best_ep)}


@torch.no_grad()
def predict(net, X, scaler, device, query_idx=None) -> np.ndarray:
    xb = torch.as_tensor(scaler(X), dtype=torch.float32, device=device)
    qi = None if query_idx is None else torch.as_tensor(query_idx, dtype=torch.long)
    return net(xb, query_idx=qi).cpu().numpy()
