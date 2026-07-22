#!/usr/bin/env python3
"""Compare video/content/affect alignment across brain encoders and raw BOLD."""

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold, ShuffleSplit
from sklearn.preprocessing import StandardScaler


def find_ccn_root():
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "CLAUDE.md").is_file() and (candidate / "study1").is_dir():
            return candidate
    raise RuntimeError("Could not locate the CCN project root")


ROOT = find_ccn_root()
EMOBRAIN_ROOT = next(parent for parent in ROOT.parents if parent.name == "EmoBrain")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "study1/data/.matplotlib"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


N_CANONICAL = 2185
ENCODER_DIRS = {
    "brain_jepa_native_pretrained": ROOT
    / "study1/data/brain_encoder_validation/embeddings/brain_jepa_resting_pos-native_pad-mean",
    "brain_jepa_native_scratch": ROOT
    / "study1/data/brain_encoder_validation/embeddings/brain_jepa_scratch_pos-native_pad-mean",
    "brain_jepa_legacy_mean_pretrained": EMOBRAIN_ROOT
    / "project/shared/output/embeddings/brain_jepa_resting_pad-mean",
    "brain_jepa_legacy_mean_scratch": EMOBRAIN_ROOT
    / "project/shared/output/embeddings/brain_jepa_scratch_pad-mean",
    "swift_e96_pretrained": EMOBRAIN_ROOT
    / "project/shared/output/embeddings/swift_NewE96_SL20_resting_pad-mean",
    "swift_e96_scratch": EMOBRAIN_ROOT
    / "project/shared/output/embeddings/swift_NewE96_SL20_scratch_pad-mean",
    "neurostorm_pretrained": EMOBRAIN_ROOT
    / "project/shared/output/embeddings/neurostorm_resting_pad-mean",
    "neurostorm_scratch": EMOBRAIN_ROOT
    / "project/shared/output/embeddings/neurostorm_scratch_pad-mean",
}
PRETRAINED_SCRATCH_PAIRS = {
    "brain_jepa_native": ("brain_jepa_native_pretrained", "brain_jepa_native_scratch"),
    "brain_jepa_legacy_mean": (
        "brain_jepa_legacy_mean_pretrained",
        "brain_jepa_legacy_mean_scratch",
    ),
    "swift_e96": ("swift_e96_pretrained", "swift_e96_scratch"),
    "neurostorm": ("neurostorm_pretrained", "neurostorm_scratch"),
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-stim", type=int, default=N_CANONICAL)
    parser.add_argument("--n-subjects", type=int, default=5)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--target-pca-rank", type=int, default=100)
    parser.add_argument("--alphas", type=float, nargs="+", default=[0.1, 1.0, 10.0, 100.0])
    parser.add_argument("--inner-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--allow-missing-corrected", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "study1/results/brain_encoder_validation/consensus",
    )
    return parser.parse_args()


def torch_load(path):
    try:
        return torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        return torch.load(path, map_location="cpu")


def load_subject_file(directory, subject, n_stim):
    stem = directory / f"sub-{subject:02d}"
    if stem.with_suffix(".npz").is_file():
        payload = np.load(stem.with_suffix(".npz"))
        embeddings = np.asarray(payload["embeddings"], dtype=np.float64)
        stim_num = np.asarray(payload["stim_num"])
    elif stem.with_suffix(".pt").is_file():
        payload = torch_load(stem.with_suffix(".pt"))
        embeddings = payload["embeddings"]
        stim_num = payload.get("stim_num")
        if hasattr(embeddings, "detach"):
            embeddings = embeddings.detach().cpu().numpy()
        if hasattr(stim_num, "detach"):
            stim_num = stim_num.detach().cpu().numpy()
        embeddings = np.asarray(embeddings, dtype=np.float64)
        stim_num = None if stim_num is None else np.asarray(stim_num)
    else:
        raise FileNotFoundError(f"No .npz or .pt file for sub-{subject:02d} in {directory}")
    embeddings = embeddings[:n_stim].reshape(n_stim, -1)
    if not np.isfinite(embeddings).all():
        raise ValueError(f"Non-finite embedding values in {stem}")
    return embeddings, None if stim_num is None else stim_num[:n_stim]


def load_encoder(directory, n_subjects, n_stim):
    arrays, stimulus_ids = [], []
    for subject in range(1, n_subjects + 1):
        embeddings, stim_num = load_subject_file(directory, subject, n_stim)
        arrays.append(embeddings)
        if stim_num is not None:
            stimulus_ids.append(stim_num)
    if stimulus_ids and not all(np.array_equal(stimulus_ids[0], ids) for ids in stimulus_ids[1:]):
        raise ValueError(f"Subject stimulus order differs in {directory}")
    return np.stack(arrays)


def load_mat_feature(name, n_stim):
    obj = sio.loadmat(
        ROOT / "data/raw/feature" / f"{name}.mat", squeeze_me=True, struct_as_record=False
    )["L"]
    return np.asarray(obj.feat, dtype=np.float64)[:n_stim]


def load_targets(n_stim):
    video = np.load(
        ROOT / "data/raw/video_embeddings/emovis_vjepa2_pretrained.npy", mmap_mode="r"
    )[:n_stim].astype(np.float64)
    visual = load_mat_feature("vision", n_stim)
    semantic = load_mat_feature("semantic", n_stim)
    emotion = load_mat_feature("categcontinuous", n_stim)
    dimensions = load_mat_feature("dimension", n_stim)
    dim_obj = sio.loadmat(
        ROOT / "data/raw/feature/dimension.mat", squeeze_me=True, struct_as_record=False
    )["L"]
    dim_names = [str(value).lower() for value in np.asarray(dim_obj.featname).tolist()]
    av = dimensions[:, [dim_names.index("arousal"), dim_names.index("valence")]]
    return {
        "raw_vjepa2": video,
        "visual_semantic": np.concatenate([visual, semantic], axis=1),
        "emotion_34d": emotion,
        "arousal_valence": av,
    }


def linear_cka(left, right):
    left = StandardScaler().fit_transform(left)
    right = StandardScaler().fit_transform(right)
    cross = left.T @ right
    left_self = left.T @ left
    right_self = right.T @ right
    denominator = np.sqrt(np.sum(left_self**2) * np.sum(right_self**2))
    return float(np.sum(cross**2) / denominator) if denominator > 0 else np.nan


def transform_target(train, test, target_name, pca_rank, seed):
    scaler = StandardScaler().fit(train)
    train_z, test_z = scaler.transform(train), scaler.transform(test)
    if target_name in {"raw_vjepa2", "visual_semantic"}:
        rank = min(pca_rank, train_z.shape[0] - 1, train_z.shape[1])
        pca = PCA(n_components=rank, svd_solver="randomized", random_state=seed).fit(train_z)
        return pca.transform(train_z), pca.transform(test_z)
    if target_name == "emotion_pca2":
        pca = PCA(n_components=2, random_state=seed).fit(train_z)
        return pca.transform(train_z), pca.transform(test_z)
    return train_z, test_z


def select_alpha(x_train, y_train, target_name, args, fold_seed):
    inner_train, inner_valid = next(
        ShuffleSplit(
            n_splits=1, test_size=args.inner_fraction, random_state=fold_seed
        ).split(x_train)
    )
    x_scaler = StandardScaler().fit(x_train[inner_train])
    x_fit = x_scaler.transform(x_train[inner_train])
    x_valid = x_scaler.transform(x_train[inner_valid])
    y_fit, y_valid = transform_target(
        y_train[inner_train],
        y_train[inner_valid],
        target_name,
        args.target_pca_rank,
        fold_seed,
    )
    scores = []
    for alpha in args.alphas:
        prediction = Ridge(alpha=alpha).fit(x_fit, y_fit).predict(x_valid)
        scores.append(float(np.mean(r2_score(y_valid, prediction, multioutput="raw_values"))))
    return float(args.alphas[int(np.argmax(scores))])


def crossvalidated_scores(features, targets, args, encoder_name, subject):
    rows = []
    folds = KFold(n_splits=args.n_folds, shuffle=True, random_state=args.seed)
    target_specs = {
        "raw_vjepa2": targets["raw_vjepa2"],
        "visual_semantic": targets["visual_semantic"],
        "emotion_pca2": targets["emotion_34d"],
        "emotion_34d": targets["emotion_34d"],
        "arousal_valence": targets["arousal_valence"],
    }
    for fold, (train, test) in enumerate(folds.split(features), start=1):
        x_scaler = StandardScaler().fit(features[train])
        x_train = x_scaler.transform(features[train])
        x_test = x_scaler.transform(features[test])
        for target_name, target in target_specs.items():
            alpha = select_alpha(
                features[train], target[train], target_name, args, args.seed + fold
            )
            y_train, y_test = transform_target(
                target[train], target[test], target_name, args.target_pca_rank, args.seed + fold
            )
            prediction = Ridge(alpha=alpha).fit(x_train, y_train).predict(x_test)
            component_r2 = r2_score(y_test, prediction, multioutput="raw_values")
            rows.append(
                {
                    "encoder": encoder_name,
                    "subject": subject,
                    "fold": fold,
                    "target": target_name,
                    "alpha": alpha,
                    "mean_r2": float(np.mean(component_r2)),
                    "median_r2": float(np.median(component_r2)),
                    "n_target_dimensions": int(len(component_r2)),
                }
            )
    return rows


def summarize_results(fold_frame):
    subject = (
        fold_frame.groupby(["encoder", "subject", "target"], as_index=False)["mean_r2"]
        .mean()
        .rename(columns={"mean_r2": "subject_mean_r2"})
    )
    summary = (
        subject.groupby(["encoder", "target"], as_index=False)
        .agg(
            mean=("subject_mean_r2", "mean"),
            std=("subject_mean_r2", "std"),
            minimum=("subject_mean_r2", "min"),
            maximum=("subject_mean_r2", "max"),
            n_subjects=("subject_mean_r2", "count"),
        )
    )
    return subject, summary


def pretraining_deltas(subject_frame):
    rows = []
    for family, (pretrained, scratch) in PRETRAINED_SCRATCH_PAIRS.items():
        pre = subject_frame[subject_frame["encoder"] == pretrained]
        scr = subject_frame[subject_frame["encoder"] == scratch]
        if pre.empty or scr.empty:
            continue
        merged = pre.merge(scr, on=["subject", "target"], suffixes=("_pretrained", "_scratch"))
        for row in merged.itertuples(index=False):
            rows.append(
                {
                    "family": family,
                    "subject": row.subject,
                    "target": row.target,
                    "pretrained_r2": row.subject_mean_r2_pretrained,
                    "scratch_r2": row.subject_mean_r2_scratch,
                    "pretrained_minus_scratch": (
                        row.subject_mean_r2_pretrained - row.subject_mean_r2_scratch
                    ),
                }
            )
    return pd.DataFrame(rows)


def save_figure(subject_frame, output_dir):
    targets = ["raw_vjepa2", "visual_semantic", "emotion_pca2", "arousal_valence"]
    encoders = list(dict.fromkeys(subject_frame["encoder"]))
    fig, axes = plt.subplots(1, len(targets), figsize=(14, 3.6), sharey=False)
    colors = plt.cm.tab10(np.linspace(0, 1, max(len(encoders), 1)))
    for axis, target in zip(axes, targets):
        subset = subject_frame[subject_frame["target"] == target]
        means = [subset.loc[subset["encoder"] == encoder, "subject_mean_r2"].mean() for encoder in encoders]
        sems = [
            subset.loc[subset["encoder"] == encoder, "subject_mean_r2"].sem() for encoder in encoders
        ]
        axis.bar(range(len(encoders)), means, yerr=sems, color=colors, capsize=2)
        axis.axhline(0, color="black", linewidth=0.8)
        axis.set_title(target.replace("_", " "))
        axis.set_xticks(range(len(encoders)))
        axis.set_xticklabels(encoders, rotation=70, ha="right", fontsize=7)
        axis.set_ylabel("Held-out mean $R^2$")
    fig.tight_layout()
    fig.savefig(output_dir / "encoder_consensus.png", dpi=250)
    fig.savefig(output_dir / "encoder_consensus.pdf")
    plt.close(fig)


def main():
    args = parse_args()
    if args.smoke:
        args.n_stim = min(args.n_stim, 180)
        args.n_subjects = min(args.n_subjects, 1)
        args.n_folds = 3
        args.target_pca_rank = min(args.target_pca_rank, 20)
        args.alphas = [1.0, 100.0]
        args.allow_missing_corrected = True
        args.output_dir = ROOT / "study1/results/brain_encoder_validation/smoke"
    args.output_dir.mkdir(parents=True, exist_ok=True)

    targets = load_targets(args.n_stim)
    encoders = {}
    for name, directory in ENCODER_DIRS.items():
        try:
            encoders[name] = load_encoder(directory, args.n_subjects, args.n_stim)
            print(f"Loaded {name}: {encoders[name].shape}")
        except FileNotFoundError as error:
            if name == "brain_jepa_native_pretrained" and not args.allow_missing_corrected:
                raise RuntimeError(
                    "Corrected Brain-JEPA embeddings are required. Run "
                    "extract_brain_jepa_frozen.sh first."
                ) from error
            print(f"Skipping unavailable encoder {name}: {error}")

    raw_bold = np.load(ROOT / "data/raw/raw_fmri/fmri_raw.npy", mmap_mode="r")[
        : args.n_subjects, : args.n_stim, :400
    ].astype(np.float64)
    encoders["raw_bold"] = raw_bold

    geometry_rows, fold_rows = [], []
    for encoder_name, values in encoders.items():
        for subject in range(values.shape[0]):
            for target_name, target in targets.items():
                geometry_rows.append(
                    {
                        "encoder": encoder_name,
                        "subject": subject + 1,
                        "target": target_name,
                        "linear_cka": linear_cka(values[subject], target),
                    }
                )
            fold_rows.extend(
                crossvalidated_scores(
                    values[subject], targets, args, encoder_name, subject + 1
                )
            )

    geometry_frame = pd.DataFrame(geometry_rows)
    fold_frame = pd.DataFrame(fold_rows)
    subject_frame, summary_frame = summarize_results(fold_frame)
    delta_frame = pretraining_deltas(subject_frame)
    geometry_frame.to_csv(args.output_dir / "direct_geometry_cka.csv", index=False)
    fold_frame.to_csv(args.output_dir / "fold_encoding_scores.csv", index=False)
    subject_frame.to_csv(args.output_dir / "subject_encoding_scores.csv", index=False)
    summary_frame.to_csv(args.output_dir / "encoder_summary.csv", index=False)
    delta_frame.to_csv(args.output_dir / "pretrained_vs_scratch.csv", index=False)
    save_figure(subject_frame, args.output_dir)

    config = {
        "n_stim": args.n_stim,
        "n_subjects": args.n_subjects,
        "n_folds": args.n_folds,
        "target_pca_rank": args.target_pca_rank,
        "alphas": args.alphas,
        "seed": args.seed,
        "encoders": {name: str(ENCODER_DIRS.get(name, "CCN raw BOLD")) for name in encoders},
        "guardrail": (
            "Direct CKA is descriptive. Cross-validated R2 and pretrained-minus-scratch "
            "replication across encoder families determine the main conclusion."
        ),
    }
    with open(args.output_dir / "run_config.json", "w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
    print(f"Finished: {args.output_dir}")


if __name__ == "__main__":
    main()
