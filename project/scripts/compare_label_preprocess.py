"""Compare 3 label preprocessing schemes on the B1 ridge baseline.

Schemes.
    zscore       raw -> per-emotion z-score (spec §5-2, current).
    log1p_z      raw -> log(1+raw) -> per-emotion z-score.
    zscore_clip  raw -> per-emotion z-score -> clip to [-3, 3].

For each scheme: fit per-emotion mu/std on TRAIN only, transform all splits,
ridge (alpha tuned on val by headline profile pearson), report test metrics.

This is a decision experiment. All schemes use identical source / split /
model; only label preprocessing differs. Ridge runs in minutes.

Run.
    bash project/scripts/compare_label_preprocess.sh
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from project.data.datasets import HorikawaDataset  # noqa: E402  (only for stim order via fmri)
from project.data.fmri_adapter import FmriAdapter
from project.evaluation.metrics import profile_correlation, per_emotion_correlation, rsa


DATA_DIR = REPO_ROOT / "project" / "shared" / "data"
LABELS_CSV = DATA_DIR / "cowen_horikawa_labels.csv"
SPLIT_CSV = DATA_DIR / "horikawa_split.csv"
SCORE_COLS = [f"score_{k}" for k in range(34)]
ALPHAS = [1.0, 10.0, 100.0, 1000.0, 10000.0]


def transform(raw: np.ndarray, mu: np.ndarray, sd: np.ndarray, scheme: str) -> np.ndarray:
    if scheme == "zscore":
        return (raw - mu) / sd
    if scheme == "log1p_z":
        return (np.log1p(raw) - mu) / sd
    if scheme == "zscore_clip":
        return np.clip((raw - mu) / sd, -3.0, 3.0)
    raise ValueError(scheme)


def fit_stats(raw_train: np.ndarray, scheme: str) -> tuple[np.ndarray, np.ndarray]:
    base = np.log1p(raw_train) if scheme == "log1p_z" else raw_train
    mu = base.mean(0)
    sd = base.std(0)
    sd = np.where(sd < 1e-8, 1.0, sd)
    return mu, sd


def build_fmri_and_labels():
    """Return per-split X (fmri mean) and raw labels aligned by sample order."""
    adapter = FmriAdapter()
    lbl = pd.read_csv(LABELS_CSV).set_index("stim_num_int")
    out = {}
    for split in ("train", "val", "test"):
        ds = HorikawaDataset(split=split, fmri_mode="mean", fmri_adapter=adapter)
        X = np.stack([ds[i]["fmri"].numpy() for i in range(len(ds))], 0).astype(np.float64)
        raw = np.stack(
            [lbl.loc[ds._samples[i].stim_num, SCORE_COLS].values.astype(np.float64) for i in range(len(ds))],
            axis=0,
        )
        out[split] = (X, raw)
    return out


def run_scheme(data, scheme: str) -> dict:
    Xtr, raw_tr = data["train"]
    Xva, raw_va = data["val"]
    Xte, raw_te = data["test"]

    mu, sd = fit_stats(raw_tr, scheme)
    Ytr = transform(raw_tr, mu, sd, scheme)
    Yva = transform(raw_va, mu, sd, scheme)
    Yte = transform(raw_te, mu, sd, scheme)

    # alpha tune on val
    best_alpha, best_val = None, -np.inf
    for alpha in ALPHAS:
        m = Ridge(alpha=alpha).fit(Xtr, Ytr)
        v = profile_correlation(m.predict(Xva), Yva)["pearson_mean"]
        if v > best_val:
            best_val, best_alpha = v, alpha

    model = Ridge(alpha=best_alpha).fit(Xtr, Ytr)
    pred = model.predict(Xte)
    prof = profile_correlation(pred, Yte)
    pe = per_emotion_correlation(pred, Yte)
    rs = rsa(pred, Yte)

    return {
        "scheme": scheme,
        "best_alpha": best_alpha,
        "target_z_max": float(np.abs(Ytr).max()),
        "target_z_p99": float(np.percentile(np.abs(Ytr), 99)),
        "profile_pearson": prof["pearson_mean"],
        "profile_spearman": prof["spearman_mean"],
        "per_emotion_mean": pe["mean"],
        "rsa": rs["rsa_pearson"],
    }


def main() -> None:
    print("[load] fmri + raw labels")
    data = build_fmri_and_labels()
    print(f"  train {data['train'][0].shape}  test {data['test'][0].shape}")

    rows = []
    for scheme in ("zscore", "log1p_z", "zscore_clip"):
        print(f"\n[run] scheme = {scheme}")
        r = run_scheme(data, scheme)
        rows.append(r)
        print(f"  best_alpha={r['best_alpha']}  target |z| max={r['target_z_max']:.1f} p99={r['target_z_p99']:.2f}")
        print(f"  profile pearson={r['profile_pearson']:+.4f}  spearman={r['profile_spearman']:+.4f}")
        print(f"  per-emotion={r['per_emotion_mean']:+.4f}  rsa={r['rsa']:+.4f}")

    print("\n" + "=" * 78)
    print(f"{'scheme':14s} {'|z|max':>7s} {'|z|p99':>7s} {'profileP':>9s} {'profileS':>9s} {'perEmo':>8s} {'rsa':>7s}")
    print("-" * 78)
    for r in rows:
        print(f"{r['scheme']:14s} {r['target_z_max']:7.1f} {r['target_z_p99']:7.2f} "
              f"{r['profile_pearson']:+9.4f} {r['profile_spearman']:+9.4f} "
              f"{r['per_emotion_mean']:+8.4f} {r['rsa']:+7.4f}")
    print("=" * 78)


if __name__ == "__main__":
    main()
