# -*- coding: utf-8 -*-
"""
CCN Analysis 17: Arousal-Valence 2D comparison

Purpose:
    Re-run the category-vs-dimension comparison using only two affective
    dimensions: Arousal and Valence.

This script combines three views in one place:
1. V-JEPA2 brain-predictable subspace vs all PCs
2. CLIP brain-predictable subspace vs all PCs
3. Raw fMRI PCA k-sweep + raw k=27/full comparison

Outputs:
    results/exp17_av2d_results.npz
    figures/exp17_av2d_model_targets.png
    figures/exp17_av2d_raw_k_sweep.png
    figures/exp17_av2d_summary.png
"""

import warnings
from pathlib import Path

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

# Paths
BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
CCN_DIR = BASE / "CCN"
RESULTS_DIR = CCN_DIR / "results"
FIG_DIR = CCN_DIR / "figures"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

META_PATH = Path(
    "/pscratch/sd/s/sjmoon/Horikawa_embedding/"
    "horikawa_filtered_MNI_to_TRs/metadata/"
    "horikawa_meta_data_with_14dims.csv"
)
VJEPA_PATH = BASE / "video_embeddings" / "vjepa2_embeddings.npy"
CLIP_PATH = BASE / "video_embeddings" / "clip_embeddings.npy"
FMRI_PATH = BASE / "raw_fmri_results" / "fmri_raw.npy"
PC_EMO_PATH = RESULTS_DIR / "pc_emotion_correlation.npz"

OUTPUT_PATH = RESULTS_DIR / "exp17_av2d_results.npz"
TARGET_FIG = FIG_DIR / "exp17_av2d_model_targets.png"
RAW_SWEEP_FIG = FIG_DIR / "exp17_av2d_raw_k_sweep.png"
SUMMARY_FIG = FIG_DIR / "exp17_av2d_summary.png"

# Constants
N_PC = 100
CV = 5
R2_THRESH = 0.01
ALPHA = 1.0
RAW_K_VALUES = [3, 5, 7, 10, 15, 20, 25, 27, 30, 34, 40, 50, 75, 100]
RAW_K_REFERENCE = 27

EMOTION_LABELS = [
    "Admiration", "Adoration", "Aesthetic appreciation", "Amusement", "Anger",
    "Anxiety", "Awe", "Awkwardness", "Boredom", "Calmness", "Confusion",
    "Contempt", "Craving", "Disgust", "Empathic pain", "Entrancement",
    "Excitement", "Fear", "Horror", "Interest", "Joy", "Nostalgia", "Relief",
    "Romance", "Sadness", "Satisfaction", "Sexual desire", "Surprise",
    "Sympathy", "Triumph", "Uncomfortable", "Annoyance", "Envy", "Guilt",
]
DIM2_LABELS = ["Arousal", "Valence"]
DIM2_COLS = ["arousal_score", "valence_score"]
TARGET_NAMES = EMOTION_LABELS + DIM2_LABELS


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


def load_metadata_av():
    meta = strip_bom_columns(pd.read_csv(META_PATH))
    stim_col = "stimulus_num" if "stimulus_num" in meta.columns else meta.columns[0]
    meta["stim_idx"] = extract_stimulus_idx(meta[stim_col])
    meta = meta.sort_values("stim_idx").reset_index(drop=True)
    emotion_scores = meta[[f"score_{i}" for i in range(34)]].to_numpy(dtype=np.float64)
    av_scores = meta[DIM2_COLS].to_numpy(dtype=np.float64)
    return meta, emotion_scores, av_scores


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


def plot_model_targets(ax, title, pred_values, all_values):
    emo_pairs = sorted(
        [(name, pred_values[i], all_values[i]) for i, name in enumerate(EMOTION_LABELS)],
        key=lambda x: x[1],
        reverse=True,
    )
    dim_pairs = [
        (name, pred_values[len(EMOTION_LABELS) + i], all_values[len(EMOTION_LABELS) + i])
        for i, name in enumerate(DIM2_LABELS)
    ]
    names = [p[0] for p in emo_pairs] + [""] + [p[0] for p in dim_pairs]
    pred_plot = [p[1] for p in emo_pairs] + [0.0] + [p[1] for p in dim_pairs]
    all_plot = [p[2] for p in emo_pairs] + [0.0] + [p[2] for p in dim_pairs]
    colors = ["steelblue"] * len(EMOTION_LABELS) + ["white"] + ["tomato"] * len(DIM2_LABELS)
    x = np.arange(len(names))

    ax.bar(x, all_plot, color="lightgray", alpha=0.65, label="Reference")
    ax.bar(x, pred_plot, color=colors, alpha=0.85, label="Focus")
    ax.axvline(len(EMOTION_LABELS) - 0.5, color="black", linestyle=":", alpha=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=90, fontsize=7)
    ax.set_ylabel("R²")
    ax.set_title(title, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=8)


def main():
    print("Loading metadata...")
    _, emotion_scores, av_scores = load_metadata_av()
    targets = np.hstack([emotion_scores, av_scores])

    print("Loading embeddings...")
    vjepa_emb = np.load(VJEPA_PATH).astype(np.float64)
    clip_emb = np.load(CLIP_PATH).astype(np.float64)
    raw_fmri = np.load(FMRI_PATH).astype(np.float64)
    raw_mean = raw_fmri.mean(axis=0)

    pc_data = np.load(PC_EMO_PATH, allow_pickle=True)
    pred_idx_v = np.where(pc_data["r2_vjepa"] > R2_THRESH)[0]
    pred_idx_c = np.where(pc_data["r2_clip"] > R2_THRESH)[0]
    unpred_idx_v = np.where(pc_data["r2_vjepa"] <= R2_THRESH)[0]
    unpred_idx_c = np.where(pc_data["r2_clip"] <= R2_THRESH)[0]

    print(f"  Metadata: {META_PATH}")
    print(f"  Targets: {targets.shape} -> 34 emotions + 2 dims")
    print(f"  V-JEPA2 pred PCs: {pred_idx_v + 1} (n={len(pred_idx_v)})")
    print(f"  CLIP pred PCs:    {pred_idx_c + 1} (n={len(pred_idx_c)})")

    print("\nFitting PCA for model embeddings...")
    vjepa_pcs = PCA(n_components=N_PC, random_state=42).fit_transform(vjepa_emb)
    clip_pcs = PCA(n_components=N_PC, random_state=42).fit_transform(clip_emb)

    # V-JEPA2 / CLIP Exp12-style analysis
    print("\nRunning model subspace comparisons...")
    model_results = {}
    for model_key, pcs, pred_idx, unpred_idx in [
        ("vjepa", vjepa_pcs, pred_idx_v, unpred_idx_v),
        ("clip", clip_pcs, pred_idx_c, unpred_idx_c),
    ]:
        model_results[model_key] = {}
        for subspace_name, feats in [
            ("pred", pcs[:, pred_idx]),
            ("unpred", pcs[:, unpred_idx]),
            ("all", pcs),
        ]:
            print(f"  {model_key} [{subspace_name}]")
            values = compute_targetwise_r2(feats, targets)
            model_results[model_key][subspace_name] = values
            s = summarize(values)
            print(
                f"    mean_cat={s['mean_cat']:.4f}  mean_av={s['mean_dim']:.4f}  "
                f"cat/av={s['cat_dim_ratio']:.3f}"
            )

    # Raw fMRI k sweep
    print("\nRunning raw fMRI A/V k-sweep...")
    raw_summary = {"k": [], "mean_cat": [], "mean_dim": [], "cat_dim_ratio": []}
    raw_targetwise = {}
    for k in RAW_K_VALUES:
        print(f"  raw k={k}")
        raw_k = PCA(n_components=k, random_state=42).fit_transform(raw_mean)
        values = compute_targetwise_r2(raw_k, targets)
        raw_targetwise[k] = values
        s = summarize(values)
        raw_summary["k"].append(k)
        raw_summary["mean_cat"].append(s["mean_cat"])
        raw_summary["mean_dim"].append(s["mean_dim"])
        raw_summary["cat_dim_ratio"].append(s["cat_dim_ratio"])
        print(
            f"    mean_cat={s['mean_cat']:.4f}  mean_av={s['mean_dim']:.4f}  "
            f"cat/av={s['cat_dim_ratio']:.3f}"
        )

    print("\nComputing raw full-450D results...")
    raw_full = compute_targetwise_r2(raw_mean, targets)
    raw_k27 = raw_targetwise[RAW_K_REFERENCE]

    # Save
    np.savez(
        OUTPUT_PATH,
        metadata_path=np.array([str(META_PATH)]),
        fmri_path=np.array([str(FMRI_PATH)]),
        target_names=np.array(TARGET_NAMES),
        emotion_labels=np.array(EMOTION_LABELS),
        dim_labels=np.array(DIM2_LABELS),
        dim_cols=np.array(DIM2_COLS),
        pred_idx_vjepa=pred_idx_v,
        pred_idx_clip=pred_idx_c,
        r2_pred_vjepa=model_results["vjepa"]["pred"],
        r2_unpred_vjepa=model_results["vjepa"]["unpred"],
        r2_all_vjepa=model_results["vjepa"]["all"],
        r2_pred_clip=model_results["clip"]["pred"],
        r2_unpred_clip=model_results["clip"]["unpred"],
        r2_all_clip=model_results["clip"]["all"],
        raw_k_values=np.array(raw_summary["k"], dtype=np.int64),
        raw_mean_cat=np.array(raw_summary["mean_cat"], dtype=np.float64),
        raw_mean_dim=np.array(raw_summary["mean_dim"], dtype=np.float64),
        raw_cat_dim_ratio=np.array(raw_summary["cat_dim_ratio"], dtype=np.float64),
        r2_raw_k27=raw_k27,
        r2_raw_full=raw_full,
    )

    # Figure 1: target-level comparison
    fig, axes = plt.subplots(3, 1, figsize=(18, 14))
    fig.patch.set_facecolor("white")
    plot_model_targets(
        axes[0],
        "V-JEPA2: brain-predictable subspace vs all PCs (34 emotions + A/V)",
        model_results["vjepa"]["pred"],
        model_results["vjepa"]["all"],
    )
    plot_model_targets(
        axes[1],
        "CLIP: brain-predictable subspace vs all PCs (34 emotions + A/V)",
        model_results["clip"]["pred"],
        model_results["clip"]["all"],
    )
    plot_model_targets(
        axes[2],
        "Raw fMRI: PCA k=27 vs full 450D (34 emotions + A/V)",
        raw_k27,
        raw_full,
    )
    plt.tight_layout()
    plt.savefig(TARGET_FIG, dpi=200, bbox_inches="tight")
    plt.close()

    # Figure 2: raw k-sweep
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor("white")
    axes[0].plot(raw_summary["k"], raw_summary["mean_cat"], "o-", color="steelblue", label="34 emotions")
    axes[0].plot(raw_summary["k"], raw_summary["mean_dim"], "o-", color="tomato", label="Arousal + Valence")
    axes[0].axvline(RAW_K_REFERENCE, color="gray", linestyle="--", alpha=0.7, label=f"k={RAW_K_REFERENCE}")
    axes[0].set_xlabel("Number of PCA dimensions (k)")
    axes[0].set_ylabel("Mean R²")
    axes[0].set_title("Raw fMRI: mean category vs A/V decoding", fontweight="bold")
    axes[0].grid(alpha=0.3)
    axes[0].legend(fontsize=8)

    axes[1].plot(raw_summary["k"], raw_summary["cat_dim_ratio"], "o-", color="black")
    axes[1].axhline(1.0, color="gray", linestyle="--", alpha=0.7)
    axes[1].axvline(RAW_K_REFERENCE, color="gray", linestyle="--", alpha=0.7)
    axes[1].set_xlabel("Number of PCA dimensions (k)")
    axes[1].set_ylabel("Category/A-V ratio")
    axes[1].set_title("Raw fMRI: category-vs-A/V balance", fontweight="bold")
    axes[1].grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(RAW_SWEEP_FIG, dpi=200, bbox_inches="tight")
    plt.close()

    # Figure 3: summary bars
    labels = [
        "VJ pred", "VJ all",
        "CLIP pred", "CLIP all",
        "Raw k27", "Raw full",
    ]
    cat_vals = [
        summarize(model_results["vjepa"]["pred"])["mean_cat"],
        summarize(model_results["vjepa"]["all"])["mean_cat"],
        summarize(model_results["clip"]["pred"])["mean_cat"],
        summarize(model_results["clip"]["all"])["mean_cat"],
        summarize(raw_k27)["mean_cat"],
        summarize(raw_full)["mean_cat"],
    ]
    dim_vals = [
        summarize(model_results["vjepa"]["pred"])["mean_dim"],
        summarize(model_results["vjepa"]["all"])["mean_dim"],
        summarize(model_results["clip"]["pred"])["mean_dim"],
        summarize(model_results["clip"]["all"])["mean_dim"],
        summarize(raw_k27)["mean_dim"],
        summarize(raw_full)["mean_dim"],
    ]
    x = np.arange(len(labels))
    width = 0.38
    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor("white")
    ax.bar(x - width / 2, cat_vals, width=width, color="steelblue", label="34 emotions")
    ax.bar(x + width / 2, dim_vals, width=width, color="tomato", label="Arousal + Valence")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Mean R²")
    ax.set_title("A/V 2D summary across representations", fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(SUMMARY_FIG, dpi=200, bbox_inches="tight")
    plt.close()

    print("\nSaved:")
    print(f"  {OUTPUT_PATH}")
    print(f"  {TARGET_FIG}")
    print(f"  {RAW_SWEEP_FIG}")
    print(f"  {SUMMARY_FIG}")


if __name__ == "__main__":
    main()
