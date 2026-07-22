#!/usr/bin/env python3
"""Cortical transformation of shared video-brain information."""

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio
from scipy.stats import spearmanr, ttest_1samp, t
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler


def find_project_root():
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "CLAUDE.md").is_file() and (candidate / "study1").is_dir():
            return candidate
    raise RuntimeError("Could not locate the CCN project root")


ROOT = find_project_root()
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "study1/data/.matplotlib"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


N_CANONICAL = 2185
N_CORTICAL = 400
DEFAULT_BRAIN_PATH = ROOT / "data/raw/brain_embeddings/brain_jepa_embeddings.npy"
NETWORK_NAMES = ["Vis", "SomMot", "DorsAttn", "SalVentAttn", "Limbic", "Cont", "Default"]
NETWORK_PARCELS = {
    "Vis": list(range(0, 31)) + list(range(200, 230)),
    "SomMot": list(range(31, 68)) + list(range(230, 270)),
    "DorsAttn": list(range(68, 91)) + list(range(270, 293)),
    "SalVentAttn": list(range(91, 113)) + list(range(293, 318)),
    "Limbic": list(range(113, 126)) + list(range(318, 331)),
    "Cont": list(range(126, 148)) + list(range(331, 361)),
    "Default": list(range(148, 200)) + list(range(361, 400)),
}
MAP_LABELS = {
    "shared": "Shared channel",
    "unique_e34_shared": "Unique 34D beyond shared",
    "unique_av_shared": "Unique A/V beyond shared",
    "fine_grained_advantage": "Fine-grained advantage",
    "unique_e34_video": "Unique 34D beyond full video",
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-stim", type=int, default=N_CANONICAL)
    parser.add_argument("--n-parcels", type=int, default=N_CORTICAL)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--n-pca", type=int, default=100)
    parser.add_argument("--max-rank", type=int, default=20)
    parser.add_argument("--shared-rank", type=int, default=3)
    parser.add_argument("--n-shuffles", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--alphas", type=float, nargs="+", default=[0.1, 1.0, 10.0, 100.0, 1000.0])
    parser.add_argument("--alpha-cv", type=int, default=3)
    parser.add_argument("--brain-path", type=Path, default=DEFAULT_BRAIN_PATH)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "study1/results/cortical_transformation")
    parser.add_argument("--save-predictions", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--skip-brain-figure", action="store_true")
    parser.add_argument("--schaefer-atlas", type=Path, default=None)
    return parser.parse_args()


def load_mat_feature(name, n_stim):
    path = ROOT / "data/raw/feature" / f"{name}.mat"
    obj = sio.loadmat(path, squeeze_me=True, struct_as_record=False)["L"]
    values = np.asarray(obj.feat, dtype=np.float64)[:n_stim]
    labels = np.asarray(obj.featname, dtype=str).tolist()
    return values, labels


def load_inputs(args):
    video = np.load(
        ROOT / "data/raw/video_embeddings/emovis_vjepa2_pretrained.npy",
        mmap_mode="r",
    )[: args.n_stim].astype(np.float64)
    brain = np.load(args.brain_path, mmap_mode="r")[:, : args.n_stim].astype(np.float64)
    fmri = np.load(
        ROOT / "data/raw/raw_fmri/fmri_raw.npy",
        mmap_mode="r",
    )[:, : args.n_stim, : args.n_parcels].astype(np.float64)
    emotion, emotion_names = load_mat_feature("categcontinuous", args.n_stim)
    dimensions, dimension_names = load_mat_feature("dimension", args.n_stim)
    dim_lookup = {name.lower(): i for i, name in enumerate(dimension_names)}
    av = dimensions[:, [dim_lookup["arousal"], dim_lookup["valence"]]]

    arrays = {"video": video, "brain": brain, "fmri": fmri, "emotion": emotion, "av": av}
    for name, values in arrays.items():
        if not np.isfinite(values).all():
            raise ValueError(f"{name} contains non-finite values")
    if video.shape[0] != args.n_stim or brain.shape[1] != args.n_stim:
        raise ValueError("Stimulus counts do not match")
    return video, brain, fmri, emotion, av, emotion_names


class SharedAxes:
    """PCA-whitened cross-covariance SVD, fit on training stimuli only."""

    def __init__(self, n_pca, max_rank, seed):
        self.n_pca = n_pca
        self.max_rank = max_rank
        self.seed = seed

    def fit(self, video, brain):
        n_comp = min(self.n_pca, len(video) - 1, video.shape[1], brain.shape[1])
        self.video_scaler = StandardScaler().fit(video)
        self.brain_scaler = StandardScaler().fit(brain)
        self.video_pca = PCA(
            n_components=n_comp, whiten=True, svd_solver="randomized", random_state=self.seed
        ).fit(self.video_scaler.transform(video))
        self.brain_pca = PCA(
            n_components=n_comp, whiten=True, svd_solver="randomized", random_state=self.seed
        ).fit(self.brain_scaler.transform(brain))
        video_pc = self.video_pca.transform(self.video_scaler.transform(video))
        brain_pc = self.brain_pca.transform(self.brain_scaler.transform(brain))
        cross_cov = video_pc.T @ brain_pc / max(len(video_pc) - 1, 1)
        u, singular_values, vt = np.linalg.svd(cross_cov, full_matrices=False)
        rank = min(self.max_rank, u.shape[1])
        self.video_axes = u[:, :rank]
        self.brain_axes = vt.T[:, :rank]
        self.singular_values = singular_values[:rank]
        return self

    def transform_video_pca(self, video):
        return self.video_pca.transform(self.video_scaler.transform(video))

    def transform_video_shared(self, video):
        return self.transform_video_pca(video) @ self.video_axes

    def transform_brain_pca(self, brain):
        return self.brain_pca.transform(self.brain_scaler.transform(brain))

    def transform_brain_shared(self, brain):
        return self.transform_brain_pca(brain) @ self.brain_axes


def column_corr(a, b):
    a0 = a - a.mean(axis=0, keepdims=True)
    b0 = b - b.mean(axis=0, keepdims=True)
    denom = np.sqrt(np.sum(a0 * a0, axis=0) * np.sum(b0 * b0, axis=0))
    return np.divide(np.sum(a0 * b0, axis=0), denom, out=np.zeros(a.shape[1]), where=denom > 0)


def fit_predict_ridge(x_train, y_train, x_test, alphas, alpha_cv):
    x_scaler = StandardScaler().fit(x_train)
    x_train_z = x_scaler.transform(x_train)
    x_test_z = x_scaler.transform(x_test)
    y_mean = y_train.mean(axis=0)
    y_std = y_train.std(axis=0)
    y_std[y_std < 1e-12] = 1.0
    y_train_z = (y_train - y_mean) / y_std

    if len(alphas) == 1:
        model = Ridge(alpha=alphas[0])
    else:
        model = RidgeCV(alphas=alphas, cv=alpha_cv, scoring="neg_mean_squared_error")
    model.fit(x_train_z, y_train_z)
    pred = model.predict(x_test_z) * y_std + y_mean
    selected_alpha = model.alpha_ if hasattr(model, "alpha_") else model.alpha
    return pred, float(selected_alpha)


def parcel_metrics(y_true, y_pred):
    r2 = r2_score(y_true, y_pred, multioutput="raw_values")
    pearson = column_corr(y_true, y_pred)
    spearman = np.array([spearmanr(y_true[:, j], y_pred[:, j]).statistic for j in range(y_true.shape[1])])
    return r2, pearson, spearman


def network_ids(n_parcels):
    ids = np.full(n_parcels, -1, dtype=int)
    for network_i, network in enumerate(NETWORK_NAMES):
        parcel_idx = np.asarray(NETWORK_PARCELS[network], dtype=int)
        parcel_idx = parcel_idx[parcel_idx < n_parcels]
        ids[parcel_idx] = network_i
    return ids


def confidence_interval(values, confidence=0.95):
    values = np.asarray(values, dtype=float)
    mean = float(np.mean(values))
    if len(values) < 2:
        return mean, np.nan, np.nan
    sem = np.std(values, ddof=1) / np.sqrt(len(values))
    half = float(t.ppf((1 + confidence) / 2, len(values) - 1) * sem)
    return mean, mean - half, mean + half


def summarize_anatomy(maps, pg1, output_dir):
    n_subjects, n_parcels = maps["shared"].shape
    net_ids = network_ids(n_parcels)
    network_rows = []
    gradient_rows = []
    contrast_rows = []
    global_rows = []
    selected_maps = ["shared", "unique_e34_shared", "fine_grained_advantage", "unique_e34_video"]

    for map_name in selected_maps:
        for subject in range(n_subjects):
            values = maps[map_name][subject]
            global_rows.append(
                {"subject": subject + 1, "map": map_name, "cortical_mean": float(np.mean(values))}
            )
            rho, p_value = spearmanr(pg1[:n_parcels], values)
            gradient_rows.append(
                {"subject": subject + 1, "map": map_name, "spearman_r": rho, "p_value_descriptive": p_value}
            )
            network_means = {}
            for network_i, network in enumerate(NETWORK_NAMES):
                keep = net_ids == network_i
                value = float(np.mean(values[keep])) if np.any(keep) else np.nan
                network_means[network] = value
                network_rows.append(
                    {"subject": subject + 1, "map": map_name, "network": network, "mean_value": value}
                )
            visual = network_means["Vis"]
            transmodal = np.nanmean([network_means["Cont"], network_means["Default"]])
            direction = visual - transmodal if map_name == "shared" else transmodal - visual
            contrast_rows.append(
                {
                    "subject": subject + 1,
                    "map": map_name,
                    "visual": visual,
                    "transmodal_cont_default": transmodal,
                    "hypothesis_aligned_contrast": direction,
                }
            )

    network_df = pd.DataFrame(network_rows)
    gradient_df = pd.DataFrame(gradient_rows)
    contrast_df = pd.DataFrame(contrast_rows)
    global_df = pd.DataFrame(global_rows)
    network_df.to_csv(output_dir / "network_summary_subjectwise.csv", index=False)
    gradient_df.to_csv(output_dir / "gradient_summary_subjectwise.csv", index=False)
    contrast_df.to_csv(output_dir / "hierarchy_contrasts_subjectwise.csv", index=False)
    global_df.to_csv(output_dir / "map_means_subjectwise.csv", index=False)

    stats_rows = []
    for map_name in selected_maps:
        values = contrast_df.loc[contrast_df["map"] == map_name, "hypothesis_aligned_contrast"].values
        mean, ci_low, ci_high = confidence_interval(values)
        test = ttest_1samp(values, 0.0)
        grad = gradient_df.loc[gradient_df["map"] == map_name, "spearman_r"].values
        grad_mean, grad_low, grad_high = confidence_interval(grad)
        grad_test = ttest_1samp(grad, 0.0)
        global_values = global_df.loc[global_df["map"] == map_name, "cortical_mean"].values
        global_mean, global_low, global_high = confidence_interval(global_values)
        global_test = ttest_1samp(global_values, 0.0)
        stats_rows.append(
            {
                "map": map_name,
                "cortical_mean": global_mean,
                "cortical_mean_ci_low": global_low,
                "cortical_mean_ci_high": global_high,
                "cortical_mean_t": global_test.statistic,
                "cortical_mean_p": global_test.pvalue,
                "hierarchy_contrast_mean": mean,
                "hierarchy_ci_low": ci_low,
                "hierarchy_ci_high": ci_high,
                "hierarchy_t": test.statistic,
                "hierarchy_p": test.pvalue,
                "gradient_r_mean": grad_mean,
                "gradient_r_ci_low": grad_low,
                "gradient_r_ci_high": grad_high,
                "gradient_t": grad_test.statistic,
                "gradient_p": grad_test.pvalue,
            }
        )
    pd.DataFrame(stats_rows).to_csv(output_dir / "hierarchy_group_statistics.csv", index=False)
    return network_df, gradient_df, net_ids


def save_parcel_table(maps, pg1, net_ids, output_dir):
    table = {
        "parcel": np.arange(1, maps["shared"].shape[1] + 1),
        "network": [NETWORK_NAMES[i] if i >= 0 else "Unknown" for i in net_ids],
        "principal_gradient_1": pg1[: maps["shared"].shape[1]],
    }
    for map_name, values in maps.items():
        table[map_name] = values.mean(axis=0)
        table[f"{map_name}_sem_subject"] = values.std(axis=0, ddof=1) / np.sqrt(values.shape[0])
    pd.DataFrame(table).to_csv(output_dir / "parcel_maps_group.csv", index=False)


def plot_summary(maps, network_df, pg1, output_dir):
    selected = ["shared", "unique_e34_shared", "fine_grained_advantage"]
    colors = ["#0072B2", "#D55E00", "#009E73"]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    ax = axes[0, 0]
    x = np.arange(len(NETWORK_NAMES))
    width = 0.24
    for i, map_name in enumerate(selected):
        means, sems = [], []
        for network in NETWORK_NAMES:
            values = network_df.loc[
                (network_df["map"] == map_name) & (network_df["network"] == network), "mean_value"
            ].values
            means.append(np.mean(values))
            sems.append(np.std(values, ddof=1) / np.sqrt(len(values)))
        ax.bar(x + (i - 1) * width, means, width, yerr=sems, color=colors[i], label=MAP_LABELS[map_name])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x, NETWORK_NAMES, rotation=30, ha="right")
    ax.set_ylabel("Held-out R2 or delta R2")
    ax.set_title("Yeo 7 network summary")
    ax.legend(frameon=False, fontsize=8)

    for ax, map_name, color in zip(axes.flat[1:], selected, colors):
        group_map = maps[map_name].mean(axis=0)
        rho = spearmanr(pg1[: len(group_map)], group_map).statistic
        ax.scatter(pg1[: len(group_map)], group_map, s=10, alpha=0.55, color=color, edgecolors="none")
        slope, intercept = np.polyfit(pg1[: len(group_map)], group_map, 1)
        xx = np.linspace(np.min(pg1), np.max(pg1), 100)
        ax.plot(xx, slope * xx + intercept, color="black", linewidth=1.2)
        ax.axhline(0, color="0.65", linewidth=0.8)
        ax.set_xlabel("Principal gradient 1")
        ax.set_ylabel("Held-out R2 or delta R2")
        ax.set_title(f"{MAP_LABELS[map_name]} (group rho={rho:.2f})")
    fig.subplots_adjust(hspace=0.22)
    fig.savefig(output_dir / "cortical_transformation_summary.png", dpi=250)
    fig.savefig(output_dir / "cortical_transformation_summary.pdf")
    plt.close(fig)


def find_schaefer_atlas(requested):
    candidates = [
        requested,
        Path("/global/homes/s/sjmoon/nilearn_data/schaefer_2018/Schaefer2018_400Parcels_7Networks_order_FSLMNI152_2mm.nii.gz"),
        Path("/global/homes/s/sjmoon/nilearn_data/schaefer_2018/Schaefer2018_400Parcels_7Networks_order_FSLMNI152_1mm.nii.gz"),
    ]
    return next((path for path in candidates if path is not None and path.exists()), None)


def save_brain_maps(maps, atlas_path, output_dir):
    import nibabel as nib
    from nilearn import plotting

    atlas_img = nib.load(atlas_path)
    atlas_data = np.asarray(atlas_img.dataobj)
    labels = np.unique(atlas_data.astype(int))
    labels = labels[labels > 0]
    if len(labels) != N_CORTICAL:
        raise ValueError(f"Expected 400 Schaefer labels, found {len(labels)} in {atlas_path}")

    selected = ["shared", "unique_e34_shared", "fine_grained_advantage"]
    stat_images = []
    for map_name in selected:
        values = maps[map_name].mean(axis=0)
        volume = np.zeros(atlas_data.shape, dtype=np.float32)
        for parcel_i, label in enumerate(labels):
            volume[atlas_data == label] = values[parcel_i]
        image = nib.Nifti1Image(volume, atlas_img.affine, atlas_img.header)
        path = output_dir / f"brain_map_{map_name}.nii.gz"
        nib.save(image, path)
        stat_images.append(image)

    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    for ax, map_name, image in zip(axes, selected, stat_images):
        vmax = float(np.nanpercentile(np.abs(maps[map_name].mean(axis=0)), 98))
        vmax = max(vmax, 1e-6)
        plotting.plot_glass_brain(
            image,
            display_mode="lyrz",
            colorbar=True,
            cmap="RdBu_r",
            symmetric_cbar=True,
            vmax=vmax,
            axes=ax,
            title=MAP_LABELS[map_name],
            plot_abs=False,
        )
    fig.subplots_adjust(hspace=0.18)
    fig.savefig(output_dir / "cortical_brain_maps.png", dpi=250)
    fig.savefig(output_dir / "cortical_brain_maps.pdf")
    plt.close(fig)


def run(args):
    if args.smoke:
        args.n_stim = min(args.n_stim, 240)
        args.n_folds = 2
        args.n_pca = min(args.n_pca, 20)
        args.max_rank = min(args.max_rank, 5)
        args.shared_rank = min(args.shared_rank, 3)
        args.n_shuffles = min(args.n_shuffles, 5)
        args.alphas = [10.0]
        args.output_dir = args.output_dir / "smoke"
    if args.n_parcels > N_CORTICAL:
        raise ValueError("This analysis is cortical-only; --n-parcels must be <= 400")
    if args.shared_rank > args.max_rank:
        raise ValueError("--shared-rank cannot exceed --max-rank")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    video, brain, fmri, emotion, av, emotion_names = load_inputs(args)
    n_subjects, n_stim, n_parcels = fmri.shape
    print(f"Loaded video={video.shape}, Brain-JEPA={brain.shape}, BOLD={fmri.shape}")

    model_names = ["shared", "shared_e34", "shared_av", "video", "video_e34", "video_av"]
    predictions = {
        name: np.full((n_subjects, n_stim, n_parcels), np.nan, dtype=np.float32)
        for name in model_names
    }
    folds = list(KFold(n_splits=args.n_folds, shuffle=True, random_state=args.seed).split(video))
    canonical_corr = np.zeros((n_subjects, args.n_folds, args.max_rank))
    singular_values = np.zeros_like(canonical_corr)
    null_corr = np.zeros((n_subjects, args.n_folds, args.n_shuffles, args.max_rank))
    chosen_alphas = np.zeros((n_subjects, args.n_folds, len(model_names)))
    rng = np.random.default_rng(args.seed)

    for subject in range(n_subjects):
        discovery_subjects = [i for i in range(n_subjects) if i != subject]
        discovery_brain = brain[discovery_subjects].mean(axis=0)
        print(f"Subject {subject + 1}/{n_subjects}: discover on subjects {[i + 1 for i in discovery_subjects]}")
        for fold_i, (train_idx, test_idx) in enumerate(folds):
            shared_model = SharedAxes(args.n_pca, args.max_rank, args.seed + fold_i).fit(
                video[train_idx], discovery_brain[train_idx]
            )
            s_train_all = shared_model.transform_video_shared(video[train_idx])
            s_test_all = shared_model.transform_video_shared(video[test_idx])
            b_test_all = shared_model.transform_brain_shared(discovery_brain[test_idx])
            canonical_corr[subject, fold_i] = column_corr(s_test_all, b_test_all)[: args.max_rank]
            singular_values[subject, fold_i] = shared_model.singular_values[: args.max_rank]

            if args.n_shuffles:
                b_train_pc = shared_model.transform_brain_pca(discovery_brain[train_idx])
                v_train_pc = shared_model.transform_video_pca(video[train_idx])
                b_test_pc = shared_model.transform_brain_pca(discovery_brain[test_idx])
                v_test_pc = shared_model.transform_video_pca(video[test_idx])
                for shuffle_i in range(args.n_shuffles):
                    permuted = b_train_pc[rng.permutation(len(train_idx))]
                    u, _, vt = np.linalg.svd(v_train_pc.T @ permuted / (len(train_idx) - 1), full_matrices=False)
                    null_corr[subject, fold_i, shuffle_i] = column_corr(
                        v_test_pc @ u[:, : args.max_rank], b_test_pc @ vt.T[:, : args.max_rank]
                    )

            shared_train = s_train_all[:, : args.shared_rank]
            shared_test = s_test_all[:, : args.shared_rank]
            video_train = shared_model.transform_video_pca(video[train_idx])
            video_test = shared_model.transform_video_pca(video[test_idx])
            feature_sets = {
                "shared": (shared_train, shared_test),
                "shared_e34": (
                    np.column_stack([shared_train, emotion[train_idx]]),
                    np.column_stack([shared_test, emotion[test_idx]]),
                ),
                "shared_av": (
                    np.column_stack([shared_train, av[train_idx]]),
                    np.column_stack([shared_test, av[test_idx]]),
                ),
                "video": (video_train, video_test),
                "video_e34": (
                    np.column_stack([video_train, emotion[train_idx]]),
                    np.column_stack([video_test, emotion[test_idx]]),
                ),
                "video_av": (
                    np.column_stack([video_train, av[train_idx]]),
                    np.column_stack([video_test, av[test_idx]]),
                ),
            }
            for model_i, model_name in enumerate(model_names):
                pred, alpha = fit_predict_ridge(
                    feature_sets[model_name][0],
                    fmri[subject, train_idx],
                    feature_sets[model_name][1],
                    args.alphas,
                    args.alpha_cv,
                )
                predictions[model_name][subject, test_idx] = pred.astype(np.float32)
                chosen_alphas[subject, fold_i, model_i] = alpha
            print(f"  fold {fold_i + 1}/{args.n_folds} complete")

    metrics = {metric: {} for metric in ["r2", "pearson_r", "spearman_r"]}
    for model_name in model_names:
        metric_values = [parcel_metrics(fmri[s], predictions[model_name][s]) for s in range(n_subjects)]
        for metric_i, metric_name in enumerate(metrics):
            metrics[metric_name][model_name] = np.stack([value[metric_i] for value in metric_values])

    maps = {
        "shared": metrics["r2"]["shared"],
        "unique_e34_shared": metrics["r2"]["shared_e34"] - metrics["r2"]["shared"],
        "unique_av_shared": metrics["r2"]["shared_av"] - metrics["r2"]["shared"],
        "fine_grained_advantage": (
            metrics["r2"]["shared_e34"] - metrics["r2"]["shared_av"]
        ),
        "video": metrics["r2"]["video"],
        "unique_e34_video": metrics["r2"]["video_e34"] - metrics["r2"]["video"],
        "unique_av_video": metrics["r2"]["video_av"] - metrics["r2"]["video"],
    }

    pg1_path = ROOT / "study2_thesis/results/ch1d_principal_gradient.npz"
    pg1 = np.load(pg1_path)["pg1"].astype(float)[:n_parcels]
    network_df, gradient_df, net_ids = summarize_anatomy(maps, pg1, output_dir)
    save_parcel_table(maps, pg1, net_ids, output_dir)
    plot_summary(maps, network_df, pg1, output_dir)

    rank_rows = []
    for subject in range(n_subjects):
        for fold_i in range(args.n_folds):
            for component in range(args.max_rank):
                observed = canonical_corr[subject, fold_i, component]
                null_values = null_corr[subject, fold_i, :, component]
                p_empirical = (
                    (1 + np.sum(null_values >= observed)) / (1 + len(null_values))
                    if len(null_values)
                    else np.nan
                )
                rank_rows.append(
                    {
                        "subject": subject + 1,
                        "fold": fold_i + 1,
                        "component": component + 1,
                        "heldout_correlation": observed,
                        "train_singular_value": singular_values[subject, fold_i, component],
                        "fold_empirical_p": p_empirical,
                    }
                )
    pd.DataFrame(rank_rows).to_csv(output_dir / "shared_rank_diagnostics.csv", index=False)
    rank_group_rows = []
    for component in range(args.max_rank):
        observed = canonical_corr[:, :, component].reshape(-1)
        mean, ci_low, ci_high = confidence_interval(observed)
        if args.n_shuffles:
            null_group_means = null_corr[:, :, :, component].mean(axis=(0, 1))
            empirical_p = (1 + np.sum(null_group_means >= mean)) / (1 + len(null_group_means))
        else:
            empirical_p = np.nan
        rank_group_rows.append(
            {
                "component": component + 1,
                "heldout_correlation_mean": mean,
                "ci_low_over_subject_folds": ci_low,
                "ci_high_over_subject_folds": ci_high,
                "group_null_empirical_p": empirical_p,
                "positive_subject_fold_fraction": float(np.mean(observed > 0)),
            }
        )
    pd.DataFrame(rank_group_rows).to_csv(output_dir / "shared_rank_group_summary.csv", index=False)

    save_dict = {
        "canonical_corr": canonical_corr,
        "canonical_corr_null": null_corr,
        "train_singular_values": singular_values,
        "chosen_alphas": chosen_alphas,
        "model_names": np.asarray(model_names),
        "emotion_names": np.asarray(emotion_names),
        "network_names": np.asarray(NETWORK_NAMES),
        "principal_gradient_1": pg1,
    }
    for metric_name, model_results in metrics.items():
        for model_name, values in model_results.items():
            save_dict[f"{metric_name}_{model_name}"] = values
    for map_name, values in maps.items():
        save_dict[f"map_{map_name}"] = values
    np.savez_compressed(output_dir / "cortical_transformation_results.npz", **save_dict)

    if args.save_predictions:
        intermediate_dir = ROOT / "study1/data/cortical_transformation"
        if args.smoke:
            intermediate_dir = intermediate_dir / "smoke"
        intermediate_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(intermediate_dir / "oof_predictions.npz", **predictions)

    atlas_path = find_schaefer_atlas(args.schaefer_atlas)
    if not args.skip_brain_figure and n_parcels == N_CORTICAL and atlas_path is not None:
        print(f"Creating cortical brain maps with {atlas_path}")
        save_brain_maps(maps, atlas_path, output_dir)
    elif not args.skip_brain_figure:
        print("Brain figure skipped: a 400-parcel Schaefer atlas was not available")

    config = vars(args).copy()
    config["brain_path"] = str(args.brain_path.resolve())
    config["output_dir"] = str(output_dir)
    config["schaefer_atlas"] = str(atlas_path) if atlas_path else None
    config["root"] = str(ROOT)
    with open(output_dir / "run_config.json", "w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
    print(f"Finished. Results: {output_dir}")


if __name__ == "__main__":
    run(parse_args())
