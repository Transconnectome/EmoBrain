# -*- coding: utf-8 -*-
"""
CCN Analysis 12 (14D): Brain-predictable subspace vs 34 emotion categories + 14 dimensions.
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

VJEPA_PATH = BASE / "video_embeddings" / "vjepa2_embeddings.npy"
CLIP_PATH = BASE / "video_embeddings" / "clip_embeddings.npy"
PC_EMO_PATH = BASE / "CCN" / "results" / "pc_emotion_correlation.npz"
OUTPUT_DIR = BASE / "CCN" / "results"
FIG_DIR = BASE / "CCN" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "brain_pred_subspace_prediction_14d.npz"
FIG_R2 = FIG_DIR / "brain_pred_subspace_r2_all_14d.png"
FIG_SCATTER = FIG_DIR / "brain_pred_subspace_scatter_14d.png"
FIG_EFF = FIG_DIR / "brain_pred_efficiency_14d.png"

N_PC = 100
R2_THRESH = 0.01
CV = 5


def ridge_r2(features, target):
    pipe = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=1.0))])
    return max(cross_val_score(pipe, features, target, cv=CV, scoring="r2").mean(), 0.0)


def results_to_arrays(result_dict, target_names):
    return {
        "pred": np.array([result_dict["pred"][t] for t in target_names]),
        "unpred": np.array([result_dict["unpred"][t] for t in target_names]),
        "all": np.array([result_dict["all"][t] for t in target_names]),
    }


def main():
    print("Loading embeddings and 14D metadata...")
    vjepa = np.load(VJEPA_PATH).astype(np.float64)
    clip_emb = np.load(CLIP_PATH).astype(np.float64)
    _, emotion_scores, dim_scores = load_targets_14d(HORIKAWA_META_14D_PATH)

    pc_data = np.load(PC_EMO_PATH, allow_pickle=True)
    pred_idx_v = np.where(pc_data["r2_vjepa"] > R2_THRESH)[0]
    pred_idx_c = np.where(pc_data["r2_clip"] > R2_THRESH)[0]
    unpred_idx_v = np.where(pc_data["r2_vjepa"] <= R2_THRESH)[0]
    unpred_idx_c = np.where(pc_data["r2_clip"] <= R2_THRESH)[0]

    print(f"  V-JEPA2 pred PCs: {pred_idx_v + 1} (n={len(pred_idx_v)})")
    print(f"  CLIP    pred PCs: {pred_idx_c + 1} (n={len(pred_idx_c)})")
    print(f"  Metadata: {HORIKAWA_META_14D_PATH}")

    vjepa_pcs = PCA(n_components=N_PC, random_state=42).fit_transform(vjepa)
    clip_pcs = PCA(n_components=N_PC, random_state=42).fit_transform(clip_emb)

    target_names = EMOTION_LABELS + DIM14_LABELS
    target_matrix = np.hstack([emotion_scores, dim_scores])

    features = {
        "vjepa": {
            "pred": vjepa_pcs[:, pred_idx_v],
            "unpred": vjepa_pcs[:, unpred_idx_v],
            "all": vjepa_pcs,
        },
        "clip": {
            "pred": clip_pcs[:, pred_idx_c],
            "unpred": clip_pcs[:, unpred_idx_c],
            "all": clip_pcs,
        },
    }

    results = {}
    for model_key in ["vjepa", "clip"]:
        print(f"\nComputing {model_key}...")
        results[model_key] = {k: {} for k in ["pred", "unpred", "all"]}
        for subspace in ["pred", "unpred", "all"]:
            feats = features[model_key][subspace]
            print(f"  [{subspace}, {feats.shape[1]} PCs]")
            for ti, target_name in enumerate(target_names):
                results[model_key][subspace][target_name] = ridge_r2(feats, target_matrix[:, ti])
            cat_mean = np.mean([results[model_key][subspace][e] for e in EMOTION_LABELS])
            dim_mean = np.mean([results[model_key][subspace][d] for d in DIM14_LABELS])
            print(
                f"    mean R² cat={cat_mean:.4f}  dim14={dim_mean:.4f}  "
                f"ratio(cat/dim)={cat_mean / max(dim_mean, 1e-10):.2f}"
            )

    # Figure 1
    fig, axes = plt.subplots(2, 1, figsize=(20, 11))
    fig.patch.set_facecolor("white")
    divider_x = len(EMOTION_LABELS) - 0.5
    for ax, model_key, label, pred_idx in [
        (axes[0], "vjepa", "V-JEPA2", pred_idx_v),
        (axes[1], "clip", "CLIP", pred_idx_c),
    ]:
        r = results[model_key]
        emo_pairs = sorted(
            [(name, r["pred"][name]) for name in EMOTION_LABELS],
            key=lambda x: x[1],
            reverse=True,
        )
        dim_pairs = [(name, r["pred"][name]) for name in DIM14_LABELS]
        names = [row[0] for row in emo_pairs] + [""] + [row[0] for row in dim_pairs]
        pred_vals = [row[1] for row in emo_pairs] + [0.0] + [row[1] for row in dim_pairs]
        all_vals = [r["all"][row[0]] for row in emo_pairs] + [0.0] + [r["all"][row[0]] for row in dim_pairs]
        colors = ["steelblue"] * len(EMOTION_LABELS) + ["white"] + ["tomato"] * len(DIM14_LABELS)
        x = np.arange(len(names))

        ax.bar(x, all_vals, color="lightgray", alpha=0.6, label="All 100 PCs")
        ax.bar(x, pred_vals, color=colors, alpha=0.85, label=f"Brain-pred subspace (n={len(pred_idx)} PCs)")
        ax.axvline(divider_x, color="black", linestyle=":", alpha=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=90, fontsize=7)
        ax.set_ylabel("R² (5-fold CV Ridge)")
        ax.set_title(f"{label}: prediction of 34 emotions + 14 dimensions", fontweight="bold")
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=8, loc="upper right")

    plt.tight_layout()
    plt.savefig(FIG_R2, dpi=200, bbox_inches="tight")
    plt.close()

    # Figure 2
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("white")
    for ax, model_key, label, pred_idx in [
        (axes[0], "vjepa", "V-JEPA2", pred_idx_v),
        (axes[1], "clip", "CLIP", pred_idx_c),
    ]:
        r = results[model_key]
        x_cat = [r["all"][e] for e in EMOTION_LABELS]
        y_cat = [r["pred"][e] for e in EMOTION_LABELS]
        x_dim = [r["all"][d] for d in DIM14_LABELS]
        y_dim = [r["pred"][d] for d in DIM14_LABELS]
        ax.scatter(x_cat, y_cat, color="steelblue", alpha=0.7, s=45, label="34 emotions")
        ax.scatter(x_dim, y_dim, color="tomato", alpha=0.85, s=60, marker="D", label="14 dimensions")
        lim = max(max(x_cat + x_dim), max(y_cat + y_dim)) * 1.05 if (x_cat + x_dim + y_cat + y_dim) else 1.0
        ax.plot([0, lim], [0, lim], "k--", alpha=0.4)
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        ax.set_xlabel("R² from all 100 PCs")
        ax.set_ylabel(f"R² from brain-pred {len(pred_idx)} PCs")
        ax.set_title(f"{label}: pred subspace vs full subspace", fontweight="bold")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(FIG_SCATTER, dpi=200, bbox_inches="tight")
    plt.close()

    # Figure 3
    fig, axes = plt.subplots(2, 1, figsize=(20, 10))
    fig.patch.set_facecolor("white")
    for ax, model_key, label, pred_idx in [
        (axes[0], "vjepa", "V-JEPA2", pred_idx_v),
        (axes[1], "clip", "CLIP", pred_idx_c),
    ]:
        r = results[model_key]
        emo_pairs = sorted(
            [(name, r["pred"][name]) for name in EMOTION_LABELS],
            key=lambda x: x[1],
            reverse=True,
        )
        dim_pairs = [(name, r["pred"][name]) for name in DIM14_LABELS]
        names = [row[0] for row in emo_pairs] + [""] + [row[0] for row in dim_pairs]
        eff_cat = [min(r["pred"][row[0]] / max(r["all"][row[0]], 1e-6), 1.0) for row in emo_pairs]
        eff_dim = [min(r["pred"][d] / max(r["all"][d], 1e-6), 1.0) for d in DIM14_LABELS]
        eff_all = eff_cat + [0.0] + eff_dim
        colors = ["steelblue"] * len(EMOTION_LABELS) + ["white"] + ["tomato"] * len(DIM14_LABELS)
        x = np.arange(len(names))

        ax.bar(x, eff_all, color=colors, alpha=0.85)
        ax.axvline(divider_x, color="black", linestyle=":", alpha=0.5)
        ax.axhline(1.0, color="gray", linestyle="--", alpha=0.4)
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=90, fontsize=7)
        ax.set_ylim(0, 1.1)
        ax.set_ylabel("Efficiency: R²(pred) / R²(all)")
        ax.set_title(f"{label}: efficiency of brain-predictable subspace", fontweight="bold")
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(FIG_EFF, dpi=200, bbox_inches="tight")
    plt.close()

    rv = results_to_arrays(results["vjepa"], target_names)
    rc = results_to_arrays(results["clip"], target_names)
    np.savez(
        OUTPUT_PATH,
        metadata_path=np.array([str(HORIKAWA_META_14D_PATH)]),
        target_names=np.array(target_names),
        emotion_labels=np.array(EMOTION_LABELS),
        dim_labels=np.array(DIM14_LABELS),
        dim_cols=np.array(DIM14_COLS),
        r2_pred_vjepa=rv["pred"],
        r2_unpred_vjepa=rv["unpred"],
        r2_all_vjepa=rv["all"],
        pred_idx_vjepa=pred_idx_v,
        r2_pred_clip=rc["pred"],
        r2_unpred_clip=rc["unpred"],
        r2_all_clip=rc["all"],
        pred_idx_clip=pred_idx_c,
    )
    print("\nSaved:")
    print(f"  {OUTPUT_PATH}")
    print(f"  {FIG_R2}")
    print(f"  {FIG_SCATTER}")
    print(f"  {FIG_EFF}")


if __name__ == "__main__":
    main()
