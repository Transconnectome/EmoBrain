# -*- coding: utf-8 -*-
"""
CCN Analysis 13: Control low-level vision/semantic confounds

This script implements two linked analyses proposed in exp13_vision_semantic.md.

Experiment A: Partial RSA
    Regress out vision-feature RSM and semantic-feature RSM from each neural/model
    RSM, then compute Spearman RSA on the residual geometry.

Experiment B: Partial R^2 of brain-predictable subspace
    Regress out vision + semantic confounds from both the brain-predictable model
    PCs and the target emotion scores, then evaluate residual prediction with
    fold-wise Ridge CV to avoid confound leakage across train/test splits.

Inputs:
    /pscratch/sd/s/sjmoon/EmoFM/vision_features.csv
    /pscratch/sd/s/sjmoon/EmoFM/semantic_features.csv
    /pscratch/sd/s/sjmoon/EmoFM/video_embeddings/vjepa2_embeddings.npy
    /pscratch/sd/s/sjmoon/EmoFM/video_embeddings/clip_embeddings.npy
    /pscratch/sd/s/sjmoon/Horikawa_embedding/.../horikawa_meta_data_with_dimension_binary.csv
    /pscratch/sd/s/sjmoon/EmoFM/CCN/results/pc_emotion_correlation.npz
    /pscratch/sd/s/sjmoon/EmoFM/CCN/results/brain_jepa_rsm_mean.npy or cka_results/rsm_brain.npy
    /pscratch/sd/s/sjmoon/EmoFM/CCN/results/raw_rsm_mean.npy (optional)
    /pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_vjepa2.npy
    /pscratch/sd/s/sjmoon/EmoFM/cka_results/rsm_clip.npy

Outputs:
    /pscratch/sd/s/sjmoon/EmoFM/CCN/results/vision_semantic_partial_results.npz
    /pscratch/sd/s/sjmoon/EmoFM/CCN/figures/partial_rsa_vision_semantic.png
    /pscratch/sd/s/sjmoon/EmoFM/CCN/figures/partial_r2_vision_semantic.png
"""

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import r2_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path("/pscratch/sd/s/sjmoon/EmoFM")
CCN_DIR = BASE / "CCN"
RESULTS_DIR = CCN_DIR / "results"
FIG_DIR = CCN_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

VISION_PATH = BASE / "vision_features.csv"
SEMANTIC_PATH = BASE / "semantic_features.csv"
VJEPA_PATH = BASE / "video_embeddings" / "vjepa2_embeddings.npy"
CLIP_PATH = BASE / "video_embeddings" / "clip_embeddings.npy"
META_PATH = Path(
    "/pscratch/sd/s/sjmoon/Horikawa_embedding/"
    "horikawa_filtered_MNI_to_TRs/metadata/"
    "horikawa_meta_data_with_dimension_binary.csv"
)
PC_EMO_PATH = RESULTS_DIR / "pc_emotion_correlation.npz"
PRED_DIM_PATH = RESULTS_DIR / "brain_predictable_dims.npz"

BRAIN_RSM_CANDIDATES = [
    RESULTS_DIR / "brain_jepa_rsm_mean.npy",
    BASE / "cka_results" / "rsm_brain.npy",
]
RAW_RSM_PATH = RESULTS_DIR / "raw_rsm_mean.npy"
VJEPA_RSM_PATH = BASE / "cka_results" / "rsm_vjepa2.npy"
CLIP_RSM_PATH = BASE / "cka_results" / "rsm_clip.npy"

OUTPUT_PATH = RESULTS_DIR / "vision_semantic_partial_results.npz"
RSA_FIG_PATH = FIG_DIR / "partial_rsa_vision_semantic.png"
R2_FIG_PATH = FIG_DIR / "partial_r2_vision_semantic.png"

# ── Constants ─────────────────────────────────────────────────────────────────
N_PC = 100
R2_THRESH = 0.01
CV = 5
SEED = 42
DIM_LABELS = ["Arousal", "Valence", "Dominance"]
EMOTION_LABELS = [
    "Admiration", "Adoration", "Aesthetic appreciation", "Amusement", "Anger",
    "Anxiety", "Awe", "Awkwardness", "Boredom", "Calmness", "Confusion",
    "Contempt", "Craving", "Disgust", "Empathic pain", "Entrancement",
    "Excitement", "Fear", "Horror", "Interest", "Joy", "Nostalgia", "Relief",
    "Romance", "Sadness", "Satisfaction", "Sexual desire", "Surprise",
    "Sympathy", "Triumph", "Uncomfortable", "Annoyance", "Envy", "Guilt",
]


def strip_bom_columns(df):
    df.columns = [str(col).replace("\ufeff", "") for col in df.columns]
    return df


def extract_stimulus_idx(values):
    extracted = (
        pd.Series(values)
        .astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype(int)
        .to_numpy()
        - 1
    )
    return extracted


def load_feature_table(path):
    df = strip_bom_columns(pd.read_csv(path))
    stim_col = df.columns[0]
    df["stim_idx"] = extract_stimulus_idx(df[stim_col])
    df = df.sort_values("stim_idx").reset_index(drop=True)
    feature_cols = [col for col in df.columns if col not in {stim_col, "stim_idx"}]
    return df, feature_cols


def load_metadata():
    meta = strip_bom_columns(pd.read_csv(META_PATH))
    stim_col = "stimulus_num" if "stimulus_num" in meta.columns else meta.columns[0]
    meta["stim_idx"] = extract_stimulus_idx(meta[stim_col])
    meta = meta.sort_values("stim_idx").reset_index(drop=True)

    score_cols = sorted(
        [col for col in meta.columns if col.startswith("score_")],
        key=lambda x: int(x.split("_")[1]),
    )
    emotion_scores = meta[score_cols].to_numpy(dtype=np.float64)
    avd_scores = meta[
        ["arousal_score", "valence_score", "dominance_score"]
    ].to_numpy(dtype=np.float64)
    return meta, score_cols, emotion_scores, avd_scores


def validate_alignment(reference_idx, *other_idx):
    for idx in other_idx:
        if len(reference_idx) != len(idx) or not np.array_equal(reference_idx, idx):
            raise ValueError("Stimulus order mismatch across metadata/confound tables.")


def first_existing(paths):
    for path in paths:
        if path.exists():
            return path
    raise FileNotFoundError(f"None of the candidate paths exists: {paths}")


def load_brain_predictable_scores():
    if PC_EMO_PATH.exists():
        data = np.load(PC_EMO_PATH, allow_pickle=True)
        return data["r2_vjepa"], data["r2_clip"]
    if PRED_DIM_PATH.exists():
        data = np.load(PRED_DIM_PATH, allow_pickle=True)
        return data["r2_vjepa_per_dim"], data["r2_clip_per_dim"]
    raise FileNotFoundError("Could not find pc_emotion_correlation.npz or brain_predictable_dims.npz")


def residualize_with_train_fit(conf_train, conf_test, values_train, values_test):
    reg = LinearRegression()
    reg.fit(conf_train, values_train)
    train_resid = values_train - reg.predict(conf_train)
    test_resid = values_test - reg.predict(conf_test)
    return train_resid, test_resid


def partial_rsa(rsm_a, rsm_b, confound_rsms):
    n = rsm_a.shape[0]
    tri_idx = np.triu_indices(n, k=1)
    a_vec = rsm_a[tri_idx].astype(np.float64)
    b_vec = rsm_b[tri_idx].astype(np.float64)
    conf_vec = np.column_stack([rsm[tri_idx].astype(np.float64) for rsm in confound_rsms])

    reg_a = LinearRegression().fit(conf_vec, a_vec)
    reg_b = LinearRegression().fit(conf_vec, b_vec)
    a_resid = a_vec - reg_a.predict(conf_vec)
    b_resid = b_vec - reg_b.predict(conf_vec)

    original_r = spearmanr(a_vec, b_vec).statistic
    partial_res = spearmanr(a_resid, b_resid)
    return original_r, partial_res.statistic, partial_res.pvalue


def compute_original_r2(features, targets):
    pipe = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=1.0))])
    out = np.zeros(targets.shape[1], dtype=np.float64)
    for i in range(targets.shape[1]):
        score = cross_val_score(pipe, features, targets[:, i], cv=CV, scoring="r2").mean()
        out[i] = max(score, 0.0)
    return out


def compute_partial_r2(confounds, features, targets):
    splitter = KFold(n_splits=CV, shuffle=False)
    results = np.zeros(targets.shape[1], dtype=np.float64)

    for target_idx in range(targets.shape[1]):
        fold_scores = []
        y = targets[:, target_idx]

        for train_idx, test_idx in splitter.split(features):
            x_train = features[train_idx]
            x_test = features[test_idx]
            c_train = confounds[train_idx]
            c_test = confounds[test_idx]
            y_train = y[train_idx]
            y_test = y[test_idx]

            x_train_resid, x_test_resid = residualize_with_train_fit(
                c_train, c_test, x_train, x_test
            )
            y_train_resid, y_test_resid = residualize_with_train_fit(
                c_train, c_test, y_train.reshape(-1, 1), y_test.reshape(-1, 1)
            )

            pipe = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=1.0))])
            pipe.fit(x_train_resid, y_train_resid.ravel())
            pred = pipe.predict(x_test_resid)
            fold_scores.append(r2_score(y_test_resid.ravel(), pred))

        results[target_idx] = max(float(np.mean(fold_scores)), 0.0)

    return results


def summarize_model(model_name, target_names, emotion_names, dim_names, original_r2, partial_r2):
    print(f"\n{'=' * 72}")
    print(f"{model_name}: brain-predictable subspace after vision/semantic control")
    print(f"{'=' * 72}")

    emo_original = original_r2[: len(emotion_names)]
    emo_partial = partial_r2[: len(emotion_names)]
    dim_original = original_r2[len(emotion_names):]
    dim_partial = partial_r2[len(emotion_names):]

    print(
        f"Mean R² emotions: original={emo_original.mean():.4f}  partial={emo_partial.mean():.4f}  "
        f"retained={emo_partial.mean() / max(emo_original.mean(), 1e-10):.3f}"
    )
    print(
        f"Mean R² A/V/D:    original={dim_original.mean():.4f}  partial={dim_partial.mean():.4f}  "
        f"retained={dim_partial.mean() / max(dim_original.mean(), 1e-10):.3f}"
    )

    delta = partial_r2 - original_r2
    top_idx = np.argsort(original_r2[: len(emotion_names)])[-5:][::-1]
    print("\nTop 5 emotions by original R²:")
    for idx in top_idx:
        print(
            f"  {target_names[idx]:<24} "
            f"original={original_r2[idx]:.4f}  partial={partial_r2[idx]:.4f}  Δ={delta[idx]:+.4f}"
        )

    print("\nA/V/D:")
    for i, dim_name in enumerate(dim_names, start=len(emotion_names)):
        print(
            f"  {target_names[i]:<24} "
            f"original={original_r2[i]:.4f}  partial={partial_r2[i]:.4f}  Δ={delta[i]:+.4f}"
        )


def make_partial_rsa_figure(source_names, model_names, original_r, partial_r):
    labels = [f"{src}\nvs {mdl}" for src in source_names for mdl in model_names]
    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor("white")
    ax.bar(x - 0.18, original_r.reshape(-1), width=0.36, color="#9fb3c8", label="Original RSA")
    ax.bar(x + 0.18, partial_r.reshape(-1), width=0.36, color="#d97757", label="Partial RSA")
    ax.axhline(0, color="black", linewidth=1, alpha=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Spearman RSA")
    ax.set_title("Experiment 13A: Partial RSA after vision/semantic control", fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(RSA_FIG_PATH, dpi=200, bbox_inches="tight")
    plt.close()


def make_partial_r2_figure(target_names, emotion_names, dim_names, results):
    fig, axes = plt.subplots(2, 1, figsize=(18, 10))
    fig.patch.set_facecolor("white")

    for ax, model_key, label in [
        (axes[0], "vjepa", "V-JEPA2"),
        (axes[1], "clip", "CLIP"),
    ]:
        original = results[model_key]["original"]
        partial = results[model_key]["partial"]

        emo_pairs = sorted(
            zip(emotion_names, original[: len(emotion_names)], partial[: len(emotion_names)]),
            key=lambda x: x[1],
            reverse=True,
        )
        dim_pairs = list(
            zip(
                dim_names,
                original[len(emotion_names):],
                partial[len(emotion_names):],
            )
        )

        labels = [row[0] for row in emo_pairs] + [""] + [row[0] for row in dim_pairs]
        orig_vals = [row[1] for row in emo_pairs] + [0.0] + [row[1] for row in dim_pairs]
        part_vals = [row[2] for row in emo_pairs] + [0.0] + [row[2] for row in dim_pairs]
        colors = ["steelblue"] * len(emotion_names) + ["white"] + ["tomato"] * len(dim_names)
        x = np.arange(len(labels))

        ax.bar(x, orig_vals, color="lightgray", alpha=0.7, label="Original R²")
        ax.bar(x, part_vals, color=colors, alpha=0.85, label="Partial R²")
        ax.axvline(len(emotion_names) - 0.5, color="black", linestyle=":", alpha=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=90, fontsize=7)
        ax.set_ylabel("R² (5-fold CV Ridge)")
        ax.set_title(
            f"{label}: brain-predictable subspace before/after vision-semantic control",
            fontweight="bold",
        )
        ax.grid(axis="y", alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    plt.savefig(R2_FIG_PATH, dpi=200, bbox_inches="tight")
    plt.close()


def main():
    print("Loading confound features...")
    vision_df, vision_cols = load_feature_table(VISION_PATH)
    semantic_df, semantic_cols = load_feature_table(SEMANTIC_PATH)
    meta, score_cols, emotion_scores, avd_scores = load_metadata()

    validate_alignment(
        meta["stim_idx"].to_numpy(),
        vision_df["stim_idx"].to_numpy(),
        semantic_df["stim_idx"].to_numpy(),
    )

    vision_features = vision_df[vision_cols].to_numpy(dtype=np.float64)
    semantic_features = semantic_df[semantic_cols].to_numpy(dtype=np.float64)
    confounds = np.column_stack([vision_features, semantic_features])

    print(f"  vision features:   {vision_features.shape}")
    print(f"  semantic features: {semantic_features.shape}")
    print(f"  confounds total:   {confounds.shape}")
    print(f"  emotion scores:    {emotion_scores.shape}")
    print(f"  A/V/D scores:      {avd_scores.shape}")

    # ── Experiment A: Partial RSA ────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("Experiment A: Partial RSA")
    print(f"{'=' * 72}")

    rsm_vision = cosine_similarity(vision_features)
    rsm_semantic = cosine_similarity(semantic_features)

    source_paths = {
        "Brain-JEPA": first_existing(BRAIN_RSM_CANDIDATES),
    }
    if RAW_RSM_PATH.exists():
        source_paths["Raw fMRI"] = RAW_RSM_PATH

    model_paths = {
        "V-JEPA2": VJEPA_RSM_PATH,
        "CLIP": CLIP_RSM_PATH,
    }

    source_names = list(source_paths.keys())
    model_names = list(model_paths.keys())
    rsa_original = np.zeros((len(source_names), len(model_names)), dtype=np.float64)
    rsa_partial = np.zeros_like(rsa_original)
    rsa_pvalue = np.zeros_like(rsa_original)

    for i, source_name in enumerate(source_names):
        source_rsm = np.load(source_paths[source_name]).astype(np.float64)
        for j, model_name in enumerate(model_names):
            model_rsm = np.load(model_paths[model_name]).astype(np.float64)
            original_r, partial_r, pval = partial_rsa(
                source_rsm,
                model_rsm,
                [rsm_vision, rsm_semantic],
            )
            rsa_original[i, j] = original_r
            rsa_partial[i, j] = partial_r
            rsa_pvalue[i, j] = pval
            print(
                f"{source_name:<10} vs {model_name:<7}  "
                f"original={original_r:+.4f}  partial={partial_r:+.4f}  "
                f"Δ={partial_r - original_r:+.4f}  p={pval:.2e}"
            )

    # ── Experiment B: Partial R² ─────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("Experiment B: Partial R² of brain-predictable subspace")
    print(f"{'=' * 72}")

    r2_vjepa, r2_clip = load_brain_predictable_scores()
    pred_idx_v = np.where(r2_vjepa > R2_THRESH)[0]
    pred_idx_c = np.where(r2_clip > R2_THRESH)[0]

    print(f"Brain-predictable PCs:")
    print(f"  V-JEPA2: {pred_idx_v + 1} (n={len(pred_idx_v)})")
    print(f"  CLIP:    {pred_idx_c + 1} (n={len(pred_idx_c)})")

    if len(pred_idx_v) == 0 or len(pred_idx_c) == 0:
        raise ValueError("No brain-predictable PCs found. Check threshold or upstream results.")

    print("\nFitting PCA (100 components)...")
    vjepa_emb = np.load(VJEPA_PATH).astype(np.float64)
    clip_emb = np.load(CLIP_PATH).astype(np.float64)
    vjepa_pcs = PCA(n_components=N_PC, random_state=SEED).fit_transform(vjepa_emb)
    clip_pcs = PCA(n_components=N_PC, random_state=SEED).fit_transform(clip_emb)

    target_names = np.array(EMOTION_LABELS + DIM_LABELS)
    targets = np.hstack([emotion_scores, avd_scores])

    r2_results = {
        "vjepa": {
            "original": compute_original_r2(vjepa_pcs[:, pred_idx_v], targets),
            "partial": compute_partial_r2(confounds, vjepa_pcs[:, pred_idx_v], targets),
        },
        "clip": {
            "original": compute_original_r2(clip_pcs[:, pred_idx_c], targets),
            "partial": compute_partial_r2(confounds, clip_pcs[:, pred_idx_c], targets),
        },
    }

    summarize_model(
        "V-JEPA2",
        target_names,
        EMOTION_LABELS,
        DIM_LABELS,
        r2_results["vjepa"]["original"],
        r2_results["vjepa"]["partial"],
    )
    summarize_model(
        "CLIP",
        target_names,
        EMOTION_LABELS,
        DIM_LABELS,
        r2_results["clip"]["original"],
        r2_results["clip"]["partial"],
    )

    # ── Save + figures ────────────────────────────────────────────────────────
    make_partial_rsa_figure(source_names, model_names, rsa_original, rsa_partial)
    make_partial_r2_figure(target_names, EMOTION_LABELS, DIM_LABELS, r2_results)

    np.savez(
        OUTPUT_PATH,
        source_names=np.array(source_names),
        model_names=np.array(model_names),
        rsa_original=rsa_original,
        rsa_partial=rsa_partial,
        rsa_pvalue=rsa_pvalue,
        emotion_labels=np.array(EMOTION_LABELS),
        dim_labels=np.array(DIM_LABELS),
        target_names=target_names,
        pred_idx_vjepa=pred_idx_v,
        pred_idx_clip=pred_idx_c,
        r2_original_vjepa=r2_results["vjepa"]["original"],
        r2_partial_vjepa=r2_results["vjepa"]["partial"],
        r2_original_clip=r2_results["clip"]["original"],
        r2_partial_clip=r2_results["clip"]["partial"],
    )

    print(f"\nSaved:")
    print(f"  {OUTPUT_PATH}")
    print(f"  {RSA_FIG_PATH}")
    print(f"  {R2_FIG_PATH}")


if __name__ == "__main__":
    main()
