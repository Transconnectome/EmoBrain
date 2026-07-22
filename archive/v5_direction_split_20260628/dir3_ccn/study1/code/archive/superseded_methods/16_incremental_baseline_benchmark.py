# -*- coding: utf-8 -*-
"""
CCN Analysis 16: Baseline benchmark (vision/semantic only vs model PCs)

Goal:
    Test whether brain-predictable model PCs add predictive value beyond
    explicit vision + semantic features.

Models:
    A. Vision + Semantic                        -> emotion / AVD
    Bv. V-JEPA2 brain-predictable PCs           -> emotion / AVD
    Bc. CLIP brain-predictable PCs              -> emotion / AVD
    Cv. Vision + Semantic + V-JEPA2 PCs         -> emotion / AVD
    Cc. Vision + Semantic + CLIP PCs            -> emotion / AVD

Key quantities:
    Incremental R²:
      Δ_vjepa = R²(vision+semantic+vjepa_pcs) - R²(vision+semantic)
      Δ_clip  = R²(vision+semantic+clip_pcs)  - R²(vision+semantic)

Outputs:
    results/exp16_incremental_baseline_results.npz
    figures/exp16_incremental_benchmark.png
    figures/exp16_incremental_scatter.png
"""

from pathlib import Path
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
CCN_DIR = BASE / "CCN"
RESULTS_DIR = CCN_DIR / "results"
FIG_DIR = CCN_DIR / "figures"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

VJEPA_PATH = BASE / "video_embeddings" / "vjepa2_embeddings.npy"
CLIP_PATH = BASE / "video_embeddings" / "clip_embeddings.npy"
VISION_PATH = BASE / "vision_features.csv"
SEMANTIC_PATH = BASE / "semantic_features.csv"
META_PATH = Path(
    "/pscratch/sd/s/sjmoon/Horikawa_embedding/"
    "horikawa_filtered_MNI_to_TRs/metadata/"
    "horikawa_meta_data_with_dimension_binary.csv"
)
PC_EMO_PATH = RESULTS_DIR / "pc_emotion_correlation.npz"

OUTPUT_PATH = RESULTS_DIR / "exp16_incremental_baseline_results.npz"
BAR_FIG_PATH = FIG_DIR / "exp16_incremental_benchmark.png"
SCATTER_FIG_PATH = FIG_DIR / "exp16_incremental_scatter.png"

# ── Constants ─────────────────────────────────────────────────────────────────
SEED = 42
N_PC = 100
CV = 5
R2_THRESH = 0.01
ALPHA = 1.0
EMOTION_LABELS = [
    "Admiration", "Adoration", "Aesthetic appreciation", "Amusement", "Anger",
    "Anxiety", "Awe", "Awkwardness", "Boredom", "Calmness", "Confusion",
    "Contempt", "Craving", "Disgust", "Empathic pain", "Entrancement",
    "Excitement", "Fear", "Horror", "Interest", "Joy", "Nostalgia", "Relief",
    "Romance", "Sadness", "Satisfaction", "Sexual desire", "Surprise",
    "Sympathy", "Triumph", "Uncomfortable", "Annoyance", "Envy", "Guilt",
]
DIM_LABELS = ["Arousal", "Valence", "Dominance"]
TARGET_NAMES = EMOTION_LABELS + DIM_LABELS


def strip_bom_columns(df):
    df.columns = [str(col).replace("\ufeff", "") for col in df.columns]
    return df


def extract_stimulus_idx(values):
    return (
        pd.Series(values)
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype(int)
        .to_numpy()
        - 1
    )


def load_feature_table(path):
    df = strip_bom_columns(pd.read_csv(path))
    stim_col = df.columns[0]
    df["stim_idx"] = extract_stimulus_idx(df[stim_col])
    df = df.sort_values("stim_idx").reset_index(drop=True)
    feature_cols = [c for c in df.columns if c not in {stim_col, "stim_idx"}]
    return df, feature_cols


def load_metadata():
    meta = strip_bom_columns(pd.read_csv(META_PATH))
    stim_col = "stimulus_num" if "stimulus_num" in meta.columns else meta.columns[0]
    meta["stim_idx"] = extract_stimulus_idx(meta[stim_col])
    meta = meta.sort_values("stim_idx").reset_index(drop=True)
    emo = meta[[f"score_{i}" for i in range(34)]].to_numpy(dtype=np.float64)
    avd = meta[["arousal_score", "valence_score", "dominance_score"]].to_numpy(dtype=np.float64)
    return meta, emo, avd


def validate_alignment(reference_idx, *other_idx):
    for idx in other_idx:
        if len(reference_idx) != len(idx) or not np.array_equal(reference_idx, idx):
            raise ValueError("Stimulus order mismatch across tables.")


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
    meta, emotion_scores, avd_scores = load_metadata()
    vision_df, vision_cols = load_feature_table(VISION_PATH)
    semantic_df, semantic_cols = load_feature_table(SEMANTIC_PATH)

    validate_alignment(
        meta["stim_idx"].to_numpy(),
        vision_df["stim_idx"].to_numpy(),
        semantic_df["stim_idx"].to_numpy(),
    )

    targets = np.hstack([emotion_scores, avd_scores])
    vision = vision_df[vision_cols].to_numpy(dtype=np.float64)
    semantic = semantic_df[semantic_cols].to_numpy(dtype=np.float64)
    baseline_features = np.column_stack([vision, semantic])

    print("Loading embeddings and brain-predictable PC masks...")
    vjepa_emb = np.load(VJEPA_PATH).astype(np.float64)
    clip_emb = np.load(CLIP_PATH).astype(np.float64)
    pc_data = np.load(PC_EMO_PATH, allow_pickle=True)
    pred_idx_v = np.where(pc_data["r2_vjepa"] > R2_THRESH)[0]
    pred_idx_c = np.where(pc_data["r2_clip"] > R2_THRESH)[0]

    print(f"  V-JEPA2 pred PCs: {pred_idx_v + 1} (n={len(pred_idx_v)})")
    print(f"  CLIP pred PCs:    {pred_idx_c + 1} (n={len(pred_idx_c)})")

    print("Fitting PCA (100 components)...")
    vjepa_pcs = PCA(n_components=N_PC, random_state=SEED).fit_transform(vjepa_emb)
    clip_pcs = PCA(n_components=N_PC, random_state=SEED).fit_transform(clip_emb)
    pred_vjepa = vjepa_pcs[:, pred_idx_v]
    pred_clip = clip_pcs[:, pred_idx_c]

    print("\nComputing baseline benchmark...")
    r2_baseline = compute_targetwise_r2(baseline_features, targets)
    r2_vjepa_only = compute_targetwise_r2(pred_vjepa, targets)
    r2_clip_only = compute_targetwise_r2(pred_clip, targets)
    r2_combined_vjepa = compute_targetwise_r2(np.column_stack([baseline_features, pred_vjepa]), targets)
    r2_combined_clip = compute_targetwise_r2(np.column_stack([baseline_features, pred_clip]), targets)

    delta_vjepa = r2_combined_vjepa - r2_baseline
    delta_clip = r2_combined_clip - r2_baseline

    print(f"\n{'=' * 72}")
    print("Summary: baseline benchmark")
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
            f"{name:<28} mean_cat={s['mean_cat']:.4f}  mean_dim={s['mean_dim']:.4f}  "
            f"cat/dim={s['cat_dim_ratio']:.3f}"
        )

    print(
        f"\nIncremental mean category R²: V-JEPA2={delta_vjepa[:34].mean():+.4f}  "
        f"CLIP={delta_clip[:34].mean():+.4f}"
    )
    print(
        f"Incremental mean A/V/D R²:   V-JEPA2={delta_vjepa[34:].mean():+.4f}  "
        f"CLIP={delta_clip[34:].mean():+.4f}"
    )

    top_v = np.argsort(delta_vjepa[:34])[-10:][::-1]
    top_c = np.argsort(delta_clip[:34])[-10:][::-1]
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

    # Save
    np.savez(
        OUTPUT_PATH,
        target_names=np.array(TARGET_NAMES),
        emotion_labels=np.array(EMOTION_LABELS),
        dim_labels=np.array(DIM_LABELS),
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

    # Figure 1: bar summary
    fig, axes = plt.subplots(2, 1, figsize=(18, 10))
    fig.patch.set_facecolor("white")

    for ax, delta, combined, label in [
        (axes[0], delta_vjepa, r2_combined_vjepa, "V-JEPA2"),
        (axes[1], delta_clip, r2_combined_clip, "CLIP"),
    ]:
        emo_pairs = sorted(
            [(TARGET_NAMES[i], r2_baseline[i], combined[i], delta[i]) for i in range(34)],
            key=lambda x: x[3],
            reverse=True,
        )
        dim_pairs = [(TARGET_NAMES[i], r2_baseline[i], combined[i], delta[i]) for i in range(34, 37)]

        names = [p[0] for p in emo_pairs] + [""] + [p[0] for p in dim_pairs]
        base_vals = [p[1] for p in emo_pairs] + [0.0] + [p[1] for p in dim_pairs]
        comb_vals = [p[2] for p in emo_pairs] + [0.0] + [p[2] for p in dim_pairs]
        colors = ["steelblue"] * 34 + ["white"] + ["tomato"] * 3
        x = np.arange(len(names))

        ax.bar(x, base_vals, color="lightgray", alpha=0.7, label="Baseline (vision+semantic)")
        ax.bar(x, comb_vals, color=colors, alpha=0.85, label=f"Baseline + {label} PCs")
        ax.axvline(33.5, color="black", linestyle=":", alpha=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=90, fontsize=7)
        ax.set_ylabel("R²")
        ax.set_title(
            f"Incremental benchmark: baseline vs baseline+{label} PCs",
            fontweight="bold",
        )
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(BAR_FIG_PATH, dpi=200, bbox_inches="tight")
    plt.close()

    # Figure 2: scatter
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("white")
    for ax, delta, combined, label in [
        (axes[0], delta_vjepa, r2_combined_vjepa, "V-JEPA2"),
        (axes[1], delta_clip, r2_combined_clip, "CLIP"),
    ]:
        x_cat = r2_baseline[:34]
        y_cat = combined[:34]
        x_dim = r2_baseline[34:]
        y_dim = combined[34:]
        ax.scatter(x_cat, y_cat, color="steelblue", alpha=0.75, label="34 emotions")
        ax.scatter(x_dim, y_dim, color="tomato", marker="D", s=80, alpha=0.9, label="A/V/D")
        lim = max(float(max(x_cat.max(), y_cat.max(), x_dim.max(), y_dim.max())), 1e-3)
        ax.plot([0, lim], [0, lim], "k--", alpha=0.5)
        ax.set_xlabel("Baseline R²")
        ax.set_ylabel(f"Baseline + {label} PCs R²")
        ax.set_title(f"{label}: incremental benchmark", fontweight="bold")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(SCATTER_FIG_PATH, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"\nSaved:")
    print(f"  {OUTPUT_PATH}")
    print(f"  {BAR_FIG_PATH}")
    print(f"  {SCATTER_FIG_PATH}")


if __name__ == "__main__":
    main()
