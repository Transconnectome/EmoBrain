# -*- coding: utf-8 -*-
"""
CCN Analysis 14: Robustness, bootstrap CI, threshold sensitivity, confound ablation

Covers the "1번" follow-up analyses:
1. Bootstrap confidence intervals for Exp 12 / Exp 13 headline metrics
2. Brain-predictable threshold sensitivity
3. Exp 13 confound ablation: vision-only, semantic-only, vision+semantic

Outputs:
  results/exp14_robustness_results.npz
  figures/exp14_threshold_sensitivity.png
  figures/exp14_confound_ablation.png
"""

from pathlib import Path
import warnings

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
BRAIN_JEPA_RSM_PATH = RESULTS_DIR / "brain_jepa_rsm_mean.npy"
RAW_RSM_PATH = RESULTS_DIR / "raw_rsm_mean.npy"
VJEPA_RSM_PATH = BASE / "cka_results" / "rsm_vjepa2.npy"
CLIP_RSM_PATH = BASE / "cka_results" / "rsm_clip.npy"

OUTPUT_PATH = RESULTS_DIR / "exp14_robustness_results.npz"
THRESH_FIG = FIG_DIR / "exp14_threshold_sensitivity.png"
CONFOUND_FIG = FIG_DIR / "exp14_confound_ablation.png"

# ── Constants ─────────────────────────────────────────────────────────────────
N_PC = 100
CV = 5
SEED = 42
BOOTSTRAPS = 100
THRESHOLDS = np.array([0.005, 0.01, 0.02, 0.03, 0.05], dtype=np.float64)
RIDGE_ALPHA = 1.0
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
CONFOUND_SETS = {
    "vision_only": ["vision"],
    "semantic_only": ["semantic"],
    "vision_semantic": ["vision", "semantic"],
}


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
    scores = meta[[f"score_{i}" for i in range(34)]].to_numpy(dtype=np.float64)
    avd = meta[["arousal_score", "valence_score", "dominance_score"]].to_numpy(dtype=np.float64)
    return meta, scores, avd


def validate_alignment(reference_idx, *other_idx):
    for idx in other_idx:
        if len(reference_idx) != len(idx) or not np.array_equal(reference_idx, idx):
            raise ValueError("Stimulus order mismatch across input tables.")


def residualize_with_train_fit(conf_train, conf_test, values_train, values_test):
    reg = LinearRegression()
    reg.fit(conf_train, values_train)
    return values_train - reg.predict(conf_train), values_test - reg.predict(conf_test)


def ridge_r2(features, target, alpha=RIDGE_ALPHA):
    pipe = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=alpha))])
    return max(cross_val_score(pipe, features, target, cv=CV, scoring="r2").mean(), 0.0)


def compute_targetwise_r2(features, targets, alpha=RIDGE_ALPHA):
    out = np.zeros(targets.shape[1], dtype=np.float64)
    for i in range(targets.shape[1]):
        out[i] = ridge_r2(features, targets[:, i], alpha=alpha)
    return out


def compute_partial_r2(confounds, features, targets, alpha=RIDGE_ALPHA):
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


def partial_rsa(rsm_a, rsm_b, confound_rsms):
    n = rsm_a.shape[0]
    tri_idx = np.triu_indices(n, k=1)
    a_vec = rsm_a[tri_idx].astype(np.float64)
    b_vec = rsm_b[tri_idx].astype(np.float64)
    x_conf = np.column_stack([rsm[tri_idx].astype(np.float64) for rsm in confound_rsms])

    reg_a = LinearRegression().fit(x_conf, a_vec)
    reg_b = LinearRegression().fit(x_conf, b_vec)
    a_resid = a_vec - reg_a.predict(x_conf)
    b_resid = b_vec - reg_b.predict(x_conf)
    return (
        spearmanr(a_vec, b_vec).statistic,
        spearmanr(a_resid, b_resid).statistic,
    )


def summarize_r2_table(values):
    emo = values[: len(EMOTION_LABELS)]
    dim = values[len(EMOTION_LABELS):]
    return {
        "mean_cat": float(emo.mean()),
        "mean_dim": float(dim.mean()),
        "cat_dim_ratio": float(emo.mean() / max(dim.mean(), 1e-10)),
    }


def bootstrap_metric(rng, features, targets, confounds=None, partial=False, n_boot=BOOTSTRAPS):
    n = features.shape[0]
    rows = np.zeros((n_boot, 3), dtype=np.float64)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        x_b = features[idx]
        y_b = targets[idx]
        if partial:
            c_b = confounds[idx]
            r2 = compute_partial_r2(c_b, x_b, y_b)
        else:
            r2 = compute_targetwise_r2(x_b, y_b)
        s = summarize_r2_table(r2)
        rows[b] = [s["mean_cat"], s["mean_dim"], s["cat_dim_ratio"]]
        if (b + 1) % 10 == 0:
            print(f"    bootstrap {b+1}/{n_boot}")
    return rows


def bootstrap_ci(samples):
    return np.percentile(samples, [2.5, 50.0, 97.5], axis=0)


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
    confound_mats = {
        "vision": vision,
        "semantic": semantic,
        "vision_semantic": np.column_stack([vision, semantic]),
    }

    print("Loading embeddings and precomputed predictability...")
    vjepa_emb = np.load(VJEPA_PATH).astype(np.float64)
    clip_emb = np.load(CLIP_PATH).astype(np.float64)
    pc_data = np.load(PC_EMO_PATH, allow_pickle=True)
    r2_vjepa = pc_data["r2_vjepa"]
    r2_clip = pc_data["r2_clip"]

    print("Fitting PCA (100 components)...")
    vjepa_pcs = PCA(n_components=N_PC, random_state=SEED).fit_transform(vjepa_emb)
    clip_pcs = PCA(n_components=N_PC, random_state=SEED).fit_transform(clip_emb)

    # ── 1) Threshold sensitivity ──────────────────────────────────────────────
    print("\n[1] Threshold sensitivity...")
    threshold_summary = {k: [] for k in ["threshold", "n_pred_vjepa", "n_pred_clip",
                                         "exp12_mean_cat_vjepa", "exp12_mean_dim_vjepa",
                                         "exp12_mean_cat_clip", "exp12_mean_dim_clip",
                                         "exp13_partial_cat_vjepa", "exp13_partial_dim_vjepa",
                                         "exp13_partial_cat_clip", "exp13_partial_dim_clip"]}

    for threshold in THRESHOLDS:
        pred_idx_v = np.where(r2_vjepa > threshold)[0]
        pred_idx_c = np.where(r2_clip > threshold)[0]
        if len(pred_idx_v) == 0 or len(pred_idx_c) == 0:
            print(f"  threshold={threshold:.3f}: skipped (empty pred set)")
            continue

        r2_orig_v = compute_targetwise_r2(vjepa_pcs[:, pred_idx_v], targets)
        r2_orig_c = compute_targetwise_r2(clip_pcs[:, pred_idx_c], targets)
        r2_part_v = compute_partial_r2(confound_mats["vision_semantic"], vjepa_pcs[:, pred_idx_v], targets)
        r2_part_c = compute_partial_r2(confound_mats["vision_semantic"], clip_pcs[:, pred_idx_c], targets)
        s_ov = summarize_r2_table(r2_orig_v)
        s_oc = summarize_r2_table(r2_orig_c)
        s_pv = summarize_r2_table(r2_part_v)
        s_pc = summarize_r2_table(r2_part_c)

        print(
            f"  thr={threshold:.3f} | V-JEPA2 n={len(pred_idx_v)} cat={s_ov['mean_cat']:.4f}->{s_pv['mean_cat']:.4f} "
            f"| CLIP n={len(pred_idx_c)} cat={s_oc['mean_cat']:.4f}->{s_pc['mean_cat']:.4f}"
        )

        threshold_summary["threshold"].append(threshold)
        threshold_summary["n_pred_vjepa"].append(len(pred_idx_v))
        threshold_summary["n_pred_clip"].append(len(pred_idx_c))
        threshold_summary["exp12_mean_cat_vjepa"].append(s_ov["mean_cat"])
        threshold_summary["exp12_mean_dim_vjepa"].append(s_ov["mean_dim"])
        threshold_summary["exp12_mean_cat_clip"].append(s_oc["mean_cat"])
        threshold_summary["exp12_mean_dim_clip"].append(s_oc["mean_dim"])
        threshold_summary["exp13_partial_cat_vjepa"].append(s_pv["mean_cat"])
        threshold_summary["exp13_partial_dim_vjepa"].append(s_pv["mean_dim"])
        threshold_summary["exp13_partial_cat_clip"].append(s_pc["mean_cat"])
        threshold_summary["exp13_partial_dim_clip"].append(s_pc["mean_dim"])

    for key in list(threshold_summary.keys()):
        threshold_summary[key] = np.array(threshold_summary[key])

    # ── 2) Bootstrap CI for Exp 12 / Exp 13 headline summaries ───────────────
    print("\n[2] Bootstrap confidence intervals...")
    pred_idx_v = np.where(r2_vjepa > 0.01)[0]
    pred_idx_c = np.where(r2_clip > 0.01)[0]

    exp12_boot_v = bootstrap_metric(rng, vjepa_pcs[:, pred_idx_v], targets, partial=False)
    exp12_boot_c = bootstrap_metric(rng, clip_pcs[:, pred_idx_c], targets, partial=False)
    exp13_boot_v = bootstrap_metric(
        rng, vjepa_pcs[:, pred_idx_v], targets, confounds=confound_mats["vision_semantic"], partial=True
    )
    exp13_boot_c = bootstrap_metric(
        rng, clip_pcs[:, pred_idx_c], targets, confounds=confound_mats["vision_semantic"], partial=True
    )

    ci_exp12_v = bootstrap_ci(exp12_boot_v)
    ci_exp12_c = bootstrap_ci(exp12_boot_c)
    ci_exp13_v = bootstrap_ci(exp13_boot_v)
    ci_exp13_c = bootstrap_ci(exp13_boot_c)

    print("  Exp12 V-JEPA2 CI [cat, dim, ratio]:")
    print(ci_exp12_v)
    print("  Exp12 CLIP CI [cat, dim, ratio]:")
    print(ci_exp12_c)
    print("  Exp13 V-JEPA2 CI [cat, dim, ratio]:")
    print(ci_exp13_v)
    print("  Exp13 CLIP CI [cat, dim, ratio]:")
    print(ci_exp13_c)

    # ── 3) Exp 13 confound ablation ───────────────────────────────────────────
    print("\n[3] Exp 13 confound ablation...")
    rsa_sources = {
        "Brain-JEPA": np.load(BRAIN_JEPA_RSM_PATH).astype(np.float64),
        "Raw fMRI": np.load(RAW_RSM_PATH).astype(np.float64),
    }
    rsa_models = {
        "V-JEPA2": np.load(VJEPA_RSM_PATH).astype(np.float64),
        "CLIP": np.load(CLIP_RSM_PATH).astype(np.float64),
    }
    rsm_confounds = {
        "vision": cosine_similarity(vision),
        "semantic": cosine_similarity(semantic),
        "vision_semantic": None,
    }
    rsm_confounds["vision_semantic"] = [rsm_confounds["vision"], rsm_confounds["semantic"]]

    confound_ablation_r2 = {}
    confound_ablation_rsa = {}

    for conf_name, members in CONFOUND_SETS.items():
        conf_mat = np.column_stack([confound_mats[m] for m in members])
        confound_ablation_r2[conf_name] = {}
        confound_ablation_rsa[conf_name] = {}

        r2_v = compute_partial_r2(conf_mat, vjepa_pcs[:, pred_idx_v], targets)
        r2_c = compute_partial_r2(conf_mat, clip_pcs[:, pred_idx_c], targets)
        confound_ablation_r2[conf_name]["vjepa"] = r2_v
        confound_ablation_r2[conf_name]["clip"] = r2_c

        print(
            f"  {conf_name}: V-JEPA2 mean cat={r2_v[:34].mean():.4f}, CLIP mean cat={r2_c[:34].mean():.4f}"
        )

        for src_name, src_rsm in rsa_sources.items():
            confound_ablation_rsa[conf_name][src_name] = {}
            chosen_rsms = [rsm_confounds[m] for m in members]
            for mdl_name, mdl_rsm in rsa_models.items():
                original_r, partial_r = partial_rsa(src_rsm, mdl_rsm, chosen_rsms)
                confound_ablation_rsa[conf_name][src_name][mdl_name] = (original_r, partial_r)

    # ── Save ──────────────────────────────────────────────────────────────────
    np.savez(
        OUTPUT_PATH,
        thresholds=threshold_summary["threshold"],
        n_pred_vjepa=threshold_summary["n_pred_vjepa"],
        n_pred_clip=threshold_summary["n_pred_clip"],
        exp12_mean_cat_vjepa=threshold_summary["exp12_mean_cat_vjepa"],
        exp12_mean_dim_vjepa=threshold_summary["exp12_mean_dim_vjepa"],
        exp12_mean_cat_clip=threshold_summary["exp12_mean_cat_clip"],
        exp12_mean_dim_clip=threshold_summary["exp12_mean_dim_clip"],
        exp13_partial_cat_vjepa=threshold_summary["exp13_partial_cat_vjepa"],
        exp13_partial_dim_vjepa=threshold_summary["exp13_partial_dim_vjepa"],
        exp13_partial_cat_clip=threshold_summary["exp13_partial_cat_clip"],
        exp13_partial_dim_clip=threshold_summary["exp13_partial_dim_clip"],
        exp12_boot_vjepa=exp12_boot_v,
        exp12_boot_clip=exp12_boot_c,
        exp13_boot_vjepa=exp13_boot_v,
        exp13_boot_clip=exp13_boot_c,
        ci_exp12_vjepa=ci_exp12_v,
        ci_exp12_clip=ci_exp12_c,
        ci_exp13_vjepa=ci_exp13_v,
        ci_exp13_clip=ci_exp13_c,
        confound_sets=np.array(list(CONFOUND_SETS.keys())),
        emotion_labels=np.array(EMOTION_LABELS),
        dim_labels=np.array(DIM_LABELS),
        target_names=np.array(TARGET_NAMES),
        confound_ablation_r2_vjepa=np.stack([confound_ablation_r2[k]["vjepa"] for k in CONFOUND_SETS]),
        confound_ablation_r2_clip=np.stack([confound_ablation_r2[k]["clip"] for k in CONFOUND_SETS]),
        confound_ablation_rsa=np.array([str(confound_ablation_rsa)], dtype=object),
    )

    # Threshold figure
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor("white")

    axes[0].plot(threshold_summary["threshold"], threshold_summary["n_pred_vjepa"], "o-", label="V-JEPA2")
    axes[0].plot(threshold_summary["threshold"], threshold_summary["n_pred_clip"], "o-", label="CLIP")
    axes[0].set_title("Brain-predictable PC count vs threshold", fontweight="bold")
    axes[0].set_xlabel("R² threshold")
    axes[0].set_ylabel("n predicted PCs")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].plot(threshold_summary["threshold"], threshold_summary["exp12_mean_cat_vjepa"], "o-", label="V-JEPA2 Exp12 cat")
    axes[1].plot(threshold_summary["threshold"], threshold_summary["exp12_mean_cat_clip"], "o-", label="CLIP Exp12 cat")
    axes[1].plot(threshold_summary["threshold"], threshold_summary["exp13_partial_cat_vjepa"], "o--", label="V-JEPA2 Exp13 partial cat")
    axes[1].plot(threshold_summary["threshold"], threshold_summary["exp13_partial_cat_clip"], "o--", label="CLIP Exp13 partial cat")
    axes[1].set_title("Summary R² vs threshold", fontweight="bold")
    axes[1].set_xlabel("R² threshold")
    axes[1].set_ylabel("Mean category R²")
    axes[1].grid(alpha=0.3)
    axes[1].legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(THRESH_FIG, dpi=200, bbox_inches="tight")
    plt.close()

    # Confound ablation figure
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor("white")
    x = np.arange(len(CONFOUND_SETS))
    conf_labels = list(CONFOUND_SETS.keys())

    v_cat = [confound_ablation_r2[k]["vjepa"][:34].mean() for k in conf_labels]
    c_cat = [confound_ablation_r2[k]["clip"][:34].mean() for k in conf_labels]
    v_dim = [confound_ablation_r2[k]["vjepa"][34:].mean() for k in conf_labels]
    c_dim = [confound_ablation_r2[k]["clip"][34:].mean() for k in conf_labels]

    axes[0].bar(x - 0.18, v_cat, width=0.36, label="V-JEPA2")
    axes[0].bar(x + 0.18, c_cat, width=0.36, label="CLIP")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(conf_labels, rotation=15)
    axes[0].set_ylabel("Mean category partial R²")
    axes[0].set_title("Exp13 confound ablation: category", fontweight="bold")
    axes[0].grid(axis="y", alpha=0.3)
    axes[0].legend()

    axes[1].bar(x - 0.18, v_dim, width=0.36, label="V-JEPA2")
    axes[1].bar(x + 0.18, c_dim, width=0.36, label="CLIP")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(conf_labels, rotation=15)
    axes[1].set_ylabel("Mean A/V/D partial R²")
    axes[1].set_title("Exp13 confound ablation: A/V/D", fontweight="bold")
    axes[1].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(CONFOUND_FIG, dpi=200, bbox_inches="tight")
    plt.close()

    print("\nSaved:")
    print(f"  {OUTPUT_PATH}")
    print(f"  {THRESH_FIG}")
    print(f"  {CONFOUND_FIG}")


if __name__ == "__main__":
    main()
