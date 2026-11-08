"""Ridge under 3 subject regimes: within / pooled / LOSO.

Goal. Disambiguate two readings of "ISC (0.23) < ridge (0.29)".
    Reading 1 (signal-limited). Ridge already extracts the subject-common
        signal; within ~ pooled ~ LOSO.
    Reading 2 (label-anchored). Labels are stimulus-fixed, so per-subject
        brain->label mapping helps; within > pooled > LOSO.

Regimes (all use the same stimulus-level train/val/test split so they are
comparable, and the same fMRI ROI mean + z-scored labels as B1).

    within   train on subject s's samples only, test on subject s's test
             samples. Averaged over 5 subjects.
    pooled   train on all 5 subjects (= B1 baseline), test on all.
    loso     train on 4 subjects, test on the held-out subject. Averaged over
             5 folds. (cross-subject generalization)

Headline compared across regimes = per-clip profile pearson (test).

Output.
    project/shared/results/noise_ceiling/ridge_subject_regimes.json

Run.
    bash project/scripts/ridge_subject_regimes.sh
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

from project.data.fmri_adapter import FmriAdapter, SUBJECTS
from project.data.labels import Cowen34Normalizer
from project.evaluation.metrics import profile_correlation, per_emotion_correlation

DATA_DIR = REPO_ROOT / "project" / "shared" / "data"
LABELS_CSV = DATA_DIR / "cowen_horikawa_labels.csv"
SPLIT_CSV = DATA_DIR / "horikawa_split.csv"
NORM = DATA_DIR / "norm_stats" / "cowen34_train.pt"
OUT_DIR = REPO_ROOT / "project" / "shared" / "results" / "noise_ceiling"
SCORE_COLS = [f"score_{k}" for k in range(34)]
ALPHAS = [1.0, 10.0, 100.0, 1000.0, 10000.0]


def build_pool():
    """Return dict subject -> {split -> (X (n,450), Y_z (n,34), stim_nums)}."""
    adapter = FmriAdapter()
    norm = Cowen34Normalizer.load(NORM)
    labels = pd.read_csv(LABELS_CSV).set_index("stim_num_int")
    split = pd.read_csv(SPLIT_CSV)

    data = {s: {} for s in SUBJECTS}
    for subj in SUBJECTS:
        rows = split[(split["subject"] == subj)]
        for sp in ("train", "val", "test"):
            stims = rows.loc[rows["split"] == sp, "stimulus_num"].astype(int).tolist()
            X = np.stack([adapter.get(subj, sn, "mean").numpy() for sn in stims], 0).astype(np.float64)
            raw = np.stack([labels.loc[sn, SCORE_COLS].values.astype(np.float64) for sn in stims], 0)
            Yz = norm.transform(raw).numpy()
            data[subj][sp] = (X, Yz, stims)
    return data


def tune_fit_eval(Xtr, Ytr, Xva, Yva, Xte, Yte):
    best_alpha, best_val = None, -np.inf
    for a in ALPHAS:
        m = Ridge(alpha=a).fit(Xtr, Ytr)
        v = profile_correlation(m.predict(Xva), Yva)["pearson_mean"]
        if v > best_val:
            best_val, best_alpha = v, a
    model = Ridge(alpha=best_alpha).fit(Xtr, Ytr)
    pred = model.predict(Xte)
    prof = profile_correlation(pred, Yte)
    pe = per_emotion_correlation(pred, Yte)
    return {"alpha": best_alpha, "profile_pearson": prof["pearson_mean"],
            "profile_spearman": prof["spearman_mean"], "per_emotion_mean": pe["mean"]}


def cat(parts, idx):
    return np.concatenate([p[idx] for p in parts], axis=0)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = build_pool()

    # ---- within-subject ----
    within = []
    for subj in SUBJECTS:
        d = data[subj]
        r = tune_fit_eval(d["train"][0], d["train"][1], d["val"][0], d["val"][1], d["test"][0], d["test"][1])
        within.append(r)
        print(f"[within] {subj}: profile={r['profile_pearson']:+.4f} (alpha {r['alpha']}, n_train={len(d['train'][0])})")
    within_mean = float(np.mean([r["profile_pearson"] for r in within]))

    # ---- pooled ----
    Xtr = cat([data[s]["train"] for s in SUBJECTS], 0)
    Ytr = cat([data[s]["train"] for s in SUBJECTS], 1)
    Xva = cat([data[s]["val"] for s in SUBJECTS], 0)
    Yva = cat([data[s]["val"] for s in SUBJECTS], 1)
    Xte = cat([data[s]["test"] for s in SUBJECTS], 0)
    Yte = cat([data[s]["test"] for s in SUBJECTS], 1)
    pooled = tune_fit_eval(Xtr, Ytr, Xva, Yva, Xte, Yte)
    print(f"\n[pooled] profile={pooled['profile_pearson']:+.4f} (alpha {pooled['alpha']}, n_train={len(Xtr)})")

    # ---- LOSO ----
    loso = []
    for held in SUBJECTS:
        others = [s for s in SUBJECTS if s != held]
        Xtr = cat([data[s]["train"] for s in others], 0)
        Ytr = cat([data[s]["train"] for s in others], 1)
        Xva = cat([data[s]["val"] for s in others], 0)
        Yva = cat([data[s]["val"] for s in others], 1)
        # test on held-out subject's test split
        Xte, Yte, _ = data[held]["test"]
        r = tune_fit_eval(Xtr, Ytr, Xva, Yva, Xte, Yte)
        loso.append(r)
        print(f"[loso] hold {held}: profile={r['profile_pearson']:+.4f} (alpha {r['alpha']})")
    loso_mean = float(np.mean([r["profile_pearson"] for r in loso]))

    out = {
        "within_mean": within_mean,
        "within_per_subject": [r["profile_pearson"] for r in within],
        "pooled": pooled["profile_pearson"],
        "loso_mean": loso_mean,
        "loso_per_fold": [r["profile_pearson"] for r in loso],
    }
    (OUT_DIR / "ridge_subject_regimes.json").write_text(json.dumps(out, indent=2))

    print("\n" + "=" * 60)
    print("SUBJECT REGIME COMPARISON (profile pearson)")
    print("=" * 60)
    print(f"  within-subject (avg 5)  = {within_mean:+.4f}")
    print(f"  pooled (5 subj)         = {pooled['profile_pearson']:+.4f}")
    print(f"  LOSO (avg 5 folds)      = {loso_mean:+.4f}")
    print("")
    print("  reading 1 (signal-limited): within ~ pooled ~ LOSO")
    print("  reading 2 (label-anchored): within > pooled > LOSO")
    print(f"\n[save] {OUT_DIR / 'ridge_subject_regimes.json'}")


if __name__ == "__main__":
    main()
