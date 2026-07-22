"""Import validated short-window Brain-JEPA embeddings into EmoBrain.

The validation output is immutable evidence. This importer creates the format
consumed by BFMSource and carries each subject's JSON audit into the saved file,
so the corrected native one-patch positional policy cannot be confused with the
legacy temporal-mean condition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = (
    REPO_ROOT
    / "external/Brain-JEPA_short_window_validation/outputs/horikawa_embeddings"
    / "init-pretrained_pos-native_input-mean"
)
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "project/shared/output/embeddings/brain_jepa_pretrained_native_mean"
)
SUBJECTS = tuple(f"sub-{i:02d}" for i in range(1, 6))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    manifest = {"variant": args.output.name, "subjects": {}}
    for subject in SUBJECTS:
        npz_path = args.source / f"{subject}.npz"
        json_path = args.source / f"{subject}.json"
        if not npz_path.exists() or not json_path.exists():
            raise FileNotFoundError(f"missing validated source for {subject}: {args.source}")

        provenance = json.loads(json_path.read_text())
        required = {
            "initialization": "pretrained",
            "position_policy": "native",
            "input_perturbation": "mean",
            "n_stimuli": 2185,
        }
        for key, expected in required.items():
            if provenance.get(key) != expected:
                raise ValueError(
                    f"{subject} provenance mismatch: {key}={provenance.get(key)!r}, "
                    f"expected {expected!r}"
                )

        with np.load(npz_path) as data:
            embeddings = torch.from_numpy(data["embeddings"].astype(np.float32))
            stim_num = torch.from_numpy(data["stim_num"].astype(np.int32))
            original_t = torch.from_numpy(data["original_T"].astype(np.int32))
            padding_ratio = torch.from_numpy(data["padding_ratio"].astype(np.float32))
        if embeddings.shape != (2185, 768):
            raise ValueError(f"{subject}: unexpected embedding shape {tuple(embeddings.shape)}")
        if sorted(stim_num.tolist()) != list(range(1, 2186)):
            raise ValueError(f"{subject}: stimulus IDs are not exactly 1..2185")

        output = args.output / f"{subject}.pt"
        torch.save(
            {
                "embeddings": embeddings,
                "stim_num": stim_num,
                "original_T": original_t,
                "padding_ratio": padding_ratio,
                "provenance": provenance,
                "source_npz": str(npz_path),
                "source_sha256": sha256(npz_path),
            },
            output,
        )
        manifest["subjects"][subject] = {
            "output": str(output),
            "source": str(npz_path),
            "source_sha256": sha256(npz_path),
            "shape": list(embeddings.shape),
        }
        print(f"[import] {subject}: {tuple(embeddings.shape)} -> {output}")

    manifest_path = args.output / "provenance.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"[done] {manifest_path}")


if __name__ == "__main__":
    main()
