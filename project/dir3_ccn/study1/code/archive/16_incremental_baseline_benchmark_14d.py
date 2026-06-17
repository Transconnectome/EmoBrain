# -*- coding: utf-8 -*-
"""
CCN Analysis 16 (14D): baseline benchmark using 34 emotions + 14 dimensions.
"""

import warnings

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
    load_feature_table,
    load_metadata_frame,
    load_targets_14d,
    validate_alignment,
)

warnings.filterwarnings("ignore")

CCN_DIR = BASE / "CCN"
RESULTS_DIR = CCN_DIR / "results"
FIG_DIR = CCN_DIR / "figures"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

VJEPA_PATH = BASE / "video_embeddings" / "vjepa2_embeddings.npy"
CLIP_PATH = BASE / "video_embeddings" / "clip_embeddings.npy"
VISION_PATH = BASE / "vision_features.csv"
SEMANTIC_PATH = BASE / "semantic_features.csv"
PC_EMO_PATH = RESULTS_DIR / "pc_emotion_correlation.npz"

OUTPUT_PATH = RESULTS_DIR / "exp16_incremental_baseline_results_14d.npz"
BAR_FIG_PATH = FIG_DIR / "exp16_incremental_benchmark_14d.png"
SCATTER_FIG_PATH = FIG_DIR / "exp16_incremental_scatter_14d.png"

SEED = 42
N_PC = 100
CV = 5
R2_THRESH = 0.01
ALPHA = 1.0
TARGET_NAMES = EMOTION_LABELS + DIM14_LABELS


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
    print("Loading metadata and confound features...")
    meta = load_metadata_frame(HORIKAWA_META_14D_PATH)
    _, emotion_scores, dim_scores = load_targets_14d(HORIKAWA_META_14D_PATH)
    vision_df, vision_cols = load_feature_table(VISION_PATH)
    semantic_df, semantic_cols = load_feature_table(SEMANTIC_PATH)
    validate_alignment(
        meta["stim_idx"].to_numpy(),
        vision_df["stim_idx"].to_numpy(),
        semantic_df["stim_idx"].to_numpy(),
    )

    targets = np.hstack([emotion_scores, dim_scores])
    baseline_features = np.column_stack([
        vision_df[vision_cols].to_numpy(dtype=np.float64),
        semantic_df[semantic_cols].to_numpy(dtype=np.float64),
    ])
    print(f"  Metadata: {HORIKAWA_META_14D_PATH}")
    print(f"  Target matrix: {targets.shape}")

    pc_data = np.load(PC_EMO_PATH, allow_pickle=True)
    pred_idx_v = np.where(pc_data["r2_vjepa"] > R2_THRESH)[0]
    pred_idx_c = np.where(pc_data["r2_clip"] > R2_THRESH)[0]
    print(f"  V-JEPA2 pred PCs: {pred_idx_v + 1} (n={len(pred_idx_v)})")
    print(f"  CLIP pred PCs:    {pred_idx_c + 1} (n={len(pred_idx_c)})")

    vjepa_pcs = PCA(n_components=N_PC, random_state=SEED).fit_transform(np.load(VJEPA_PATH).astype(np.float64))
    clip_pcs = PCA(n_components=N_PC, random_state=SEED).fit_transform(np.load(CLIP_PATH).astype(np.float64))
    pred_vjepa = vjepa_pcs[:, pred_idx_v]
    pred_clip = clip_pcs[:, pred_idx_c]

    print("\nComputing 14D benchmark...")
    r2_baseline = compute_targetwise_r2(baseline_features, targets)
    r2_vjepa_only = compute_targetwise_r2(pred_vjepa, targets)
    r2_clip_only = compute_targetwise_r2(pred_clip, targets)
    r2_combined_vjepa = compute_targetwise_r2(np.column_stack([baseline_features, pred_vjepa]), targets)
    r2_combined_clip = compute_targetwise_r2(np.column_stack([baseline_features, pred_clip]), targets)
    delta_vjepa = r2_combined_vjepa - r2_baseline
    delta_clip = r2_combined_clip - r2_baseline

    print(f"\n{'=' * 72}")
    print("Summary: 14D baseline benchmark")
    print(f"{'=' * 72}")
    for name, values in [
        ("Baseline (vision+semantic)", r2_baseline),
        ("V-JEPA2 PCs only", r2_vjepa_only),
        ("CLIP PCs only", r2_clip_only),
        ("Baseline + V-JEPA2 PCs", r2_combined_vjepa),
        ("Baseline + CLIP PCs", r2_combined_clip),
    ]:
        s = summarize(values)
        print(
            f"{name:<28} mean_cat={s['mean_cat']:.4f}  "
            f"mean_dim14={s['mean_dim']:.4f}  cat/dim={s['cat_dim_ratio']:.3f}"
        )

    print(
        f"\nIncremental mean category R²: V-JEPA2={delta_vjepa[:len(EMOTION_LABELS)].mean():+.4f}  "
        f"CLIP={delta_clip[:len(EMOTION_LABELS)].mean():+.4f}"
    )
    print(
        f"Incremental mean 14D R²:      V-JEPA2={delta_vjepa[len(EMOTION_LABELS):].mean():+.4f}  "
        f"CLIP={delta_clip[len(EMOTION_LABELS):].mean():+.4f}"
    )

    top_v = np.argsort(delta_vjepa[: len(EMOTION_LABELS)])[-10:][::-1]
    top_c = np.argsort(delta_clip[: len(EMOTION_LABELS)])[-10:][::-1]
    print("\nTop 10 incremental emotions (Baseline+V-JEPA2 vs Baseline):")
    for idx in top_v:
        print(
            f"  {TARGET_NAMES[idx]:<24} baseline={r2_baseline[idx]:.4f}  "
            f"combined={r2_combined_vjepa[idx]:.4f}  Δ={delta_vjepa[idx]:+.4f}"
        )
    print("\nTop 10 incremental emotions (Baseline+CLIP vs Baseline):")
    for idx in top_c:
        print(
            f"  {TARGET_NAMES[idx]:<24} baseline={r2_baseline[idx]:.4f}  "
            f"combined={r2_combined_clip[idx]:.4f}  Δ={delta_clip[idx]:+.4f}"
        )

    np.savez(
        OUTPUT_PATH,
        metadata_path=np.array([str(HORIKAWA_META_14D_PATH)]),
        target_names=np.array(TARGET_NAMES),
        emotion_labels=np.array(EMOTION_LABELS),
        dim_labels=np.array(DIM14_LABELS),
        dim_cols=np.array(DIM14_COLS),
        pred_idx_vjepa=pred_idx_v,
        pred_idx_clip=pred_idx_c,
        r2_baseline=r2_baseline,
        r2_vjepa_only=r2_vjepa_only,
        r2_clip_only=r2_clip_only,
        r2_combined_vjepa=r2_combined_vjepa,
        r2_combined_clip=r2_combined_clip,
        delta_vjepa=delta_vjepa,
        delta_clip=delta_clip,
    )

    # Figure 1
    fig, axes = plt.subplots(2, 1, figsize=(20, 11))
    fig.patch.set_facecolor("white")
    dim_start = len(EMOTION_LABELS)
    divider_x = dim_start - 0.5
    for ax, delta, combined, label in [
        (axes[0], delta_vjepa, r2_combined_vjepa, "V-JEPA2"),
        (axes[1], delta_clip, r2_combined_clip, "CLIP"),
    ]:
        emo_pairs = sorted(
            [(TARGET_NAMES[i], r2_baseline[i], combined[i], delta[i]) for i in range(len(EMOTION_LABELS))],
            key=lambda x: x[3],
            reverse=True,
        )
        dim_pairs = [(TARGET_NAMES[i], r2_baseline[i], combined[i], delta[i]) for i in range(dim_start, len(TARGET_NAMES))]
        names = [p[0] for p in emo_pairs] + [""] + [p[0] for p in dim_pairs]
        base_vals = [p[1] for p in emo_pairs] + [0.0] + [p[1] for p in dim_pairs]
        comb_vals = [p[2] for p in emo_pairs] + [0.0] + [p[2] for p in dim_pairs]
        colors = ["steelblue"] * len(EMOTION_LABELS) + ["white"] + ["tomato"] * len(DIM14_LABELS)
        x = np.arange(len(names))
        ax.bar(x, base_vals, color="lightgray", alpha=0.7, label="Baseline (vision+semantic)")
        ax.bar(x, comb_vals, color=colors, alpha=0.85, label=f"Baseline + {label} PCs")
        ax.axvline(divider_x, color="black", linestyle=":", alpha=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=90, fontsize=7)
        ax.set_ylabel("R²")
        ax.set_title(f"Incremental benchmark (14D): baseline vs baseline+{label} PCs", fontweight="bold")
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(BAR_FIG_PATH, dpi=200, bbox_inches="tight")
    plt.close()

    # Figure 2
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("white")
    for ax, combined, label in [
        (axes[0], r2_combined_vjepa, "V-JEPA2"),
        (axes[1], r2_combined_clip, "CLIP"),
    ]:
        x_cat = r2_baseline[:dim_start]
        y_cat = combined[:dim_start]
        x_dim = r2_baseline[dim_start:]
        y_dim = combined[dim_start:]
        ax.scatter(x_cat, y_cat, color="steelblue", alpha=0.75, label="34 emotions")
        ax.scatter(x_dim, y_dim, color="tomato", marker="D", s=70, alpha=0.9, label="14 dimensions")
        lim = max(float(max(x_cat.max(), y_cat.max(), x_dim.max(), y_dim.max())), 1e-3)
        ax.plot([0, lim], [0, lim], "k--", alpha=0.5)
        ax.set_xlabel("Baseline R²")
        ax.set_ylabel(f"Baseline + {label} PCs R²")
        ax.set_title(f"{label}: incremental benchmark (14D)", fontweight="bold")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(SCATTER_FIG_PATH, dpi=200, bbox_inches="tight")
    plt.close()

    print("\nSaved:")
    print(f"  {OUTPUT_PATH}")
    print(f"  {BAR_FIG_PATH}")
    print(f"  {SCATTER_FIG_PATH}")


if __name__ == "__main__":
    main()
