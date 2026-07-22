#!/usr/bin/env python3
"""Compare native 160-TR Brain-JEPA embeddings with aggregated 16-TR embeddings."""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold, ShuffleSplit
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.brain_jepa_adapter import create_encoder
from lib.metrics import linear_cka, neighbor_overlap, rsa_spearman


N_ROIS = 450
NATIVE_LENGTH = 160
SHORT_LENGTH = 16
N_WINDOWS = NATIVE_LENGTH // SHORT_LENGTH


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--key", default="timeseries", help="NPZ key; ignored for NPY")
    parser.add_argument("--normalization-params", type=Path, default=None)
    parser.add_argument("--crop", choices=["first", "center"], default="center")
    parser.add_argument("--max-samples", type=int, default=1000)
    parser.add_argument("--batch-size-short", type=int, default=32)
    parser.add_argument("--batch-size-full", type=int, default=1)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--target-rank", type=int, default=100)
    parser.add_argument("--alphas", type=float, nargs="+", default=[0.1, 1.0, 10.0, 100.0])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--save-embeddings", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    return parser.parse_args()


def load_timeseries(args):
    if args.input.suffix == ".npy":
        values = np.load(args.input, mmap_mode="r")
    elif args.input.suffix == ".npz":
        payload = np.load(args.input)
        if args.key not in payload:
            raise KeyError(f"{args.key!r} not found; available keys: {payload.files}")
        values = payload[args.key]
    else:
        raise ValueError("Input must be .npy or .npz")
    if values.ndim != 3:
        raise ValueError(f"Expected a 3D array, received {values.shape}")
    if values.shape[1] == N_ROIS:
        values = values
    elif values.shape[2] == N_ROIS:
        values = np.swapaxes(values, 1, 2)
    else:
        raise ValueError(f"Expected one axis with {N_ROIS} ROIs, received {values.shape}")
    if values.shape[2] < NATIVE_LENGTH:
        raise ValueError(f"At least {NATIVE_LENGTH} timepoints are required")
    n_samples = min(len(values), args.max_samples)
    if args.smoke:
        n_samples = min(n_samples, 4)
    values = np.asarray(values[:n_samples], dtype=np.float32)
    if args.crop == "center":
        start = (values.shape[2] - NATIVE_LENGTH) // 2
    else:
        start = 0
    values = values[:, :, start : start + NATIVE_LENGTH]
    if args.normalization_params is not None:
        params = np.load(args.normalization_params)
        medians = np.asarray(params["medians"], dtype=np.float32)
        iqrs = np.asarray(params["iqrs"], dtype=np.float32)
        if medians.shape != (N_ROIS,) or iqrs.shape != (N_ROIS,):
            raise ValueError("Normalization parameters must contain 450-element medians and iqrs")
        values = (values - medians[None, :, None]) / (iqrs[None, :, None] + 1e-8)
    if not np.isfinite(values).all():
        raise ValueError("Input contains NaN or Inf")
    return values


def embed_array(model, values, batch_size, device):
    outputs = []
    for start in range(0, len(values), batch_size):
        batch = torch.from_numpy(values[start : start + batch_size]).unsqueeze(1)
        batch = batch.to(device)
        with torch.no_grad():
            output = model(batch)
            if isinstance(output, tuple):
                output = output[0]
        outputs.append(output.detach().cpu().numpy().astype(np.float32))
        print(f"embedded {min(start + batch_size, len(values))}/{len(values)}")
    result = np.concatenate(outputs)
    if not np.isfinite(result).all():
        raise ValueError("Embedding contains NaN or Inf")
    return result


def select_alpha(features, target, alphas, rank, seed):
    train, valid = next(ShuffleSplit(n_splits=1, test_size=0.2, random_state=seed).split(features))
    x_scaler = StandardScaler().fit(features[train])
    x_train, x_valid = x_scaler.transform(features[train]), x_scaler.transform(features[valid])
    y_scaler = StandardScaler().fit(target[train])
    y_train_z, y_valid_z = y_scaler.transform(target[train]), y_scaler.transform(target[valid])
    n_components = min(rank, len(train) - 1, y_train_z.shape[1])
    pca = PCA(n_components=n_components, svd_solver="randomized", random_state=seed)
    y_train, y_valid = pca.fit_transform(y_train_z), pca.transform(y_valid_z)
    scores = []
    for alpha in alphas:
        prediction = Ridge(alpha=alpha).fit(x_train, y_train).predict(x_valid)
        scores.append(float(np.mean(r2_score(y_valid, prediction, multioutput="raw_values"))))
    return float(alphas[int(np.argmax(scores))])


def crossvalidated_full_prediction(short, full, args):
    rows = []
    folds = KFold(n_splits=min(args.n_folds, len(short)), shuffle=True, random_state=args.seed)
    for fold, (train, test) in enumerate(folds.split(short), start=1):
        alpha = select_alpha(
            short[train], full[train], args.alphas, args.target_rank, args.seed + fold
        )
        x_scaler = StandardScaler().fit(short[train])
        x_train, x_test = x_scaler.transform(short[train]), x_scaler.transform(short[test])
        y_scaler = StandardScaler().fit(full[train])
        y_train_z, y_test_z = y_scaler.transform(full[train]), y_scaler.transform(full[test])
        rank = min(args.target_rank, len(train) - 1, y_train_z.shape[1])
        pca = PCA(n_components=rank, svd_solver="randomized", random_state=args.seed + fold)
        y_train, y_test = pca.fit_transform(y_train_z), pca.transform(y_test_z)
        prediction = Ridge(alpha=alpha).fit(x_train, y_train).predict(x_test)
        scores = r2_score(y_test, prediction, multioutput="raw_values")
        rows.append(
            {
                "fold": fold,
                "alpha": alpha,
                "mean_r2": float(np.mean(scores)),
                "median_r2": float(np.median(scores)),
                "n_test": int(len(test)),
            }
        )
    return rows


def main():
    args = parse_args()
    if args.smoke:
        args.n_folds = 2
        args.target_rank = 2
        args.alphas = [1.0, 100.0]
    values = load_timeseries(args)
    windows = values.reshape(len(values), N_ROIS, N_WINDOWS, SHORT_LENGTH).transpose(0, 2, 1, 3)
    windows_flat = windows.reshape(len(values) * N_WINDOWS, N_ROIS, SHORT_LENGTH)
    device = torch.device(args.device)
    output_dir = ROOT / "outputs/native_length_validation"
    if args.smoke:
        output_dir = ROOT / "outputs/smoke/native_length_validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_rows, window_rows, fold_rows, audits = [], [], [], []
    for init in ["pretrained", "scratch"]:
        full_model, full_audit = create_encoder(init, 160, "checkpoint", device, seed=args.seed)
        full = embed_array(full_model, values, args.batch_size_full, device)
        del full_model
        if device.type == "cuda":
            torch.cuda.empty_cache()
        short_model, short_audit = create_encoder(init, 16, "native", device, seed=args.seed)
        short = embed_array(short_model, windows_flat, args.batch_size_short, device)
        short = short.reshape(len(values), N_WINDOWS, -1)
        short_mean = short.mean(axis=1)
        audits.append({"init": init, "full": full_audit, "short": short_audit})

        summary_rows.append(
            {
                "init": init,
                "n_samples": len(values),
                "linear_cka": linear_cka(full, short_mean),
                "rsa_spearman": rsa_spearman(full, short_mean),
                "neighbor_overlap_k10": neighbor_overlap(
                    full, short_mean, k=min(10, len(values) - 1)
                ),
            }
        )
        for window in range(N_WINDOWS):
            window_rows.append(
                {
                    "init": init,
                    "window": window,
                    "linear_cka": linear_cka(full, short[:, window]),
                    "rsa_spearman": rsa_spearman(full, short[:, window]),
                }
            )
        if len(values) >= 10:
            for row in crossvalidated_full_prediction(short_mean, full, args):
                fold_rows.append({"init": init, **row})
        if args.save_embeddings:
            np.savez_compressed(
                output_dir / f"native_short_embeddings_{init}.npz",
                full_160=full,
                short_16=short,
                short_mean=short_mean,
            )
        del short_model
        if device.type == "cuda":
            torch.cuda.empty_cache()

    pd.DataFrame(summary_rows).to_csv(output_dir / "native_short_geometry.csv", index=False)
    pd.DataFrame(window_rows).to_csv(output_dir / "windowwise_geometry.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(output_dir / "short_to_full_encoding.csv", index=False)
    config = {
        "input": str(args.input),
        "input_key": args.key,
        "normalization_params": None if args.normalization_params is None else str(args.normalization_params),
        "crop": args.crop,
        "n_samples": len(values),
        "audits": audits,
        "interpretation": (
            "High pretrained full-short geometry with a weaker scratch baseline supports "
            "short-window transfer. It does not imply recovery of all long-range dynamics."
        ),
    }
    with open(output_dir / "run_config.json", "w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2)
    print(f"Finished: {output_dir}")


if __name__ == "__main__":
    main()
