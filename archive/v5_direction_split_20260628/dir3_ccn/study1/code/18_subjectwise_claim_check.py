# -*- coding: utf-8 -*-
"""
CCN Analysis 18: Subject-wise claim check against the group-mean result

Purpose:
    Test whether the core group-level claim is preserved at the individual
    subject level.

Core question:
    If we define brain-predictable video-model PCs from each single subject
    brain representation, do we still see the same category-vs-dimension
    balance that we saw from the group-mean Brain-JEPA representation?

What this script does:
    1. Fit PCA(100) on V-JEPA2 and CLIP embeddings once.
    2. For each neural representation:
         - group mean Brain-JEPA
         - subject 1..5 Brain-JEPA
       predict each model PC from brain with Ridge CV.
    3. Define brain-predictable PCs by R² > 0.01.
    4. Re-run Exp12-style prediction on three target ontologies:
         - 3D: 34 emotions + A/V/D
         - 14D: 34 emotions + 14 dimensions
         - 2D: 34 emotions + A/V
    5. Compare each subject's category-vs-dimension balance against the
       group-mean result.

Outputs:
    results/exp18_subjectwise_claim_check.npz
    figures/exp18_subjectwise_ratios.png
    figures/exp18_subjectwise_pc_counts.png
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

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
CCN_DIR = BASE / "CCN"
RESULTS_DIR = CCN_DIR / "results"
FIG_DIR = CCN_DIR / "figures"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

BRAIN_PATH = BASE / "brain_embeddings" / "brain_jepa_embeddings.npy"
VJEPA_PATH = BASE / "video_embeddings" / "vjepa2_embeddings.npy"
CLIP_PATH = BASE / "video_embeddings" / "clip_embeddings.npy"
META_3D_PATH = Path(
    "/pscratch/sd/s/sjmoon/Horikawa_embedding/"
    "horikawa_filtered_MNI_to_TRs/metadata/"
    "horikawa_meta_data_with_dimension_binary.csv"
)
META_14D_PATH = HORIKAWA_META_14D_PATH

OUTPUT_PATH = RESULTS_DIR / "exp18_subjectwise_claim_check.npz"
RATIO_FIG_PATH = FIG_DIR / "exp18_subjectwise_ratios.png"
PC_COUNT_FIG_PATH = FIG_DIR / "exp18_subjectwise_pc_counts.png"

# ── Constants ─────────────────────────────────────────────────────────────────
SEED = 42
N_PC = 100
CV = 5
ALPHA = 1.0
R2_THRESH = 0.01
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
MODEL_ORDER = ["vjepa", "clip"]


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
    if features.shape[1] == 0:
        return 0.0
    pipe = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=ALPHA))])
    return max(float(cross_val_score(pipe, features, target, cv=CV, scoring="r2").mean()), 0.0)


def compute_pc_predictability(brain_repr, model_pcs):
    r2 = np.zeros(model_pcs.shape[1], dtype=np.float64)
    for i in range(model_pcs.shape[1]):
        r2[i] = ridge_r2(brain_repr, model_pcs[:, i])
    return r2


def compute_targetwise_r2(features, targets):
    out = np.zeros(targets.shape[1], dtype=np.float64)
    for i in range(targets.shape[1]):
        out[i] = ridge_r2(features, targets[:, i])
    return out


def summarize(values, n_emotions):
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


def ontology_spec():
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
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    fig.patch.set_facecolor("white")
    colors = {"vjepa": "#4c78a8", "clip": "#f58518"}

    for ax, ontology in zip(axes, ONTOLOGY_ORDER):
        x = np.arange(len(row_labels))
        for offset, model_key in [(-0.18, "vjepa"), (0.18, "clip")]:
            ratios = [summary[ontology][model_key][label]["cat_dim_ratio"] for label in row_labels]
            ax.bar(x + offset, ratios, width=0.36, color=colors[model_key], alpha=0.85,
                   label="V-JEPA2" if model_key == "vjepa" else "CLIP")
        ax.axhline(1.0, color="black", linestyle="--", alpha=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(row_labels, rotation=25, ha="right")
        ax.set_title(f"{ontology}: category/dimension ratio", fontweight="bold")
        ax.grid(axis="y", alpha=0.3)
        if ontology == "3D":
            ax.set_ylabel("Mean category R² / mean dimension R²")
            ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(RATIO_FIG_PATH, dpi=200, bbox_inches="tight")
    plt.close()


def make_pc_count_figure(pc_counts, row_labels):
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("white")
    x = np.arange(len(row_labels))
    ax.bar(x - 0.18, pc_counts["vjepa"], width=0.36, color="#4c78a8", alpha=0.85, label="V-JEPA2")
    ax.bar(x + 0.18, pc_counts["clip"], width=0.36, color="#f58518", alpha=0.85, label="CLIP")
    ax.set_xticks(x)
    ax.set_xticklabels(row_labels, rotation=25, ha="right")
    ax.set_ylabel("Number of brain-predictable PCs")
    ax.set_title("Group mean vs individual subjects: predictable PC count", fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(PC_COUNT_FIG_PATH, dpi=200, bbox_inches="tight")
    plt.close()


def main():
    print("Loading embeddings...")
    brain = np.load(BRAIN_PATH).astype(np.float64)            # (5, 2196, 768)
    brain_mean = brain.mean(axis=0)                           # (2196, 768)
    vjepa = np.load(VJEPA_PATH).astype(np.float64)            # (2196, 1408)
    clip = np.load(CLIP_PATH).astype(np.float64)              # (2196, 512)

    print("Loading target ontologies...")
    ontology_data = ontology_spec()

    print("Fitting PCA(100) on video-model embeddings...")
    vjepa_pcs = PCA(n_components=N_PC, random_state=SEED).fit_transform(vjepa)
    clip_pcs = PCA(n_components=N_PC, random_state=SEED).fit_transform(clip)

    neural_reprs = [("mean", brain_mean)] + [(f"subj{s+1}", brain[s]) for s in range(brain.shape[0])]
    row_labels = [name for name, _ in neural_reprs]

    pc_r2 = {model_key: np.zeros((len(neural_reprs), N_PC), dtype=np.float64) for model_key in MODEL_ORDER}
    pc_masks = {model_key: np.zeros((len(neural_reprs), N_PC), dtype=bool) for model_key in MODEL_ORDER}
    pc_counts = {model_key: np.zeros(len(neural_reprs), dtype=np.int64) for model_key in MODEL_ORDER}

    summary = {
        ontology: {
            model_key: {label: None for label in row_labels}
            for model_key in MODEL_ORDER
        }
        for ontology in ONTOLOGY_ORDER
    }
    targetwise = {
        ontology: {
            model_key: np.zeros((len(neural_reprs), ontology_data[ontology]["targets"].shape[1]), dtype=np.float64)
            for model_key in MODEL_ORDER
        }
        for ontology in ONTOLOGY_ORDER
    }

    print("\nStep 1: subject-wise brain-predictable PC discovery")
    for row_idx, (row_name, brain_repr) in enumerate(neural_reprs):
        print(f"  {row_name}: predicting V-JEPA2 PCs")
        r2_v = compute_pc_predictability(brain_repr, vjepa_pcs)
        mask_v = r2_v > R2_THRESH
        pc_r2["vjepa"][row_idx] = r2_v
        pc_masks["vjepa"][row_idx] = mask_v
        pc_counts["vjepa"][row_idx] = int(mask_v.sum())

        print(f"    predictable PCs: {np.where(mask_v)[0] + 1} (n={mask_v.sum()})")

        print(f"  {row_name}: predicting CLIP PCs")
        r2_c = compute_pc_predictability(brain_repr, clip_pcs)
        mask_c = r2_c > R2_THRESH
        pc_r2["clip"][row_idx] = r2_c
        pc_masks["clip"][row_idx] = mask_c
        pc_counts["clip"][row_idx] = int(mask_c.sum())
        print(f"    predictable PCs: {np.where(mask_c)[0] + 1} (n={mask_c.sum()})")

    print("\nStep 2: subject-wise Exp12-style category-vs-dimension checks")
    for ontology in ONTOLOGY_ORDER:
        targets = ontology_data[ontology]["targets"]
        n_emotions = len(EMOTION_LABELS)
        print(f"\n  Ontology: {ontology}")
        for model_key, pcs in [("vjepa", vjepa_pcs), ("clip", clip_pcs)]:
            print(f"    Model: {model_key}")
            for row_idx, row_name in enumerate(row_labels):
                mask = pc_masks[model_key][row_idx]
                feats = pcs[:, mask]
                r2 = compute_targetwise_r2(feats, targets)
                targetwise[ontology][model_key][row_idx] = r2
                stats = summarize(r2, n_emotions=n_emotions)
                summary[ontology][model_key][row_name] = stats
                print(
                    f"      {row_name:<5} n_pc={mask.sum():>2}  "
                    f"cat={stats['mean_cat']:.4f}  dim={stats['mean_dim']:.4f}  "
                    f"ratio={stats['cat_dim_ratio']:.3f}  -> {stats['orientation']}"
                )

    print("\nStep 3: agreement with the group-mean claim")
    agreement = {
        ontology: {model_key: np.zeros(brain.shape[0], dtype=np.int64) for model_key in MODEL_ORDER}
        for ontology in ONTOLOGY_ORDER
    }
    agreement_rate = {
        ontology: {model_key: 0.0 for model_key in MODEL_ORDER}
        for ontology in ONTOLOGY_ORDER
    }
    for ontology in ONTOLOGY_ORDER:
        for model_key in MODEL_ORDER:
            mean_orientation = summary[ontology][model_key]["mean"]["orientation"]
            subj_orientations = np.array(
                [summary[ontology][model_key][f"subj{s+1}"]["orientation"] for s in range(brain.shape[0])]
            )
            matches = (subj_orientations == mean_orientation).astype(np.int64)
            agreement[ontology][model_key] = matches
            agreement_rate[ontology][model_key] = float(matches.mean())
            print(
                f"  {ontology} | {model_key}: mean claim={mean_orientation} | "
                f"subject agreement={matches.sum()}/{len(matches)}"
            )

    make_ratio_figure(summary, row_labels)
    make_pc_count_figure(pc_counts, row_labels)

    np.savez(
        OUTPUT_PATH,
        row_labels=np.array(row_labels),
        ontology_order=np.array(ONTOLOGY_ORDER),
        model_order=np.array(MODEL_ORDER),
        emotion_labels=np.array(EMOTION_LABELS),
        dim3_labels=np.array(DIM3_LABELS),
        dim14_labels=np.array(DIM14_LABELS),
        dim2_labels=np.array(DIM2_LABELS),
        r2_pc_vjepa=pc_r2["vjepa"],
        r2_pc_clip=pc_r2["clip"],
        mask_vjepa=pc_masks["vjepa"],
        mask_clip=pc_masks["clip"],
        pc_count_vjepa=pc_counts["vjepa"],
        pc_count_clip=pc_counts["clip"],
        r2_3d_vjepa=targetwise["3D"]["vjepa"],
        r2_3d_clip=targetwise["3D"]["clip"],
        r2_14d_vjepa=targetwise["14D"]["vjepa"],
        r2_14d_clip=targetwise["14D"]["clip"],
        r2_2d_vjepa=targetwise["2D"]["vjepa"],
        r2_2d_clip=targetwise["2D"]["clip"],
        agreement_3d_vjepa=agreement["3D"]["vjepa"],
        agreement_3d_clip=agreement["3D"]["clip"],
        agreement_14d_vjepa=agreement["14D"]["vjepa"],
        agreement_14d_clip=agreement["14D"]["clip"],
        agreement_2d_vjepa=agreement["2D"]["vjepa"],
        agreement_2d_clip=agreement["2D"]["clip"],
        agreement_rate_3d_vjepa=np.array([agreement_rate["3D"]["vjepa"]]),
        agreement_rate_3d_clip=np.array([agreement_rate["3D"]["clip"]]),
        agreement_rate_14d_vjepa=np.array([agreement_rate["14D"]["vjepa"]]),
        agreement_rate_14d_clip=np.array([agreement_rate["14D"]["clip"]]),
        agreement_rate_2d_vjepa=np.array([agreement_rate["2D"]["vjepa"]]),
        agreement_rate_2d_clip=np.array([agreement_rate["2D"]["clip"]]),
    )

    print("\nSaved:")
    print(f"  {OUTPUT_PATH}")
    print(f"  {RATIO_FIG_PATH}")
    print(f"  {PC_COUNT_FIG_PATH}")


if __name__ == "__main__":
    main()
