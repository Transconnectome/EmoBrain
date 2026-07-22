# -*- coding: utf-8 -*-
"""
CCN Analysis 19: Subject-wise direct decoding from Brain-JEPA

Purpose:
    Directly test whether the category-vs-dimension pattern is preserved when
    each subject's Brain-JEPA embedding is used as the decoding feature space.

Key difference from Exp 18:
    Exp 18 re-estimated subject-specific brain-predictable model-PC masks and
    then decoded from the selected video-model subspace.
    This script skips model PCs entirely and decodes targets directly from the
    neural embedding itself.

Outputs:
    results/exp19_subjectwise_direct_decoding.npz
    figures/exp19_subjectwise_direct_decoding_ratios.png
    figures/exp19_subjectwise_direct_decoding_means.png
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

from ccn_dim14_metadata import DIM14_COLS, DIM14_LABELS, HORIKAWA_META_14D_PATH

warnings.filterwarnings("ignore")


# Paths
BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
CCN_DIR = BASE / "CCN"
RESULTS_DIR = CCN_DIR / "results"
FIG_DIR = CCN_DIR / "figures"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

BRAIN_PATH = BASE / "brain_embeddings" / "brain_jepa_embeddings.npy"
META_3D_PATH = Path(
    "/pscratch/sd/s/sjmoon/Horikawa_embedding/"
    "horikawa_filtered_MNI_to_TRs/metadata/"
    "horikawa_meta_data_with_dimension_binary.csv"
)
META_14D_PATH = HORIKAWA_META_14D_PATH

OUTPUT_PATH = RESULTS_DIR / "exp19_subjectwise_direct_decoding.npz"
RATIO_FIG_PATH = FIG_DIR / "exp19_subjectwise_direct_decoding_ratios.png"
MEAN_FIG_PATH = FIG_DIR / "exp19_subjectwise_direct_decoding_means.png"


# Constants
SEED = 42
CV = 5
ALPHA = 1.0
K_REFERENCE = 27
DIM3_COLS = ["arousal_score", "valence_score", "dominance_score"]
DIM3_LABELS = ["Arousal", "Valence", "Dominance"]
DIM2_COLS = ["arousal_score", "valence_score"]
DIM2_LABELS = ["Arousal", "Valence"]
EMOTION_LABELS = [
    "Admiration", "Adoration", "Aesthetic appreciation", "Amusement", "Anger",
    "Anxiety", "Awe", "Awkwardness", "Boredom", "Calmness", "Confusion",
    "Contempt", "Craving", "Disgust", "Empathic pain", "Entrancement",
    "Excitement", "Fear", "Horror", "Interest", "Joy", "Nostalgia", "Relief",
    "Romance", "Sadness", "Satisfaction", "Sexual desire", "Surprise",
    "Sympathy", "Triumph", "Uncomfortable", "Annoyance", "Envy", "Guilt",
]
ONTOLOGY_ORDER = ["3D", "14D", "2D"]
SETTING_ORDER = ["k27", "full"]


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


def load_metadata(path):
    meta = strip_bom_columns(pd.read_csv(path))
    stim_col = "stimulus_num" if "stimulus_num" in meta.columns else meta.columns[0]
    meta["stim_idx"] = extract_stimulus_idx(meta[stim_col])
    meta = meta.sort_values("stim_idx").reset_index(drop=True)
    return meta


def ridge_r2(features, target):
    pipe = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=ALPHA))])
    return max(float(cross_val_score(pipe, features, target, cv=CV, scoring="r2").mean()), 0.0)


def compute_targetwise_r2(features, targets):
    out = np.zeros(targets.shape[1], dtype=np.float64)
    for i in range(targets.shape[1]):
        out[i] = ridge_r2(features, targets[:, i])
    return out


def summarize(values, n_emotions=34):
    cat = values[:n_emotions]
    dim = values[n_emotions:]
    mean_cat = float(cat.mean())
    mean_dim = float(dim.mean())
    ratio = float(mean_cat / max(mean_dim, 1e-10))
    orientation = "category" if ratio > 1.0 else "dimension"
    return {
        "mean_cat": mean_cat,
        "mean_dim": mean_dim,
        "cat_dim_ratio": ratio,
        "orientation": orientation,
    }


def load_targets():
    meta3 = load_metadata(META_3D_PATH)
    meta14 = load_metadata(META_14D_PATH)
    ref_idx = meta3["stim_idx"].to_numpy()
    if not np.array_equal(ref_idx, meta14["stim_idx"].to_numpy()):
        raise ValueError("Stimulus order mismatch between 3D and 14D metadata.")

    emotions = meta3[[f"score_{i}" for i in range(34)]].to_numpy(dtype=np.float64)
    targets_3d = np.hstack([emotions, meta3[DIM3_COLS].to_numpy(dtype=np.float64)])
    targets_14d = np.hstack([emotions, meta14[DIM14_COLS].to_numpy(dtype=np.float64)])
    targets_2d = np.hstack([emotions, meta14[DIM2_COLS].to_numpy(dtype=np.float64)])

    return {
        "3D": {"targets": targets_3d, "dim_labels": DIM3_LABELS},
        "14D": {"targets": targets_14d, "dim_labels": DIM14_LABELS},
        "2D": {"targets": targets_2d, "dim_labels": DIM2_LABELS},
    }


def make_ratio_figure(summary, row_labels):
    fig, axes = plt.subplots(2, 3, figsize=(17, 8), sharey=True)
    fig.patch.set_facecolor("white")
    colors = ["#4c78a8", "#f58518", "#54a24b", "#e45756", "#72b7b2", "#b279a2"]
    x = np.arange(len(row_labels))

    for row_idx, setting in enumerate(SETTING_ORDER):
        for col_idx, ontology in enumerate(ONTOLOGY_ORDER):
            ax = axes[row_idx, col_idx]
            ratios = [summary[setting][ontology][label]["cat_dim_ratio"] for label in row_labels]
            ax.bar(x, ratios, color=colors, alpha=0.9)
            ax.axhline(1.0, color="black", linestyle="--", alpha=0.5)
            ax.set_xticks(x)
            ax.set_xticklabels(row_labels, rotation=25, ha="right")
            ax.set_title(f"{setting} | {ontology}", fontweight="bold")
            ax.grid(axis="y", alpha=0.3)
            if col_idx == 0:
                ax.set_ylabel("Mean category R² / mean dimension R²")

    plt.tight_layout()
    plt.savefig(RATIO_FIG_PATH, dpi=200, bbox_inches="tight")
    plt.close()


def make_mean_figure(summary, row_labels):
    fig, axes = plt.subplots(2, 3, figsize=(17, 8), sharey=True)
    fig.patch.set_facecolor("white")
    x = np.arange(len(row_labels))
    width = 0.38

    for row_idx, setting in enumerate(SETTING_ORDER):
        for col_idx, ontology in enumerate(ONTOLOGY_ORDER):
            ax = axes[row_idx, col_idx]
            cat_vals = [summary[setting][ontology][label]["mean_cat"] for label in row_labels]
            dim_vals = [summary[setting][ontology][label]["mean_dim"] for label in row_labels]
            ax.bar(x - width / 2, cat_vals, width=width, color="steelblue", alpha=0.9, label="Category")
            ax.bar(x + width / 2, dim_vals, width=width, color="tomato", alpha=0.9, label="Dimension")
            ax.set_xticks(x)
            ax.set_xticklabels(row_labels, rotation=25, ha="right")
            ax.set_title(f"{setting} | {ontology}", fontweight="bold")
            ax.grid(axis="y", alpha=0.3)
            if row_idx == 0 and col_idx == 0:
                ax.legend(fontsize=8)
            if col_idx == 0:
                ax.set_ylabel("Mean R²")

    plt.tight_layout()
    plt.savefig(MEAN_FIG_PATH, dpi=200, bbox_inches="tight")
    plt.close()


def main():
    print("Loading Brain-JEPA embeddings...")
    brain = np.load(BRAIN_PATH).astype(np.float64)  # (5, 2196, 768)
    brain_mean = brain.mean(axis=0)
    print(f"  Brain embeddings: {brain.shape}")

    print("Loading target ontologies...")
    ontology_data = load_targets()

    neural_reprs = [("mean", brain_mean)] + [(f"subj{s+1}", brain[s]) for s in range(brain.shape[0])]
    row_labels = [name for name, _ in neural_reprs]

    targetwise = {
        setting: {
            ontology: np.zeros((len(neural_reprs), ontology_data[ontology]["targets"].shape[1]), dtype=np.float64)
            for ontology in ONTOLOGY_ORDER
        }
        for setting in SETTING_ORDER
    }
    summary = {
        setting: {
            ontology: {label: None for label in row_labels}
            for ontology in ONTOLOGY_ORDER
        }
        for setting in SETTING_ORDER
    }
    agreement = {
        setting: {
            ontology: np.zeros(brain.shape[0], dtype=np.int64)
            for ontology in ONTOLOGY_ORDER
        }
        for setting in SETTING_ORDER
    }
    agreement_rate = {
        setting: {
            ontology: 0.0
            for ontology in ONTOLOGY_ORDER
        }
        for setting in SETTING_ORDER
    }

    for row_idx, (row_name, brain_repr) in enumerate(neural_reprs):
        print(f"\nPreparing features for {row_name}...")
        features = {
            "full": brain_repr,
            "k27": PCA(n_components=K_REFERENCE, random_state=SEED).fit_transform(brain_repr),
        }
        for setting in SETTING_ORDER:
            print(f"  Setting: {setting} -> {features[setting].shape}")
            feats = features[setting]
            for ontology in ONTOLOGY_ORDER:
                targets = ontology_data[ontology]["targets"]
                r2 = compute_targetwise_r2(feats, targets)
                targetwise[setting][ontology][row_idx] = r2
                stats = summarize(r2, n_emotions=len(EMOTION_LABELS))
                summary[setting][ontology][row_name] = stats
                print(
                    f"    {ontology:<3} cat={stats['mean_cat']:.4f}  "
                    f"dim={stats['mean_dim']:.4f}  ratio={stats['cat_dim_ratio']:.3f}  "
                    f"-> {stats['orientation']}"
                )

    print("\nAgreement with the group-mean orientation")
    for setting in SETTING_ORDER:
        for ontology in ONTOLOGY_ORDER:
            mean_orientation = summary[setting][ontology]["mean"]["orientation"]
            subj_orient = np.array(
                [summary[setting][ontology][f"subj{s+1}"]["orientation"] for s in range(brain.shape[0])]
            )
            matches = (subj_orient == mean_orientation).astype(np.int64)
            agreement[setting][ontology] = matches
            agreement_rate[setting][ontology] = float(matches.mean())
            print(
                f"  {setting} | {ontology}: mean={mean_orientation} | "
                f"subject agreement={matches.sum()}/{len(matches)}"
            )

    make_ratio_figure(summary, row_labels)
    make_mean_figure(summary, row_labels)

    np.savez(
        OUTPUT_PATH,
        row_labels=np.array(row_labels),
        setting_order=np.array(SETTING_ORDER),
        ontology_order=np.array(ONTOLOGY_ORDER),
        emotion_labels=np.array(EMOTION_LABELS),
        dim3_labels=np.array(DIM3_LABELS),
        dim14_labels=np.array(DIM14_LABELS),
        dim2_labels=np.array(DIM2_LABELS),
        r2_3d_k27=targetwise["k27"]["3D"],
        r2_14d_k27=targetwise["k27"]["14D"],
        r2_2d_k27=targetwise["k27"]["2D"],
        r2_3d_full=targetwise["full"]["3D"],
        r2_14d_full=targetwise["full"]["14D"],
        r2_2d_full=targetwise["full"]["2D"],
        agreement_k27_3d=agreement["k27"]["3D"],
        agreement_k27_14d=agreement["k27"]["14D"],
        agreement_k27_2d=agreement["k27"]["2D"],
        agreement_full_3d=agreement["full"]["3D"],
        agreement_full_14d=agreement["full"]["14D"],
        agreement_full_2d=agreement["full"]["2D"],
        agreement_rate_k27_3d=np.array([agreement_rate["k27"]["3D"]]),
        agreement_rate_k27_14d=np.array([agreement_rate["k27"]["14D"]]),
        agreement_rate_k27_2d=np.array([agreement_rate["k27"]["2D"]]),
        agreement_rate_full_3d=np.array([agreement_rate["full"]["3D"]]),
        agreement_rate_full_14d=np.array([agreement_rate["full"]["14D"]]),
        agreement_rate_full_2d=np.array([agreement_rate["full"]["2D"]]),
    )

    print("\nSaved:")
    print(f"  {OUTPUT_PATH}")
    print(f"  {RATIO_FIG_PATH}")
    print(f"  {MEAN_FIG_PATH}")


if __name__ == "__main__":
    main()
