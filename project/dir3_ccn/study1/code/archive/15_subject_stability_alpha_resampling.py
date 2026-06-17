# -*- coding: utf-8 -*-
"""
CCN Analysis 15: Subject stability, resampling stability, alpha sensitivity

Covers the "2번" follow-up analyses:
1. Subject-wise stability of brain-predictable PCs
2. Resampling stability of Exp 12 summaries and top emotions
3. Ridge alpha sensitivity for Exp 12 / Exp 13 summaries

Outputs:
  results/exp15_stability_results.npz
  figures/exp15_subject_stability.png
  figures/exp15_alpha_sensitivity.png
"""

from pathlib import Path
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold, cross_val_score
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

BRAIN_PATH = BASE / "brain_embeddings" / "brain_jepa_embeddings.npy"
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

OUTPUT_PATH = RESULTS_DIR / "exp15_stability_results.npz"
SUBJECT_FIG = FIG_DIR / "exp15_subject_stability.png"
ALPHA_FIG = FIG_DIR / "exp15_alpha_sensitivity.png"

# ── Constants ─────────────────────────────────────────────────────────────────
SEED = 42
N_PC = 100
CV = 5
R2_THRESH = 0.01
N_RESAMPLE = 100
ALPHAS = np.array([0.1, 1.0, 10.0, 100.0], dtype=np.float64)
EMOTION_LABELS = [
    "Admiration", "Adoration", "Aesthetic appreciation", "Amusement", "Anger",
    "Anxiety", "Awe", "Awkwardness", "Boredom", "Calmness", "Confusion",
    "Contempt", "Craving", "Disgust", "Empathic pain", "Entrancement",
    "Excitement", "Fear", "Horror", "Interest", "Joy", "Nostalgia", "Relief",
    "Romance", "Sadness", "Satisfaction", "Sexual desire", "Surprise",
    "Sympathy", "Triumph", "Uncomfortable", "Annoyance", "Envy", "Guilt",
]
DIM_LABELS = ["Arousal", "Valence", "Dominance"]


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


def load_metadata():
    meta = strip_bom_columns(pd.read_csv(META_PATH))
    stim_col = "stimulus_num" if "stimulus_num" in meta.columns else meta.columns[0]
    meta["stim_idx"] = extract_stimulus_idx(meta[stim_col])
    meta = meta.sort_values("stim_idx").reset_index(drop=True)
    emo = meta[[f"score_{i}" for i in range(34)]].to_numpy(dtype=np.float64)
    avd = meta[["arousal_score", "valence_score", "dominance_score"]].to_numpy(dtype=np.float64)
    return meta, emo, avd


def load_feature_table(path):
    df = strip_bom_columns(pd.read_csv(path))
    stim_col = df.columns[0]
    df["stim_idx"] = extract_stimulus_idx(df[stim_col])
    df = df.sort_values("stim_idx").reset_index(drop=True)
    feature_cols = [c for c in df.columns if c not in {stim_col, "stim_idx"}]
    return df, feature_cols


def validate_alignment(reference_idx, *other_idx):
    for idx in other_idx:
        if len(reference_idx) != len(idx) or not np.array_equal(reference_idx, idx):
            raise ValueError("Stimulus order mismatch.")


def ridge_r2(features, target, alpha=1.0):
    pipe = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=alpha))])
    return max(cross_val_score(pipe, features, target, cv=CV, scoring="r2").mean(), 0.0)


def compute_targetwise_r2(features, targets, alpha=1.0):
    out = np.zeros(targets.shape[1], dtype=np.float64)
    for i in range(targets.shape[1]):
        out[i] = ridge_r2(features, targets[:, i], alpha=alpha)
    return out


def residualize_with_train_fit(conf_train, conf_test, values_train, values_test):
    reg = LinearRegression()
    reg.fit(conf_train, values_train)
    return values_train - reg.predict(conf_train), values_test - reg.predict(conf_test)


def compute_partial_r2(confounds, features, targets, alpha=1.0):
    splitter = KFold(n_splits=CV, shuffle=False)
    out = np.zeros(targets.shape[1], dtype=np.float64)
    for target_idx in range(targets.shape[1]):
        y = targets[:, target_idx]
        fold_scores = []
        for train_idx, test_idx in splitter.split(features):
            x_train, x_test = features[train_idx], features[test_idx]
            c_train, c_test = confounds[train_idx], confounds[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            x_train_resid, x_test_resid = residualize_with_train_fit(c_train, c_test, x_train, x_test)
            y_train_resid, y_test_resid = residualize_with_train_fit(
                c_train, c_test, y_train.reshape(-1, 1), y_test.reshape(-1, 1)
            )

            pipe = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=alpha))])
            pipe.fit(x_train_resid, y_train_resid.ravel())
            pred = pipe.predict(x_test_resid)
            fold_scores.append(r2_score(y_test_resid.ravel(), pred))

        out[target_idx] = max(float(np.mean(fold_scores)), 0.0)
    return out


def jaccard(mask_a, mask_b):
    inter = np.logical_and(mask_a, mask_b).sum()
    union = np.logical_or(mask_a, mask_b).sum()
    return inter / max(union, 1)


def summarize(values):
    emo = values[: len(EMOTION_LABELS)]
    dim = values[len(EMOTION_LABELS):]
    return emo.mean(), dim.mean(), emo.mean() / max(dim.mean(), 1e-10)


def main():
    rng = np.random.default_rng(SEED)

    print("Loading data...")
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
    confounds = np.column_stack([vision, semantic])

    brain = np.load(BRAIN_PATH).astype(np.float64)
    brain_mean = brain.mean(axis=0)
    vjepa_emb = np.load(VJEPA_PATH).astype(np.float64)
    clip_emb = np.load(CLIP_PATH).astype(np.float64)
    pc_data = np.load(PC_EMO_PATH, allow_pickle=True)

    print("Fitting PCA (100 components)...")
    vjepa_pcs = PCA(n_components=N_PC, random_state=SEED).fit_transform(vjepa_emb)
    clip_pcs = PCA(n_components=N_PC, random_state=SEED).fit_transform(clip_emb)

    # ── 1) Subject-wise predictability stability ──────────────────────────────
    print("\n[1] Subject-wise brain-predictable PC stability...")
    subj_r2_v = np.zeros((brain.shape[0], N_PC), dtype=np.float64)
    subj_r2_c = np.zeros((brain.shape[0], N_PC), dtype=np.float64)

    for s in range(brain.shape[0]):
        print(f"  subject {s+1}/{brain.shape[0]}")
        for i in range(N_PC):
            subj_r2_v[s, i] = ridge_r2(brain[s], vjepa_pcs[:, i], alpha=1.0)
            subj_r2_c[s, i] = ridge_r2(brain[s], clip_pcs[:, i], alpha=1.0)

    subj_mask_v = subj_r2_v > R2_THRESH
    subj_mask_c = subj_r2_c > R2_THRESH
    mean_mask_v = pc_data["r2_vjepa"] > R2_THRESH
    mean_mask_c = pc_data["r2_clip"] > R2_THRESH

    jaccard_v = np.zeros((brain.shape[0], brain.shape[0]), dtype=np.float64)
    jaccard_c = np.zeros((brain.shape[0], brain.shape[0]), dtype=np.float64)
    for i in range(brain.shape[0]):
        for j in range(brain.shape[0]):
            jaccard_v[i, j] = jaccard(subj_mask_v[i], subj_mask_v[j])
            jaccard_c[i, j] = jaccard(subj_mask_c[i], subj_mask_c[j])

    freq_v = subj_mask_v.mean(axis=0)
    freq_c = subj_mask_c.mean(axis=0)

    # ── 2) Resampling stability of Exp12 summaries and top emotions ───────────
    print("\n[2] Resampling stability...")
    pred_idx_v = np.where(mean_mask_v)[0]
    pred_idx_c = np.where(mean_mask_c)[0]
    resample_summary_v = np.zeros((N_RESAMPLE, 3), dtype=np.float64)
    resample_summary_c = np.zeros((N_RESAMPLE, 3), dtype=np.float64)
    top5_freq_v = np.zeros(len(EMOTION_LABELS), dtype=np.int64)
    top5_freq_c = np.zeros(len(EMOTION_LABELS), dtype=np.int64)

    for r in range(N_RESAMPLE):
        idx = np.sort(rng.choice(targets.shape[0], size=targets.shape[0] // 2, replace=False))
        r2_v = compute_targetwise_r2(vjepa_pcs[idx][:, pred_idx_v], targets[idx], alpha=1.0)
        r2_c = compute_targetwise_r2(clip_pcs[idx][:, pred_idx_c], targets[idx], alpha=1.0)
        resample_summary_v[r] = summarize(r2_v)
        resample_summary_c[r] = summarize(r2_c)
        top5_v = np.argsort(r2_v[: len(EMOTION_LABELS)])[-5:]
        top5_c = np.argsort(r2_c[: len(EMOTION_LABELS)])[-5:]
        top5_freq_v[top5_v] += 1
        top5_freq_c[top5_c] += 1
        if (r + 1) % 10 == 0:
            print(f"  resample {r+1}/{N_RESAMPLE}")

    # ── 3) Ridge alpha sensitivity for Exp12 / Exp13 ──────────────────────────
    print("\n[3] Alpha sensitivity...")
    alpha_summary = {
        "alpha": [],
        "exp12_cat_vjepa": [], "exp12_dim_vjepa": [],
        "exp12_cat_clip": [], "exp12_dim_clip": [],
        "exp13_cat_vjepa": [], "exp13_dim_vjepa": [],
        "exp13_cat_clip": [], "exp13_dim_clip": [],
    }

    for alpha in ALPHAS:
        r2_exp12_v = compute_targetwise_r2(vjepa_pcs[:, pred_idx_v], targets, alpha=alpha)
        r2_exp12_c = compute_targetwise_r2(clip_pcs[:, pred_idx_c], targets, alpha=alpha)
        r2_exp13_v = compute_partial_r2(confounds, vjepa_pcs[:, pred_idx_v], targets, alpha=alpha)
        r2_exp13_c = compute_partial_r2(confounds, clip_pcs[:, pred_idx_c], targets, alpha=alpha)
        sv12 = summarize(r2_exp12_v)
        sc12 = summarize(r2_exp12_c)
        sv13 = summarize(r2_exp13_v)
        sc13 = summarize(r2_exp13_c)

        alpha_summary["alpha"].append(alpha)
        alpha_summary["exp12_cat_vjepa"].append(sv12[0])
        alpha_summary["exp12_dim_vjepa"].append(sv12[1])
        alpha_summary["exp12_cat_clip"].append(sc12[0])
        alpha_summary["exp12_dim_clip"].append(sc12[1])
        alpha_summary["exp13_cat_vjepa"].append(sv13[0])
        alpha_summary["exp13_dim_vjepa"].append(sv13[1])
        alpha_summary["exp13_cat_clip"].append(sc13[0])
        alpha_summary["exp13_dim_clip"].append(sc13[1])

        print(
            f"  alpha={alpha:.1f} | Exp12 cat V={sv12[0]:.4f}, C={sc12[0]:.4f} | "
            f"Exp13 cat V={sv13[0]:.4f}, C={sc13[0]:.4f}"
        )

    for key in list(alpha_summary.keys()):
        alpha_summary[key] = np.array(alpha_summary[key], dtype=np.float64)

    # ── Save ──────────────────────────────────────────────────────────────────
    np.savez(
        OUTPUT_PATH,
        subj_r2_vjepa=subj_r2_v,
        subj_r2_clip=subj_r2_c,
        subj_mask_vjepa=subj_mask_v,
        subj_mask_clip=subj_mask_c,
        mean_mask_vjepa=mean_mask_v,
        mean_mask_clip=mean_mask_c,
        jaccard_vjepa=jaccard_v,
        jaccard_clip=jaccard_c,
        selection_freq_vjepa=freq_v,
        selection_freq_clip=freq_c,
        resample_summary_vjepa=resample_summary_v,
        resample_summary_clip=resample_summary_c,
        top5_freq_vjepa=top5_freq_v,
        top5_freq_clip=top5_freq_c,
        alpha=alpha_summary["alpha"],
        exp12_cat_vjepa=alpha_summary["exp12_cat_vjepa"],
        exp12_dim_vjepa=alpha_summary["exp12_dim_vjepa"],
        exp12_cat_clip=alpha_summary["exp12_cat_clip"],
        exp12_dim_clip=alpha_summary["exp12_dim_clip"],
        exp13_cat_vjepa=alpha_summary["exp13_cat_vjepa"],
        exp13_dim_vjepa=alpha_summary["exp13_dim_vjepa"],
        exp13_cat_clip=alpha_summary["exp13_cat_clip"],
        exp13_dim_clip=alpha_summary["exp13_dim_clip"],
        emotion_labels=np.array(EMOTION_LABELS),
        dim_labels=np.array(DIM_LABELS),
    )

    # Subject stability figure
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor("white")

    im = axes[0].imshow(jaccard_v, vmin=0, vmax=1, cmap="Blues")
    axes[0].set_title("Subject Jaccard: V-JEPA2 PCs", fontweight="bold")
    axes[0].set_xlabel("Subject")
    axes[0].set_ylabel("Subject")
    plt.colorbar(im, ax=axes[0], fraction=0.046)

    im = axes[1].imshow(jaccard_c, vmin=0, vmax=1, cmap="Reds")
    axes[1].set_title("Subject Jaccard: CLIP PCs", fontweight="bold")
    axes[1].set_xlabel("Subject")
    axes[1].set_ylabel("Subject")
    plt.colorbar(im, ax=axes[1], fraction=0.046)

    plt.tight_layout()
    plt.savefig(SUBJECT_FIG, dpi=200, bbox_inches="tight")
    plt.close()

    # Alpha figure
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor("white")

    axes[0].plot(alpha_summary["alpha"], alpha_summary["exp12_cat_vjepa"], "o-", label="Exp12 V-JEPA2 cat")
    axes[0].plot(alpha_summary["alpha"], alpha_summary["exp12_cat_clip"], "o-", label="Exp12 CLIP cat")
    axes[0].plot(alpha_summary["alpha"], alpha_summary["exp13_cat_vjepa"], "o--", label="Exp13 V-JEPA2 partial cat")
    axes[0].plot(alpha_summary["alpha"], alpha_summary["exp13_cat_clip"], "o--", label="Exp13 CLIP partial cat")
    axes[0].set_xscale("log")
    axes[0].set_xlabel("Ridge alpha")
    axes[0].set_ylabel("Mean category R²")
    axes[0].set_title("Category summary vs alpha", fontweight="bold")
    axes[0].grid(alpha=0.3)
    axes[0].legend(fontsize=8)

    axes[1].plot(alpha_summary["alpha"], alpha_summary["exp12_dim_vjepa"], "o-", label="Exp12 V-JEPA2 dim")
    axes[1].plot(alpha_summary["alpha"], alpha_summary["exp12_dim_clip"], "o-", label="Exp12 CLIP dim")
    axes[1].plot(alpha_summary["alpha"], alpha_summary["exp13_dim_vjepa"], "o--", label="Exp13 V-JEPA2 partial dim")
    axes[1].plot(alpha_summary["alpha"], alpha_summary["exp13_dim_clip"], "o--", label="Exp13 CLIP partial dim")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("Ridge alpha")
    axes[1].set_ylabel("Mean A/V/D R²")
    axes[1].set_title("A/V/D summary vs alpha", fontweight="bold")
    axes[1].grid(alpha=0.3)
    axes[1].legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(ALPHA_FIG, dpi=200, bbox_inches="tight")
    plt.close()

    print("\nSaved:")
    print(f"  {OUTPUT_PATH}")
    print(f"  {SUBJECT_FIG}")
    print(f"  {ALPHA_FIG}")


if __name__ == "__main__":
    main()
