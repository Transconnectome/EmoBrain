#!/usr/bin/env python3
"""Benchmark corrected Brain-JEPA short-window validity on Horikawa stimuli."""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio
from scipy.stats import ttest_1samp
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold, ShuffleSplit
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
EMOBRAIN_ROOT = ROOT.parents[1]
CCN_ROOT = (
    EMOBRAIN_ROOT / "archive/v5_direction_split_20260628/dir3_ccn"
)
sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "outputs/.matplotlib"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lib.metrics import linear_cka, neighbor_overlap, rsa_spearman


N_STIM = 2185
CONDITIONS = {
    "pre_native_mean": "init-pretrained_pos-native_input-mean",
    "scratch_native_mean": "init-scratch_pos-native_input-mean",
    "pre_legacy_mean": "init-pretrained_pos-temporal_mean_input-mean",
    "pre_center_mean": "init-pretrained_pos-temporal_center_input-mean",
    "pre_native_zero": "init-pretrained_pos-native_input-zero",
    "pre_native_spatial": "init-pretrained_pos-native_input-spatial_only",
    "pre_native_shuffle": "init-pretrained_pos-native_input-time_shuffle",
}
CONTRASTS = {
    "pretraining": ("pre_native_mean", "scratch_native_mean"),
    "native_minus_legacy_position": ("pre_native_mean", "pre_legacy_mean"),
    "native_minus_center_position": ("pre_native_mean", "pre_center_mean"),
    "mean_minus_zero_padding": ("pre_native_mean", "pre_native_zero"),
    "temporal_information_vs_spatial": ("pre_native_mean", "pre_native_spatial"),
    "temporal_order_vs_shuffle": ("pre_native_mean", "pre_native_shuffle"),
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-stim", type=int, default=N_STIM)
    parser.add_argument("--n-subjects", type=int, default=5)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--target-rank", type=int, default=100)
    parser.add_argument("--alphas", type=float, nargs="+", default=[0.1, 1.0, 10.0, 100.0])
    parser.add_argument("--inner-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--conditions", nargs="+", choices=list(CONDITIONS), default=None)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def load_condition(directory_name, args):
    directory = ROOT / "outputs/horikawa_embeddings" / directory_name
    if args.smoke:
        directory = ROOT / "outputs/smoke/horikawa_embeddings" / directory_name
    arrays, ids, original_times = [], [], []
    for subject in range(1, args.n_subjects + 1):
        path = directory / f"sub-{subject:02d}.npz"
        if not path.is_file():
            raise FileNotFoundError(path)
        payload = np.load(path)
        arrays.append(np.asarray(payload["embeddings"][: args.n_stim], dtype=np.float64))
        ids.append(np.asarray(payload["stim_num"][: args.n_stim]))
        original_times.append(np.asarray(payload["original_T"][: args.n_stim]))
    if not all(np.array_equal(ids[0], values) for values in ids[1:]):
        raise ValueError(f"Stimulus order differs between subjects in {directory}")
    return np.stack(arrays), np.stack(original_times)


def load_mat(name, n_stim):
    obj = sio.loadmat(
        CCN_ROOT / "data/raw/feature" / f"{name}.mat",
        squeeze_me=True,
        struct_as_record=False,
    )["L"]
    return np.asarray(obj.feat, dtype=np.float64)[:n_stim]


def load_targets(n_stim):
    video = np.load(
        CCN_ROOT / "data/raw/video_embeddings/emovis_vjepa2_pretrained.npy", mmap_mode="r"
    )[:n_stim].astype(np.float64)
    visual = load_mat("vision", n_stim)
    semantic = load_mat("semantic", n_stim)
    emotion = load_mat("categcontinuous", n_stim)
    dimensions = load_mat("dimension", n_stim)
    dim_obj = sio.loadmat(
        CCN_ROOT / "data/raw/feature/dimension.mat",
        squeeze_me=True,
        struct_as_record=False,
    )["L"]
    names = [str(value).lower() for value in np.asarray(dim_obj.featname).tolist()]
    av = dimensions[:, [names.index("arousal"), names.index("valence")]]
    return {
        "raw_vjepa2": video,
        "visual_semantic": np.concatenate([visual, semantic], axis=1),
        "emotion_pca2": emotion,
        "emotion_34d": emotion,
        "arousal_valence": av,
    }


def transform_target(train, test, target_name, rank, seed):
    scaler = StandardScaler().fit(train)
    train_z, test_z = scaler.transform(train), scaler.transform(test)
    if target_name in {"raw_vjepa2", "visual_semantic"}:
        n_components = min(rank, len(train_z) - 1, train_z.shape[1])
        pca = PCA(n_components=n_components, svd_solver="randomized", random_state=seed)
        return pca.fit_transform(train_z), pca.transform(test_z)
    if target_name == "emotion_pca2":
        pca = PCA(n_components=2, random_state=seed)
        return pca.fit_transform(train_z), pca.transform(test_z)
    return train_z, test_z


def select_alpha(features, target, target_name, args, seed):
    train, valid = next(
        ShuffleSplit(n_splits=1, test_size=args.inner_fraction, random_state=seed).split(features)
    )
    x_scaler = StandardScaler().fit(features[train])
    x_train, x_valid = x_scaler.transform(features[train]), x_scaler.transform(features[valid])
    y_train, y_valid = transform_target(
        target[train], target[valid], target_name, args.target_rank, seed
    )
    scores = []
    for alpha in args.alphas:
        prediction = Ridge(alpha=alpha).fit(x_train, y_train).predict(x_valid)
        scores.append(float(np.mean(r2_score(y_valid, prediction, multioutput="raw_values"))))
    return float(args.alphas[int(np.argmax(scores))])


def crossvalidated_encoding(features, targets, condition, subject, args):
    rows = []
    folds = KFold(n_splits=args.n_folds, shuffle=True, random_state=args.seed)
    for fold, (train, test) in enumerate(folds.split(features), start=1):
        x_scaler = StandardScaler().fit(features[train])
        x_train, x_test = x_scaler.transform(features[train]), x_scaler.transform(features[test])
        for target_name, target in targets.items():
            alpha = select_alpha(
                features[train], target[train], target_name, args, args.seed + fold
            )
            y_train, y_test = transform_target(
                target[train], target[test], target_name, args.target_rank, args.seed + fold
            )
            prediction = Ridge(alpha=alpha).fit(x_train, y_train).predict(x_test)
            component_scores = r2_score(y_test, prediction, multioutput="raw_values")
            rows.append(
                {
                    "condition": condition,
                    "subject": subject,
                    "fold": fold,
                    "target": target_name,
                    "alpha": alpha,
                    "mean_r2": float(np.mean(component_scores)),
                    "median_r2": float(np.median(component_scores)),
                    "n_target_dimensions": int(len(component_scores)),
                }
            )
    return rows


def representation_stability(embeddings, original_times, targets):
    rows, length_rows = [], []
    names = list(embeddings)
    for left_i, left_name in enumerate(names):
        for right_name in names[left_i + 1 :]:
            for subject in range(embeddings[left_name].shape[0]):
                left, right = embeddings[left_name][subject], embeddings[right_name][subject]
                rows.append(
                    {
                        "left": left_name,
                        "right": right_name,
                        "subject": subject + 1,
                        "linear_cka": linear_cka(left, right),
                        "rsa_spearman": rsa_spearman(left, right),
                        "neighbor_overlap_k10": neighbor_overlap(left, right, k=10),
                    }
                )
    primary = embeddings["pre_native_mean"]
    lengths = original_times["pre_native_mean"]
    for subject in range(primary.shape[0]):
        for label, keep in {
            "T_le_5": lengths[subject] <= 5,
            "T_6_to_15": (lengths[subject] >= 6) & (lengths[subject] <= 15),
            "T_ge_16": lengths[subject] >= 16,
        }.items():
            if keep.sum() < 20:
                continue
            for target_name, target in targets.items():
                length_rows.append(
                    {
                        "subject": subject + 1,
                        "length_bin": label,
                        "n_stimuli": int(keep.sum()),
                        "target": target_name,
                        "linear_cka": linear_cka(primary[subject, keep], target[keep]),
                    }
                )
    return pd.DataFrame(rows), pd.DataFrame(length_rows)


def contrast_table(subject_scores):
    rows = []
    for contrast, (left, right) in CONTRASTS.items():
        left_frame = subject_scores[subject_scores["condition"] == left]
        right_frame = subject_scores[subject_scores["condition"] == right]
        if left_frame.empty or right_frame.empty:
            continue
        merged = left_frame.merge(right_frame, on=["subject", "target"], suffixes=("_left", "_right"))
        for target, values in merged.groupby("target"):
            differences = values["subject_mean_r2_left"] - values["subject_mean_r2_right"]
            test = ttest_1samp(differences, 0.0) if len(differences) > 1 else None
            rows.append(
                {
                    "contrast": contrast,
                    "left": left,
                    "right": right,
                    "target": target,
                    "mean_difference": float(differences.mean()),
                    "min_difference": float(differences.min()),
                    "subjects_positive": int((differences > 0).sum()),
                    "n_subjects": int(len(differences)),
                    "exploratory_t": None if test is None else float(test.statistic),
                    "exploratory_p": None if test is None else float(test.pvalue),
                }
            )
    return pd.DataFrame(rows)


def save_figure(subject_scores, output_dir):
    targets = ["raw_vjepa2", "visual_semantic", "emotion_pca2", "arousal_valence"]
    conditions = list(subject_scores["condition"].drop_duplicates())
    fig, axes = plt.subplots(1, len(targets), figsize=(14, 4))
    colors = plt.cm.tab10(np.linspace(0, 1, len(conditions)))
    for axis, target in zip(axes, targets):
        subset = subject_scores[subject_scores["target"] == target]
        means = [subset.loc[subset["condition"] == name, "subject_mean_r2"].mean() for name in conditions]
        errors = [subset.loc[subset["condition"] == name, "subject_mean_r2"].sem() for name in conditions]
        axis.bar(range(len(conditions)), means, yerr=errors, color=colors, capsize=2)
        axis.axhline(0, color="black", linewidth=0.8)
        axis.set_title(target.replace("_", " "))
        axis.set_xticks(range(len(conditions)))
        axis.set_xticklabels(conditions, rotation=70, ha="right", fontsize=7)
        axis.set_ylabel("Held-out mean R2")
    fig.tight_layout()
    fig.savefig(output_dir / "short_window_benchmark.png", dpi=250)
    fig.savefig(output_dir / "short_window_benchmark.pdf")
    plt.close(fig)


def main():
    args = parse_args()
    output_dir = ROOT / "outputs/short_window_benchmark"
    if args.smoke:
        args.n_stim = min(args.n_stim, 12)
        args.n_subjects = 1
        args.n_folds = 3
        args.target_rank = 10
        args.alphas = [1.0, 100.0]
        if args.conditions is None:
            args.conditions = ["pre_native_mean"]
        output_dir = ROOT / "outputs/smoke/short_window_benchmark"
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = load_targets(args.n_stim)
    embeddings, original_times = {}, {}
    selected_conditions = args.conditions or list(CONDITIONS)
    for name in selected_conditions:
        directory = CONDITIONS[name]
        embeddings[name], original_times[name] = load_condition(directory, args)
        print(f"Loaded {name}: {embeddings[name].shape}")
    raw_bold = np.load(CCN_ROOT / "data/raw/raw_fmri/fmri_raw.npy", mmap_mode="r")[
        : args.n_subjects, : args.n_stim, :400
    ].astype(np.float64)

    geometry_rows = []
    all_features = {**embeddings, "raw_bold": raw_bold}
    for condition, values in all_features.items():
        for subject in range(values.shape[0]):
            for target_name, target in targets.items():
                geometry_rows.append(
                    {
                        "condition": condition,
                        "subject": subject + 1,
                        "target": target_name,
                        "linear_cka": linear_cka(values[subject], target),
                    }
                )

    fold_rows = []
    for condition, values in all_features.items():
        for subject in range(values.shape[0]):
            fold_rows.extend(
                crossvalidated_encoding(values[subject], targets, condition, subject + 1, args)
            )
    fold_frame = pd.DataFrame(fold_rows)
    subject_scores = (
        fold_frame.groupby(["condition", "subject", "target"], as_index=False)["mean_r2"]
        .mean()
        .rename(columns={"mean_r2": "subject_mean_r2"})
    )
    stability, length_stratified = representation_stability(
        embeddings, original_times, targets
    )
    contrasts = contrast_table(subject_scores)

    pd.DataFrame(geometry_rows).to_csv(output_dir / "direct_geometry_cka.csv", index=False)
    fold_frame.to_csv(output_dir / "fold_encoding_scores.csv", index=False)
    subject_scores.to_csv(output_dir / "subject_encoding_scores.csv", index=False)
    stability.to_csv(output_dir / "embedding_stability.csv", index=False)
    length_stratified.to_csv(output_dir / "length_stratified_cka.csv", index=False)
    contrasts.to_csv(output_dir / "planned_contrasts.csv", index=False)
    save_figure(subject_scores, output_dir)

    config = {
        "n_stim": args.n_stim,
        "n_subjects": args.n_subjects,
        "n_folds": args.n_folds,
        "target_rank": args.target_rank,
        "alphas": args.alphas,
        "conditions": {name: CONDITIONS[name] for name in selected_conditions},
        "contrasts": CONTRASTS,
        "interpretation": (
            "Pretrained-vs-scratch tests transferred pretrained structure. Position and input "
            "contrasts test sensitivity. They do not establish native 160-TR temporal equivalence."
        ),
    }
    with open(output_dir / "run_config.json", "w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
    print(f"Finished: {output_dir}")


if __name__ == "__main__":
    main()
