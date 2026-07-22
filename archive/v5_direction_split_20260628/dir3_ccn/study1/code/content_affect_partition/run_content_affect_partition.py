#!/usr/bin/env python3
"""No-PCA content and affect variance partitioning in cortical BOLD."""

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio
from scipy.linalg import cho_factor, cho_solve
from scipy.stats import spearmanr, t, ttest_1samp
from sklearn.decomposition import PCA
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold, ShuffleSplit
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
EMOTION_RANKS = [2, 3, 5, 10, 20, 34]
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
    "video_content": "Raw video + visual-semantic",
    "unique_e34_vc": "Unique 34D beyond video + content",
    "fine_grained_vs_av": "34D advantage over arousal-valence",
    "matched_2d_vs_av": "Emotion PCA-2D advantage over A/V",
    "resolution_34d_vs_2d": "Fine-grained resolution gain: 34D vs 2D",
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-stim", type=int, default=N_CANONICAL)
    parser.add_argument("--n-parcels", type=int, default=N_CORTICAL)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--alphas", type=float, nargs="+", default=[0.01, 0.1, 1.0, 10.0])
    parser.add_argument("--inner-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--brain-path", type=Path, default=DEFAULT_BRAIN_PATH)
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "study1/results/content_affect_partition"
    )
    parser.add_argument("--schaefer-atlas", type=Path, default=None)
    parser.add_argument("--skip-brain-figure", action="store_true")
    parser.add_argument("--geometry-only", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def load_mat_feature(name, n_stim):
    obj = sio.loadmat(
        ROOT / "data/raw/feature" / f"{name}.mat",
        squeeze_me=True,
        struct_as_record=False,
    )["L"]
    return np.asarray(obj.feat, dtype=np.float64)[:n_stim]


def load_inputs(args):
    video = np.load(
        ROOT / "data/raw/video_embeddings/emovis_vjepa2_pretrained.npy", mmap_mode="r"
    )[: args.n_stim].astype(np.float64)
    brain = np.load(args.brain_path, mmap_mode="r")[:, : args.n_stim].astype(np.float64)
    fmri = np.load(ROOT / "data/raw/raw_fmri/fmri_raw.npy", mmap_mode="r")[
        :, : args.n_stim, : args.n_parcels
    ].astype(np.float64)
    vision = load_mat_feature("vision", args.n_stim)
    semantic = load_mat_feature("semantic", args.n_stim)
    emotion = load_mat_feature("categcontinuous", args.n_stim)
    dimensions = load_mat_feature("dimension", args.n_stim)
    dim_obj = sio.loadmat(
        ROOT / "data/raw/feature/dimension.mat", squeeze_me=True, struct_as_record=False
    )["L"]
    dim_names = [str(x).lower() for x in np.asarray(dim_obj.featname).tolist()]
    av = dimensions[:, [dim_names.index("arousal"), dim_names.index("valence")]]
    arrays = [video, brain, fmri, vision, semantic, emotion, av]
    if not all(np.isfinite(values).all() for values in arrays):
        raise ValueError("An input contains non-finite values")
    return video, brain, fmri, vision, semantic, emotion, av


def scale_block(train, test):
    scaler = StandardScaler().fit(train)
    return scaler.transform(train), scaler.transform(test)


def emotion_rank_features(train, test, rank, seed):
    train_z, test_z = scale_block(train, test)
    pca = PCA(n_components=rank, random_state=seed).fit(train_z)
    return scale_block(pca.transform(train_z), pca.transform(test_z))


def kernel_matrix(left, right, n_features):
    return left @ right.T / max(n_features, 1)


def solve_kernel(k_train, targets, alpha):
    regularized = k_train.copy()
    regularized.flat[:: len(regularized) + 1] += alpha + 1e-8
    factor = cho_factor(regularized, lower=True, check_finite=False)
    return cho_solve(factor, targets, check_finite=False)


def select_alpha(k_train, group_target, alphas, inner_fraction, seed):
    inner_train, inner_valid = next(
        ShuffleSplit(n_splits=1, test_size=inner_fraction, random_state=seed).split(k_train)
    )
    target_mean = group_target[inner_train].mean(axis=0)
    target_std = group_target[inner_train].std(axis=0)
    target_std[target_std < 1e-12] = 1.0
    y_train = (group_target[inner_train] - target_mean) / target_std
    y_valid = (group_target[inner_valid] - target_mean) / target_std
    scores = []
    for alpha in alphas:
        weights = solve_kernel(k_train[np.ix_(inner_train, inner_train)], y_train, alpha)
        pred = k_train[np.ix_(inner_valid, inner_train)] @ weights
        scores.append(np.nanmean(r2_score(y_valid, pred, multioutput="raw_values")))
    return float(alphas[int(np.argmax(scores))]), scores


def predict_all_subjects(k_train, k_test, fmri_train, alpha):
    y_mean = fmri_train.mean(axis=1)
    y_std = fmri_train.std(axis=1)
    y_std[y_std < 1e-12] = 1.0
    y_z = (fmri_train - y_mean[:, None, :]) / y_std[:, None, :]
    n_subjects, n_train, n_parcels = y_z.shape
    y_matrix = y_z.transpose(1, 0, 2).reshape(n_train, n_subjects * n_parcels)
    weights = solve_kernel(k_train, y_matrix, alpha)
    pred_z = (k_test @ weights).reshape(len(k_test), n_subjects, n_parcels).transpose(1, 0, 2)
    return pred_z * y_std[:, None, :] + y_mean[:, None, :]


def linear_cka(left, right):
    left = StandardScaler().fit_transform(left)
    right = StandardScaler().fit_transform(right)
    left -= left.mean(axis=0, keepdims=True)
    right -= right.mean(axis=0, keepdims=True)
    cross = left.T @ right
    left_self = left.T @ left
    right_self = right.T @ right
    numerator = np.sum(cross * cross)
    denominator = np.sqrt(np.sum(left_self * left_self) * np.sum(right_self * right_self))
    return float(numerator / denominator)


def column_corr(left, right):
    left = left - left.mean(axis=0, keepdims=True)
    right = right - right.mean(axis=0, keepdims=True)
    denom = np.sqrt(np.sum(left * left, axis=0) * np.sum(right * right, axis=0))
    return np.divide(np.sum(left * right, axis=0), denom, out=np.zeros(left.shape[1]), where=denom > 0)


def fdr_bh(p_values):
    p_values = np.asarray(p_values, dtype=float)
    order = np.argsort(p_values)
    ranked = p_values[order] * len(p_values) / np.arange(1, len(p_values) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty_like(ranked)
    out[order] = np.clip(ranked, 0, 1)
    return out


def confidence_interval(values):
    values = np.asarray(values, dtype=float)
    mean = float(np.mean(values))
    sem = np.std(values, ddof=1) / np.sqrt(len(values))
    half = float(t.ppf(0.975, len(values) - 1) * sem)
    return mean, mean - half, mean + half


def network_ids(n_parcels):
    ids = np.full(n_parcels, -1, dtype=int)
    for network_i, network in enumerate(NETWORK_NAMES):
        parcels = np.asarray(NETWORK_PARCELS[network])
        parcels = parcels[parcels < n_parcels]
        ids[parcels] = network_i
    return ids


def summarize_maps(maps, pg1, output_dir):
    ids = network_ids(maps["video_content"].shape[1])
    subject_rows, network_rows, gradient_rows, group_rows = [], [], [], []
    for map_name, values_by_subject in maps.items():
        global_values, hierarchy_values, gradient_values = [], [], []
        for subject, values in enumerate(values_by_subject):
            cortical_mean = float(np.mean(values))
            global_values.append(cortical_mean)
            net_means = {}
            for network_i, network in enumerate(NETWORK_NAMES):
                keep = ids == network_i
                net_mean = float(np.mean(values[keep]))
                net_means[network] = net_mean
                network_rows.append(
                    {"subject": subject + 1, "map": map_name, "network": network, "mean": net_mean}
                )
            hierarchy = np.mean([net_means["Cont"], net_means["Default"]]) - net_means["Vis"]
            rho = float(spearmanr(pg1, values).statistic)
            hierarchy_values.append(hierarchy)
            gradient_values.append(rho)
            subject_rows.append(
                {
                    "subject": subject + 1,
                    "map": map_name,
                    "cortical_mean": cortical_mean,
                    "transmodal_minus_visual": hierarchy,
                    "gradient_spearman_r": rho,
                }
            )
            gradient_rows.append({"subject": subject + 1, "map": map_name, "spearman_r": rho})
        global_mean, global_low, global_high = confidence_interval(global_values)
        hierarchy_mean, hierarchy_low, hierarchy_high = confidence_interval(hierarchy_values)
        gradient_mean, gradient_low, gradient_high = confidence_interval(gradient_values)
        group_rows.append(
            {
                "map": map_name,
                "cortical_mean": global_mean,
                "cortical_ci_low": global_low,
                "cortical_ci_high": global_high,
                "cortical_p": ttest_1samp(global_values, 0).pvalue,
                "transmodal_minus_visual": hierarchy_mean,
                "hierarchy_ci_low": hierarchy_low,
                "hierarchy_ci_high": hierarchy_high,
                "hierarchy_p": ttest_1samp(hierarchy_values, 0).pvalue,
                "gradient_r": gradient_mean,
                "gradient_ci_low": gradient_low,
                "gradient_ci_high": gradient_high,
                "gradient_p": ttest_1samp(gradient_values, 0).pvalue,
            }
        )
    group_df = pd.DataFrame(group_rows)
    for p_col in ["cortical_p", "hierarchy_p", "gradient_p"]:
        group_df[p_col.replace("_p", "_q_fdr")] = fdr_bh(group_df[p_col].values)
    pd.DataFrame(subject_rows).to_csv(output_dir / "map_statistics_subjectwise.csv", index=False)
    pd.DataFrame(network_rows).to_csv(output_dir / "network_summary_subjectwise.csv", index=False)
    pd.DataFrame(gradient_rows).to_csv(output_dir / "gradient_summary_subjectwise.csv", index=False)
    group_df.to_csv(output_dir / "map_statistics_group.csv", index=False)
    return pd.DataFrame(network_rows), ids


def find_schaefer_atlas(requested):
    candidates = [
        requested,
        Path("/global/homes/s/sjmoon/nilearn_data/schaefer_2018/Schaefer2018_400Parcels_7Networks_order_FSLMNI152_2mm.nii.gz"),
    ]
    return next((path for path in candidates if path is not None and path.exists()), None)


def save_brain_figure(maps, atlas_path, output_dir):
    import nibabel as nib
    from nilearn import plotting

    atlas = nib.load(atlas_path)
    atlas_data = np.asarray(atlas.dataobj).astype(int)
    labels = np.unique(atlas_data)
    labels = labels[labels > 0]
    selected = ["video_content", "unique_e34_vc", "fine_grained_vs_av", "resolution_34d_vs_2d"]
    images = []
    for map_name in selected:
        values = maps[map_name].mean(axis=0)
        volume = np.zeros(atlas_data.shape, dtype=np.float32)
        for parcel_i, label in enumerate(labels):
            volume[atlas_data == label] = values[parcel_i]
        image = nib.Nifti1Image(volume, atlas.affine, atlas.header)
        nib.save(image, output_dir / f"brain_map_{map_name}.nii.gz")
        images.append(image)
    fig, axes = plt.subplots(4, 1, figsize=(12, 13))
    for ax, map_name, image in zip(axes, selected, images):
        values = maps[map_name].mean(axis=0)
        vmax = max(float(np.percentile(np.abs(values), 98)), 1e-6)
        plotting.plot_glass_brain(
            image,
            display_mode="lyrz",
            axes=ax,
            colorbar=True,
            cmap="RdBu_r",
            symmetric_cbar=True,
            vmax=vmax,
            plot_abs=False,
            title=MAP_LABELS[map_name],
        )
    fig.subplots_adjust(hspace=0.18)
    fig.savefig(output_dir / "content_affect_brain_maps.png", dpi=250)
    fig.savefig(output_dir / "content_affect_brain_maps.pdf")
    plt.close(fig)


def plot_network_summary(maps, network_df, output_dir):
    selected = ["video_content", "unique_e34_vc", "fine_grained_vs_av", "matched_2d_vs_av"]
    colors = ["#0072B2", "#D55E00", "#009E73", "#CC79A7"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, map_name, color in zip(axes.flat, selected, colors):
        means, sems = [], []
        for network in NETWORK_NAMES:
            values = network_df.loc[
                (network_df["map"] == map_name) & (network_df["network"] == network), "mean"
            ].values
            means.append(np.mean(values))
            sems.append(np.std(values, ddof=1) / np.sqrt(len(values)))
        ax.bar(np.arange(7), means, yerr=sems, color=color)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(np.arange(7), NETWORK_NAMES, rotation=30, ha="right")
        ax.set_ylabel("Held-out R2 or delta R2")
        ax.set_title(MAP_LABELS[map_name])
    fig.tight_layout()
    fig.savefig(output_dir / "content_affect_network_summary.png", dpi=250)
    fig.savefig(output_dir / "content_affect_network_summary.pdf")
    plt.close(fig)


def run(args):
    if args.smoke:
        args.n_stim = min(args.n_stim, 240)
        args.n_folds = 2
        args.alphas = [1.0]
        args.output_dir = args.output_dir / "smoke"
    if args.n_parcels != N_CORTICAL:
        raise ValueError("This module currently requires all 400 cortical parcels")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    video, brain, fmri, vision, semantic, emotion, av = load_inputs(args)
    n_subjects, n_stim, n_parcels = fmri.shape
    print(
        f"Loaded video={video.shape}, content={(len(video), vision.shape[1] + semantic.shape[1])}, "
        f"Brain-JEPA={brain.shape}, BOLD={fmri.shape}"
    )

    content_full = np.column_stack([vision, semantic])
    geometry_rows = []
    geometry_inputs = {
        "raw_vjepa2": video,
        "visual_semantic": content_full,
        "emotion_34d": emotion,
        "arousal_valence": av,
    }
    for name, features in geometry_inputs.items():
        for subject in range(n_subjects):
            geometry_rows.append(
                {"representation": name, "subject": subject + 1, "linear_cka": linear_cka(features, brain[subject])}
            )
    pd.DataFrame(geometry_rows).to_csv(output_dir / "direct_geometry_cka.csv", index=False)
    if args.geometry_only:
        config = vars(args).copy()
        config["brain_path"] = str(args.brain_path.resolve())
        config["output_dir"] = str(output_dir)
        config["root"] = str(ROOT)
        config["schaefer_atlas"] = None
        with open(output_dir / "run_config.json", "w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2)
        print(f"Finished direct geometry only. Results: {output_dir}")
        return

    model_names = ["video", "content", "video_content", "vc_av"] + [
        f"vc_e{rank}" for rank in EMOTION_RANKS
    ]
    predictions = {
        name: np.full((n_subjects, n_stim, n_parcels), np.nan, dtype=np.float32)
        for name in model_names
    }
    selected_alphas = np.zeros((args.n_folds, len(model_names)))
    alpha_scores = np.zeros((args.n_folds, len(model_names), len(args.alphas)))
    folds = list(KFold(n_splits=args.n_folds, shuffle=True, random_state=args.seed).split(video))

    for fold_i, (train_idx, test_idx) in enumerate(folds):
        print(f"Fold {fold_i + 1}/{args.n_folds}")
        video_train, video_test = scale_block(video[train_idx], video[test_idx])
        vision_train, vision_test = scale_block(vision[train_idx], vision[test_idx])
        semantic_train, semantic_test = scale_block(semantic[train_idx], semantic[test_idx])
        av_train, av_test = scale_block(av[train_idx], av[test_idx])
        content_train = np.column_stack([vision_train, semantic_train])
        content_test = np.column_stack([vision_test, semantic_test])
        vc_train = np.column_stack([video_train, content_train])
        vc_test = np.column_stack([video_test, content_test])
        feature_sets = {
            "video": (video_train, video_test),
            "content": (content_train, content_test),
            "video_content": (vc_train, vc_test),
            "vc_av": (np.column_stack([vc_train, av_train]), np.column_stack([vc_test, av_test])),
        }
        for rank in EMOTION_RANKS:
            emotion_train, emotion_test = emotion_rank_features(
                emotion[train_idx], emotion[test_idx], rank, args.seed + fold_i
            )
            feature_sets[f"vc_e{rank}"] = (
                np.column_stack([vc_train, emotion_train]),
                np.column_stack([vc_test, emotion_test]),
            )

        group_target = fmri[:, train_idx].mean(axis=0)
        for model_i, model_name in enumerate(model_names):
            x_train, x_test = feature_sets[model_name]
            k_train = kernel_matrix(x_train, x_train, x_train.shape[1])
            k_test = kernel_matrix(x_test, x_train, x_train.shape[1])
            alpha, scores = select_alpha(
                k_train, group_target, args.alphas, args.inner_fraction, args.seed + fold_i
            )
            selected_alphas[fold_i, model_i] = alpha
            alpha_scores[fold_i, model_i] = scores
            pred = predict_all_subjects(k_train, k_test, fmri[:, train_idx], alpha)
            predictions[model_name][:, test_idx] = pred.astype(np.float32)
            print(f"  {model_name}: p={x_train.shape[1]}, alpha={alpha:g}")

    r2 = {}
    pearson = {}
    for model_name in model_names:
        r2[model_name] = np.stack(
            [r2_score(fmri[s], predictions[model_name][s], multioutput="raw_values") for s in range(n_subjects)]
        )
        pearson[model_name] = np.stack(
            [column_corr(fmri[s], predictions[model_name][s]) for s in range(n_subjects)]
        )

    maps = {
        "video": r2["video"],
        "content": r2["content"],
        "video_content": r2["video_content"],
        "unique_video_given_content": r2["video_content"] - r2["content"],
        "unique_content_given_video": r2["video_content"] - r2["video"],
        "commonality_video_content": r2["video"] + r2["content"] - r2["video_content"],
        "unique_av_vc": r2["vc_av"] - r2["video_content"],
        "unique_e2_vc": r2["vc_e2"] - r2["video_content"],
        "unique_e34_vc": r2["vc_e34"] - r2["video_content"],
        "matched_2d_vs_av": r2["vc_e2"] - r2["vc_av"],
        "fine_grained_vs_av": r2["vc_e34"] - r2["vc_av"],
        "resolution_34d_vs_2d": r2["vc_e34"] - r2["vc_e2"],
    }
    for rank in EMOTION_RANKS:
        maps[f"unique_e{rank}_vc"] = r2[f"vc_e{rank}"] - r2["video_content"]

    pg1 = np.load(ROOT / "study2_thesis/results/ch1d_principal_gradient.npz")["pg1"][:n_parcels]
    network_df, ids = summarize_maps(maps, pg1, output_dir)
    plot_network_summary(maps, network_df, output_dir)

    parcel_table = {
        "parcel": np.arange(1, n_parcels + 1),
        "network": [NETWORK_NAMES[i] for i in ids],
        "principal_gradient_1": pg1,
    }
    for name, values in maps.items():
        parcel_table[name] = values.mean(axis=0)
        parcel_table[f"{name}_sem"] = values.std(axis=0, ddof=1) / np.sqrt(n_subjects)
    pd.DataFrame(parcel_table).to_csv(output_dir / "parcel_maps_group.csv", index=False)

    atlas_path = find_schaefer_atlas(args.schaefer_atlas)
    if not args.skip_brain_figure and atlas_path is not None:
        save_brain_figure(maps, atlas_path, output_dir)

    save_data = {
        "model_names": np.asarray(model_names),
        "selected_alphas": selected_alphas,
        "alpha_scores": alpha_scores,
        "principal_gradient_1": pg1,
    }
    for name in model_names:
        save_data[f"r2_{name}"] = r2[name]
        save_data[f"pearson_{name}"] = pearson[name]
    for name, values in maps.items():
        save_data[f"map_{name}"] = values
    np.savez_compressed(output_dir / "content_affect_partition_results.npz", **save_data)

    config = vars(args).copy()
    config["brain_path"] = str(args.brain_path.resolve())
    config["output_dir"] = str(output_dir)
    config["root"] = str(ROOT)
    config["schaefer_atlas"] = str(atlas_path) if atlas_path else None
    with open(output_dir / "run_config.json", "w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
    print(f"Finished. Results: {output_dir}")


if __name__ == "__main__":
    run(parse_args())
