"""Fit the E2 ridge encoder (ROI 450 -> 34D z-label) on train, freeze, save.

E2 uses a ridge regressor as a fixed brain feature extractor: fit closed-form
on train (alpha tuned on val, same as B1), then the frozen 34D "ridge latent"
feeds the projector -> LLM. Output = coef (34,450) + intercept (34) saved to
project/shared/data/ridge_encoder.pt, loaded by encoders/ridge_latent.py.

Run.
    bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/fit_ridge_encoder.sh
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402
from sklearn.linear_model import Ridge  # noqa: E402

from project.data.fmri_adapter import FmriAdapter  # noqa: E402
from project.data.labels import Cowen34Normalizer  # noqa: E402
from project.evaluation.metrics import compute_metrics  # noqa: E402
from project.training.train_modality_solo import (  # noqa: E402
    split_stims, brain_features, labels_for, LABELS_CSV, NORM)

ALPHAS = [1.0, 10.0, 100.0, 1000.0, 10000.0]
OUT = REPO_ROOT / "project/shared/data/ridge_encoder.pt"


def main():
    adapter = FmriAdapter()
    norm = Cowen34Normalizer.load(NORM)
    labels_df = pd.read_csv(LABELS_CSV).set_index("stim_num_int")
    stims = split_stims()
    X = {sp: brain_features(stims[sp], adapter) for sp in ("train", "val")}
    Y = {sp: labels_for(stims[sp], norm, labels_df) for sp in ("train", "val")}

    best_a, best_v = None, -1e9
    for a in ALPHAS:
        m = Ridge(alpha=a).fit(X["train"], Y["train"])
        v = compute_metrics(m.predict(X["val"]), Y["val"],
                            which=["profile"])["profile"]["pearson_mean"]
        print(f"  alpha={a:>8.1f}  val pearson={v:+.4f}")
        if v > best_v:
            best_v, best_a = v, a
    model = Ridge(alpha=best_a).fit(X["train"], Y["train"])
    print(f"[fit] best alpha={best_a} (val pearson {best_v:+.4f})")

    torch.save({
        "coef": model.coef_.astype(np.float32),          # (34, 450)
        "intercept": model.intercept_.astype(np.float32),  # (34,)
        "alpha": best_a,
    }, OUT)
    print(f"[done] saved {OUT}  coef{model.coef_.shape} intercept{model.intercept_.shape}")


if __name__ == "__main__":
    main()
