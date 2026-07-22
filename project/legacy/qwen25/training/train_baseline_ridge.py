"""B1 baseline. Ridge regression from fMRI ROI mean to 34D emotion (NO LLM).

Implementation of `docs/notes/implementation_spec_20260702.md` §7-1.

This is the controlled reference baseline. Same source, preprocessing, split,
z-score, and metrics as the main experiments; only the model differs (a plain
per-emotion ridge instead of an encoder + LLM). It is NOT a floor to beat but a
same-axis reference for the 34D task.

Pipeline.
    X = fMRI ROI mean (N, 450)      via HorikawaDataset(fmri_mode="mean")
    Y = z-scored 34D label (N, 34)  same normalizer as everything else
    Ridge (multi-output) fit on train, alpha tuned on val (headline metric),
    reported on test with the full metric suite.

Rare emotions.
    The 10 emotions with the lowest train marginal mean (raw score) are the
    rare subset for per-emotion recovery reporting.

Output.
    project/shared/results/baseline/b1_ridge_metrics.json
    project/shared/results/baseline/b1_ridge_pred_test.npy

Run.
    bash project/scripts/train_baseline_ridge.sh
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

from project.data.datasets import HorikawaDataset
from project.data.fmri_adapter import FmriAdapter
from project.data.labels import Cowen34Normalizer
from project.evaluation.metrics import compute_metrics


DATA_DIR = REPO_ROOT / "project" / "shared" / "data"
LABELS_CSV = DATA_DIR / "cowen_horikawa_labels.csv"
OUT_DIR = REPO_ROOT / "project" / "shared" / "results" / "baseline"

SCORE_COLS = [f"score_{k}" for k in range(34)]
ALPHAS = [1.0, 10.0, 100.0, 1000.0, 10000.0]
N_RARE = 10


def load_xy(split: str, adapter: FmriAdapter) -> tuple[np.ndarray, np.ndarray]:
    ds = HorikawaDataset(split=split, fmri_mode="mean", fmri_adapter=adapter)
    X = np.stack([ds[i]["fmri"].numpy() for i in range(len(ds))], axis=0)
    Y = np.stack([ds[i]["label"].numpy() for i in range(len(ds))], axis=0)
    return X.astype(np.float64), Y.astype(np.float64)


def rare_emotion_idx() -> list[int]:
    """10 emotions with the lowest train marginal mean (raw fraction)."""
    labels = pd.read_csv(LABELS_CSV)
    marginal = labels[SCORE_COLS].mean(axis=0).values  # (34,)
    return list(np.argsort(marginal)[:N_RARE])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    adapter = FmriAdapter()

    print("[load] train / val / test")
    Xtr, Ytr = load_xy("train", adapter)
    Xva, Yva = load_xy("val", adapter)
    Xte, Yte = load_xy("test", adapter)
    print(f"  train {Xtr.shape} val {Xva.shape} test {Xte.shape}")

    rare_idx = rare_emotion_idx()
    print(f"[rare] idx = {rare_idx}")

    # Alpha tuning on val by headline profile Pearson.
    print("[tune] alpha on val (headline = profile pearson)")
    best_alpha, best_val = None, -np.inf
    for alpha in ALPHAS:
        model = Ridge(alpha=alpha)
        model.fit(Xtr, Ytr)
        pred_va = model.predict(Xva)
        m = compute_metrics(pred_va, Yva, which=["profile"])
        val_score = m["profile"]["pearson_mean"]
        print(f"  alpha={alpha:>8.1f}  val profile pearson = {val_score:+.4f}")
        if val_score > best_val:
            best_val, best_alpha = val_score, alpha
    print(f"[tune] best alpha = {best_alpha} (val profile pearson {best_val:+.4f})")

    # Refit train and report on test.
    model = Ridge(alpha=best_alpha)
    model.fit(Xtr, Ytr)
    pred_te = model.predict(Xte)

    norm = Cowen34Normalizer.load(REPO_ROOT / "project" / "shared" / "data" / "norm_stats" / "cowen34_train.pt")
    metrics = compute_metrics(pred_te, Yte, rare_idx=rare_idx, normalizer=norm)
    metrics["config"] = {"best_alpha": best_alpha, "val_profile_pearson": best_val,
                         "n_train": int(Xtr.shape[0]), "n_test": int(Xte.shape[0]),
                         "rare_idx": [int(i) for i in rare_idx]}

    (OUT_DIR / "b1_ridge_metrics.json").write_text(json.dumps(metrics, indent=2))
    np.save(OUT_DIR / "b1_ridge_pred_test.npy", pred_te)

    # Report
    prof = metrics["profile"]
    err = metrics["error"]
    pe = metrics["per_emotion"]
    sp = metrics["sparse"]
    print("")
    print("=" * 64)
    print("B1 RIDGE (LLM 없음) — TEST RESULT")
    print("=" * 64)
    print("  -- headline (profile shape) --")
    print(f"  profile pearson mean/median = {prof['pearson_mean']:+.4f} / {prof['pearson_median']:+.4f}")
    print(f"  profile CCC  mean           = {prof['ccc_mean']:+.4f}   (< pearson => value/scale mismatch)")
    print(f"  profile spearman mean       = {prof['spearman_mean']:+.4f}")
    print(f"  profile cosine mean         = {prof['cosine_mean']:+.4f}")
    print("  -- absolute error --")
    print(f"  MSE (z)  = {err['mse_z']:.4f}   vs all-zero {err['zero_pred_mse_z']:.4f}   (improve {err['mse_improve_vs_zero']:+.4f})")
    print(f"  MAE (z)  = {err['mae_z']:.4f}   R2 = {err['r2_mean_z']:+.4f}")
    print(f"  MSE (raw)= {err['mse_raw']:.5f}   MAE (raw) = {err['mae_raw']:.5f}")
    print("  -- per-emotion --")
    print(f"  per-emotion pearson mean/median = {pe['mean']:+.4f} / {pe['median']:+.4f}")
    print(f"  per-emotion CCC mean            = {pe['ccc_mean']:+.4f}")
    print(f"  per-emotion range [{pe['min']:+.3f}, {pe['max']:+.3f}]")
    print(f"  rare-emotion pearson / CCC      = {pe['rare_mean']:+.4f} / {pe['rare_ccc_mean']:+.4f}")
    print("  -- structure / sparse --")
    print(f"  RSA (34x34)  = {metrics['rsa']['rsa_pearson']:+.4f}")
    print(f"  sparse retrieval  p@1={sp['precision@1']:.3f}  p@3={sp['precision@3']:.3f}  p@5={sp['precision@5']:.3f}")
    print(f"  dim-compression pearson@k = {[round(x,3) for x in metrics['dim_compression']['pearson_at_k']]}")
    print(f"                        ks  = {metrics['dim_compression']['ks']}")
    print("")
    print(f"[save] {OUT_DIR / 'b1_ridge_metrics.json'}")


if __name__ == "__main__":
    main()
