"""Cheap (no-LLM) fusion baseline + noise-floor / leakage controls.

Answers, on the SAME held-out stimulus test split and the SAME per-clip 34D
profile-Pearson metric used by the Qwen3-VL pipeline (project.evaluation.metrics),
two questions the LLM justification hinges on.

  Q_reframe (does rich info help at all?)
      ridge / MLP fusion of {brain + V-JEPA2 video + caption} vs ridge on brain
      alone (the R0 ceiling ~0.31). If fusion >> brain-alone, "emotion decoding
      needs rich information" is empirically supported without any LLM.

  Q_scope (is the help brain-decoding or just stimulus-decoding?)
      ridge on {video + caption} with NO brain. Because video+caption are
      stimulus features available at test time, a high number here means the
      fusion lift is largely stimulus decoding, NOT reading cortex. This is the
      quantitative guard for our claim that rich info is a TRAINING scaffold for
      a brain-only student, not a test-time crutch.

Controls.
  mean_profile_floor   predict the train-mean 34D profile for every test clip.
                       Reveals how much per-clip Pearson is free from the shared
                       heavy-tailed profile structure (73.8% zeros).
  brain_shuffle        permute the brain rows against their labels. ridge_brain
                       must collapse to ~floor (no leakage); mlp_fusion with the
                       brain shuffled measures the brain's MARGINAL contribution
                       over stimulus features.

Everything trains on train, selects on val, and reports the untouched test.
Model swap only; the split, labels, and metric are identical to the LLM runs.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/cheap_fusion_and_floor.sh
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import torch  # noqa: E402
from sklearn.linear_model import Ridge  # noqa: E402

from project.data.datasets import HorikawaDataset  # noqa: E402
from project.evaluation.metrics import compute_metrics  # noqa: E402

FEAT = REPO_ROOT / "project" / "shared" / "data" / "stimulus_features"
OUT = REPO_ROOT / "project" / "output" / "cheap_fusion_and_floor.json"
SEED = 0
ALPHAS = [1.0, 10.0, 100.0, 1000.0, 10000.0]


def profile_pearson(pred: np.ndarray, true: np.ndarray) -> dict:
    """Per-clip 34D profile metric, exactly as the LLM trainer computes it."""
    m = compute_metrics(pred.astype(np.float32), true.astype(np.float32), which=["profile"])
    return m["profile"]


def per_clip_pearson_vec(pred: np.ndarray, true: np.ndarray) -> np.ndarray:
    """Per-clip Pearson r as a length-N vector, for bootstrap CIs on differences."""
    p = pred - pred.mean(1, keepdims=True)
    t = true - true.mean(1, keepdims=True)
    num = (p * t).sum(1)
    den = np.sqrt((p ** 2).sum(1) * (t ** 2).sum(1)) + 1e-8
    return num / den


def load_split(split: str):
    """Return brain(N,450), video(N,1408), caption(N,768), Y(N,34), stim_num, subj."""
    ds = HorikawaDataset(split=split, fmri_mode="mean", brain_source="roi_mean", caption_mode="off")
    brain, Y, stim, subj = [], [], [], []
    for i in range(len(ds)):
        s = ds[i]
        brain.append(np.asarray(s["fmri"], dtype=np.float32))
        Y.append(np.asarray(s["label"], dtype=np.float32))
        stim.append(int(s["stim_num"]))
        subj.append(s["subject_id"])
    brain = np.stack(brain)
    Y = np.stack(Y)
    stim = np.asarray(stim)
    vid = np.load(FEAT / "vjepa2_pretrained.npy")[stim - 1].astype(np.float32)
    cap = np.load(FEAT / "caption_embed.npy")[stim - 1].astype(np.float32)
    return {"brain": brain, "video": vid, "caption": cap, "Y": Y, "stim": stim, "subj": subj}


class Standardizer:
    """Per-modality z-score fitted on train, applied everywhere."""

    def __init__(self, X):
        self.mu = X.mean(0, keepdims=True)
        self.sd = X.std(0, keepdims=True) + 1e-6

    def __call__(self, X):
        return (X - self.mu) / self.sd


def build_X(d, scalers, keys):
    return np.concatenate([scalers[k](d[k]) for k in keys], axis=1)


def fit_ridge(Xtr, Ytr, Xva, Yva):
    best_a, best_v, best_m = None, -np.inf, None
    for a in ALPHAS:
        m = Ridge(alpha=a).fit(Xtr, Ytr)
        v = profile_pearson(m.predict(Xva), Yva)["pearson_mean"]
        if v > best_v:
            best_a, best_v, best_m = a, v, m
    return best_m, best_a, best_v


class MLP(torch.nn.Module):
    def __init__(self, d_in, d_out=34, hidden=(512, 256), p=0.1):
        super().__init__()
        layers, d = [], d_in
        for h in hidden:
            layers += [torch.nn.Linear(d, h), torch.nn.GELU(), torch.nn.Dropout(p)]
            d = h
        layers += [torch.nn.Linear(d, d_out)]
        self.net = torch.nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def fit_mlp(Xtr, Ytr, Xva, Yva, device, epochs=200, bs=256, lr=1e-3, wd=1e-4):
    torch.manual_seed(SEED)
    g = torch.Generator().manual_seed(SEED)
    xtr = torch.as_tensor(Xtr, dtype=torch.float32)
    ytr = torch.as_tensor(Ytr, dtype=torch.float32)
    xva = torch.as_tensor(Xva, dtype=torch.float32, device=device)
    net = MLP(Xtr.shape[1]).to(device)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=wd)
    lossf = torch.nn.MSELoss()
    n = len(xtr)
    best_v, best_state = -np.inf, None
    for ep in range(epochs):
        net.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb = xtr[idx].to(device)
            yb = ytr[idx].to(device)
            opt.zero_grad()
            lossf(net(xb), yb).backward()
            opt.step()
        net.eval()
        with torch.no_grad():
            pv = net(xva).cpu().numpy()
        v = profile_pearson(pv, Yva)["pearson_mean"]
        if v > best_v:
            best_v = v
            best_state = {k: t.detach().cpu().clone() for k, t in net.state_dict().items()}
    net.load_state_dict(best_state)
    return net, best_v


@torch.no_grad()
def mlp_predict(net, X, device):
    net.eval()
    return net(torch.as_tensor(X, dtype=torch.float32, device=device)).cpu().numpy()


def bootstrap_ci(a_vec, b_vec, n_boot=2000, seed=SEED):
    """95% CI on mean(a - b) over clips (a,b are per-clip Pearson vectors)."""
    rng = np.random.default_rng(seed)
    diff = a_vec - b_vec
    n = len(diff)
    boots = np.array([diff[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    return float(diff.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def main():
    print("[load] building matrices ...")
    tr, va, te = load_split("train"), load_split("val"), load_split("test")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[data] train {len(tr['Y'])} val {len(va['Y'])} test {len(te['Y'])} device={device}")

    scalers = {k: Standardizer(tr[k]) for k in ("brain", "video", "caption")}
    Ytr, Yva, Yte = tr["Y"], va["Y"], te["Y"]

    results = {}
    pcv = {}  # per-clip pearson vectors on TEST, for CIs

    # --- floor -------------------------------------------------------------
    mean_prof = Ytr.mean(0, keepdims=True)
    floor_pred = np.repeat(mean_prof, len(Yte), axis=0)
    results["mean_profile_floor"] = profile_pearson(floor_pred, Yte)
    pcv["mean_profile_floor"] = per_clip_pearson_vec(floor_pred, Yte)

    # --- ridge families ----------------------------------------------------
    ridge_specs = {
        "ridge_brain": ["brain"],
        "ridge_stimulus": ["video", "caption"],   # NO brain
        "ridge_fusion": ["brain", "video", "caption"],
    }
    fitted = {}
    for name, keys in ridge_specs.items():
        Xtr = build_X(tr, scalers, keys)
        Xva = build_X(va, scalers, keys)
        Xte = build_X(te, scalers, keys)
        m, a, vpear = fit_ridge(Xtr, Ytr, Xva, Yva)
        pred = m.predict(Xte)
        results[name] = {**profile_pearson(pred, Yte), "alpha": a, "val_pearson": vpear}
        pcv[name] = per_clip_pearson_vec(pred, Yte)
        fitted[name] = (m, keys)

    # --- MLP cheap fusion (Arm A) -----------------------------------------
    keys = ["brain", "video", "caption"]
    Xtr = build_X(tr, scalers, keys)
    Xva = build_X(va, scalers, keys)
    Xte = build_X(te, scalers, keys)
    net, vpear = fit_mlp(Xtr, Ytr, Xva, Yva, device)
    pred = mlp_predict(net, Xte, device)
    results["mlp_fusion"] = {**profile_pearson(pred, Yte), "val_pearson": vpear}
    pcv["mlp_fusion"] = per_clip_pearson_vec(pred, Yte)

    # --- leakage / marginal-brain controls --------------------------------
    rng = np.random.default_rng(SEED)
    # (a) ridge_brain with brain permuted vs labels in BOTH train and test.
    perm_tr = rng.permutation(len(Ytr))
    perm_te = rng.permutation(len(Yte))
    Xtr_bs = scalers["brain"](tr["brain"][perm_tr])
    Xva_bs = scalers["brain"](va["brain"])  # val untouched for selection
    Xte_bs = scalers["brain"](te["brain"][perm_te])
    m, a, vpear = fit_ridge(Xtr_bs, Ytr, Xva_bs, Yva)
    pred = m.predict(Xte_bs)
    results["ridge_brain_shuffle"] = {**profile_pearson(pred, Yte), "alpha": a}
    pcv["ridge_brain_shuffle"] = per_clip_pearson_vec(pred, Yte)

    # (b) mlp_fusion with ONLY brain shuffled (video+caption real) -> marginal brain.
    tr_bs = {**tr, "brain": tr["brain"][perm_tr]}
    te_bs = {**te, "brain": te["brain"][perm_te]}
    Xtr2 = build_X(tr_bs, scalers, keys)
    Xva2 = build_X(va, scalers, keys)
    Xte2 = build_X(te_bs, scalers, keys)
    net2, vpear2 = fit_mlp(Xtr2, Ytr, Xva2, Yva, device)
    pred = mlp_predict(net2, Xte2, device)
    results["mlp_fusion_brainshuffle"] = {**profile_pearson(pred, Yte), "val_pearson": vpear2}
    pcv["mlp_fusion_brainshuffle"] = per_clip_pearson_vec(pred, Yte)

    # --- bootstrap CIs on the decisive differences ------------------------
    cis = {
        "fusion_vs_ridge_brain": bootstrap_ci(pcv["mlp_fusion"], pcv["ridge_brain"]),
        "fusion_vs_stimulus_only": bootstrap_ci(pcv["mlp_fusion"], pcv["ridge_stimulus"]),
        "ridge_brain_vs_floor": bootstrap_ci(pcv["ridge_brain"], pcv["mean_profile_floor"]),
        "brain_marginal_in_fusion": bootstrap_ci(pcv["mlp_fusion"], pcv["mlp_fusion_brainshuffle"]),
    }

    # --- report -----------------------------------------------------------
    order = ["mean_profile_floor", "ridge_brain", "ridge_brain_shuffle", "ridge_stimulus",
             "ridge_fusion", "mlp_fusion", "mlp_fusion_brainshuffle"]
    print("\n===== TEST per-clip 34D profile Pearson =====")
    print(f"{'model':28s} {'pearson':>9s} {'ccc':>8s}")
    for k in order:
        r = results[k]
        print(f"{k:28s} {r['pearson_mean']:>9.4f} {r.get('ccc_mean', float('nan')):>8.4f}")
    print("\n===== bootstrap 95% CI on mean per-clip difference =====")
    for k, (d, lo, hi) in cis.items():
        sig = "sig" if (lo > 0 or hi < 0) else "ns"
        print(f"{k:28s} d={d:+.4f}  CI[{lo:+.4f},{hi:+.4f}]  {sig}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"results": results, "bootstrap_ci": cis,
                               "device": device, "seed": SEED}, indent=2))
    print(f"\n[done] -> {OUT}")


if __name__ == "__main__":
    main()
