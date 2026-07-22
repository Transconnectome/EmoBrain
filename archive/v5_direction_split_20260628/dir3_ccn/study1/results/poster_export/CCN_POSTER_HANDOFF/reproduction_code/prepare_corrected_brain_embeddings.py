#!/usr/bin/env python3
"""Validate and stack corrected Brain-JEPA embeddings for the CCN reanalysis."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def find_project_root():
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "CLAUDE.md").is_file() and (candidate / "study1").is_dir():
            return candidate
    raise RuntimeError("Could not locate the CCN project root")


ROOT = find_project_root()
EMOBRAIN_ROOT = ROOT.parents[2]
DEFAULT_SOURCE = (
    EMOBRAIN_ROOT
    / "external/Brain-JEPA_short_window_validation/outputs/horikawa_embeddings"
    / "init-pretrained_pos-native_input-mean"
)
DEFAULT_OUTPUT = ROOT / "study1/data/corrected_reanalysis/brain_jepa_native_1patch.npy"
CANONICAL_CSV = EMOBRAIN_ROOT / "project/shared/data/feelin_canonical_stimuli.csv"
N_SUBJECTS = 5
N_STIMULI = 2185
EMBED_DIM = 768


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_subject(source_dir, subject, expected_ids):
    stem = source_dir / f"sub-{subject:02d}"
    npz_path = stem.with_suffix(".npz")
    json_path = stem.with_suffix(".json")
    if not npz_path.is_file() or not json_path.is_file():
        raise FileNotFoundError(f"Missing corrected output for sub-{subject:02d}: {stem}")

    with open(json_path, encoding="utf-8") as handle:
        metadata = json.load(handle)
    audit = metadata.get("audit", {})
    required_audit = {
        "applied_position_policy": "native",
        "model_time_patches": 1,
        "position_code_trainable": False,
    }
    for key, expected in required_audit.items():
        if audit.get(key) != expected:
            raise ValueError(
                f"sub-{subject:02d} audit mismatch for {key}: "
                f"expected {expected!r}, found {audit.get(key)!r}"
            )
    if audit.get("unexpected_keys"):
        raise ValueError(f"sub-{subject:02d} has unexpected checkpoint keys")

    with np.load(npz_path) as payload:
        embeddings = np.asarray(payload["embeddings"], dtype=np.float32)
        stimulus_ids = np.asarray(payload["stim_num"])
        original_time = np.asarray(payload["original_T"])
        padding_ratio = np.asarray(payload["padding_ratio"])

    if embeddings.shape != (N_STIMULI, EMBED_DIM):
        raise ValueError(f"Unexpected sub-{subject:02d} shape: {embeddings.shape}")
    if not np.array_equal(stimulus_ids, expected_ids):
        raise ValueError(f"sub-{subject:02d} stimulus IDs do not match canonical order")
    if len(np.unique(stimulus_ids)) != N_STIMULI:
        raise ValueError(f"sub-{subject:02d} contains duplicate stimulus IDs")
    if not np.isfinite(embeddings).all():
        raise ValueError(f"sub-{subject:02d} contains non-finite embeddings")
    if np.any(np.linalg.norm(embeddings, axis=1) == 0):
        raise ValueError(f"sub-{subject:02d} contains zero embedding rows")
    if original_time.shape != (N_STIMULI,) or padding_ratio.shape != (N_STIMULI,):
        raise ValueError(f"sub-{subject:02d} extraction metadata is incomplete")

    record = {
        "subject": f"sub-{subject:02d}",
        "npz_path": str(npz_path.resolve()),
        "npz_sha256": file_sha256(npz_path),
        "metadata_path": str(json_path.resolve()),
        "embedding_shape": list(embeddings.shape),
        "original_time_min": int(original_time.min()),
        "original_time_max": int(original_time.max()),
        "mean_padding_ratio": float(padding_ratio.mean()),
        "position_code_sha256": audit.get("position_code_sha256"),
    }
    return embeddings, record


def main():
    args = parse_args()
    canonical = pd.read_csv(CANONICAL_CSV)
    expected_ids = canonical["stimulus_num"].to_numpy()
    if len(expected_ids) != N_STIMULI or not np.array_equal(
        expected_ids, np.arange(1, N_STIMULI + 1)
    ):
        raise ValueError("Canonical stimulus contract has changed")

    arrays, records = [], []
    for subject in range(1, N_SUBJECTS + 1):
        embeddings, record = load_subject(args.source_dir, subject, expected_ids)
        arrays.append(embeddings)
        records.append(record)
        print(
            f"Validated {record['subject']}: {tuple(embeddings.shape)}, "
            f"padding={record['mean_padding_ratio']:.3f}"
        )

    stacked = np.stack(arrays)
    if stacked.shape != (N_SUBJECTS, N_STIMULI, EMBED_DIM):
        raise RuntimeError(f"Unexpected stacked shape: {stacked.shape}")
    manifest = {
        "description": "Corrected frozen Brain-JEPA, native one-time-patch sin/cos code",
        "source_directory": str(args.source_dir.resolve()),
        "canonical_csv": str(CANONICAL_CSV.resolve()),
        "output_shape": list(stacked.shape),
        "dtype": str(stacked.dtype),
        "subjects": records,
    }

    if args.check_only:
        print(json.dumps(manifest, indent=2))
        print("Check-only complete; no CCN input file was written.")
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output.with_suffix(".json")
    if (args.output.exists() or manifest_path.exists()) and not args.force:
        raise FileExistsError(
            f"Output already exists: {args.output}. Use --force only for an intentional refresh."
        )
    np.save(args.output, stacked)
    manifest["output_path"] = str(args.output.resolve())
    manifest["output_sha256"] = file_sha256(args.output)
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    print(f"Saved corrected CCN input: {args.output}")
    print(f"Saved provenance manifest: {manifest_path}")


if __name__ == "__main__":
    main()
