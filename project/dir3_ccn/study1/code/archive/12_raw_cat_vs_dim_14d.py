# -*- coding: utf-8 -*-
"""
CCN Analysis 12 (Raw fMRI, 14D)

Goal:
    Raw fMRI representation predicts 34 emotions + 14 affective dimensions.
    This is the raw-fMRI analogue of Exp 12, focused on category-vs-dimension
    decoding rather than brain-predictable model subspaces.

Outputs:
    results/raw_exp12_14d_results.npz
    figures/raw_exp12_14d_k_sweep.png
    figures/raw_exp12_14d_targets.png
"""

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ccn_dim14_metadata import (
    BASE,
    DIM14_COLS,
    DIM14_LABELS,
    EMOTION_LABELS,
    HORIKAWA_META_14D_PATH,
    load_targets_14d,
)

warnings.filterwarnings("ignore")

FMRI_PATH = BASE / "raw_fmri_results" / "fmri_raw.npy"
RESULTS_DIR = BASE / "CCN" / "results"
FIG_DIR = BASE / "CCN" / "figures"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = RESULTS_DIR / "raw_exp12_14d_results.npz"
KSWEEP_FIG = FIG_DIR / "raw_exp12_14d_k_sweep.png"
TARGET_FIG = FIG_DIR / "raw_exp12_14d_targets.png"

CV = 5
ALPHA = 1.0
K_VALUES = [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]
K_REFERENCE = 27


def ridge_r2(features, target):
    pipe = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=ALPHA))])
    return max(cross_val_score(pipe, features, target, cv=CV, scoring="r2").mean(), 0.0)


def compute_targetwise_r2(features, targets):
    out = np.zeros(targets.shape[1], dtype=np.float64)
    for i in range(targets.shape[1]):
        out[i] = ridge_r2(features, targets[:, i])
    return out


def summarize(values):
    emo = values[: len(EMOTION_LABELS)]
    dim = values[len(EMOTION_LABELS):]
    return {
        "mean_cat": float(emo.mean()),
        "mean_dim": float(dim.mean()),
        "cat_dim_ratio": float(emo.mean() / max(dim.mean(), 1e-10)),
    }


def main():
    print("Loading raw fMRI and 14D metadata...")
    fmri_raw = np.load(FMRI_PATH).astype(np.float64)  # (5, 2196, 450)
    fmri_mean = fmri_raw.mean(axis=0)                 # (2196, 450)
    _, emotion_scores, dim_scores = load_targets_14d(HORIKAWA_META_14D_PATH)
    targets = np.hstack([emotion_scores, dim_scores])
    target_names = EMOTION_LABELS + DIM14_LABELS

    print(f"  Raw fMRI mean: {fmri_mean.shape}")
    print(f"  Metadata:      {HORIKAWA_META_14D_PATH}")
    print(f"  Targets:       {targets.shape}")

    print("\nRunning raw-fMRI k-sweep for 34 emotions + 14 dimensions...")
    summary = {
        "k": [],
        "mean_cat": [],
        "mean_dim": [],
        "cat_dim_ratio": [],
    }
    targetwise_k = {}

    for k in K_VALUES:
        print(f"  k={k}")
        fmri_k = PCA(n_components=k, random_state=42).fit_transform(fmri_mean)
        r2_k = compute_targetwise_r2(fmri_k, targets)
        targetwise_k[k] = r2_k
        s = summarize(r2_k)
        summary["k"].append(k)
        summary["mean_cat"].append(s["mean_cat"])
        summary["mean_dim"].append(s["mean_dim"])
        summary["cat_dim_ratio"].append(s["cat_dim_ratio"])
        print(
            f"    mean_cat={s['mean_cat']:.4f}  mean_dim14={s['mean_dim']:.4f}  "
            f"cat/dim={s['cat_dim_ratio']:.3f}"
        )

    print("\nComputing full raw-fMRI decoding (450 features)...")
    r2_full = compute_targetwise_r2(fmri_mean, targets)
    s_full = summarize(r2_full)
    print(
        f"  full mean_cat={s_full['mean_cat']:.4f}  mean_dim14={s_full['mean_dim']:.4f}  "
        f"cat/dim={s_full['cat_dim_ratio']:.3f}"
    )

    k_ref = K_REFERENCE
    if k_ref not in targetwise_k:
        raise ValueError(f"k={k_ref} missing from K_VALUES")
    r2_ref = targetwise_k[k_ref]
    s_ref = summarize(r2_ref)

    print(f"\n{'=' * 72}")
    print("RAW fMRI Exp12-style summary (14D)")
    print(f"{'=' * 72}")
    print(
        f"k={k_ref:<3} mean_cat={s_ref['mean_cat']:.4f}  mean_dim14={s_ref['mean_dim']:.4f}  "
        f"cat/dim={s_ref['cat_dim_ratio']:.3f}"
    )
    print(
        f"full  mean_cat={s_full['mean_cat']:.4f}  mean_dim14={s_full['mean_dim']:.4f}  "
        f"cat/dim={s_full['cat_dim_ratio']:.3f}"
    )

    top_emo_ref = np.argsort(r2_ref[: len(EMOTION_LABELS)])[-10:][::-1]
    top_dim_ref = np.argsort(r2_ref[len(EMOTION_LABELS):])[-10:][::-1]
    print("\nTop 10 emotions at k=27:")
    for idx in top_emo_ref:
        print(f"  {target_names[idx]:<24} k27={r2_ref[idx]:.4f}  full={r2_full[idx]:.4f}")
    print("\nTop 10 dimensions at k=27:")
    for idx in top_dim_ref:
        di = len(EMOTION_LABELS) + idx
        print(f"  {target_names[di]:<24} k27={r2_ref[di]:.4f}  full={r2_full[di]:.4f}")

    np.savez(
        OUTPUT_PATH,
        metadata_path=np.array([str(HORIKAWA_META_14D_PATH)]),
        fmri_path=np.array([str(FMRI_PATH)]),
        target_names=np.array(target_names),
        emotion_labels=np.array(EMOTION_LABELS),
        dim_labels=np.array(DIM14_LABELS),
        dim_cols=np.array(DIM14_COLS),
        k_values=np.array(K_VALUES, dtype=np.int64),
        mean_cat=np.array(summary["mean_cat"], dtype=np.float64),
        mean_dim=np.array(summary["mean_dim"], dtype=np.float64),
        cat_dim_ratio=np.array(summary["cat_dim_ratio"], dtype=np.float64),
        r2_k27=r2_ref,
        r2_full=r2_full,
    )

    # Figure 1: k-sweep summary
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor("white")

    axes[0].plot(summary["k"], summary["mean_cat"], "o-", color="steelblue", label="34 emotions")
    axes[0].plot(summary["k"], summary["mean_dim"], "o-", color="tomato", label="14 dimensions")
    axes[0].axvline(k_ref, color="gray", linestyle="--", alpha=0.7, label=f"k={k_ref}")
    axes[0].set_xlabel("Number of PCA dimensions (k)")
    axes[0].set_ylabel("Mean R²")
    axes[0].set_title("Raw fMRI: mean category vs dimension decoding", fontweight="bold")
    axes[0].grid(alpha=0.3)
    axes[0].legend(fontsize=8)

    axes[1].plot(summary["k"], summary["cat_dim_ratio"], "o-", color="black")
    axes[1].axhline(1.0, color="gray", linestyle="--", alpha=0.7)
    axes[1].axvline(k_ref, color="gray", linestyle="--", alpha=0.7)
    axes[1].set_xlabel("Number of PCA dimensions (k)")
    axes[1].set_ylabel("Category/dimension ratio")
    axes[1].set_title("Raw fMRI: category-vs-dimension balance", fontweight="bold")
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(KSWEEP_FIG, dpi=200, bbox_inches="tight")
    plt.close()

    # Figure 2: target-wise k=27 vs full
    fig, axes = plt.subplots(2, 1, figsize=(20, 10))
    fig.patch.set_facecolor("white")
    divider = len(EMOTION_LABELS) - 0.5

    for ax, values, title in [
        (axes[0], r2_ref, f"Raw fMRI PCA k={k_ref}"),
        (axes[1], r2_full, "Raw fMRI full 450D"),
    ]:
        emo_pairs = sorted(
            [(name, values[i]) for i, name in enumerate(EMOTION_LABELS)],
            key=lambda x: x[1],
            reverse=True,
        )
        dim_pairs = [(name, values[len(EMOTION_LABELS) + i]) for i, name in enumerate(DIM14_LABELS)]
        names = [p[0] for p in emo_pairs] + [""] + [p[0] for p in dim_pairs]
        vals = [p[1] for p in emo_pairs] + [0.0] + [p[1] for p in dim_pairs]
        colors = ["steelblue"] * len(EMOTION_LABELS) + ["white"] + ["tomato"] * len(DIM14_LABELS)
        x = np.arange(len(names))
        ax.bar(x, vals, color=colors, alpha=0.85)
        ax.axvline(divider, color="black", linestyle=":", alpha=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=90, fontsize=7)
        ax.set_ylabel("R²")
        ax.set_title(
            f"{title}: 34 emotions + 14 dimensions | "
            f"mean_cat={summarize(values)['mean_cat']:.4f}, mean_dim14={summarize(values)['mean_dim']:.4f}",
            fontweight="bold",
        )
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(TARGET_FIG, dpi=200, bbox_inches="tight")
    plt.close()

    print("\nSaved:")
    print(f"  {OUTPUT_PATH}")
    print(f"  {KSWEEP_FIG}")
    print(f"  {TARGET_FIG}")


if __name__ == "__main__":
    main()
