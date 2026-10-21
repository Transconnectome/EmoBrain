"""Immutable small pilot runs with actual source hashes and row-aligned output."""
from dataclasses import asdict
import csv
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

from project.code.pilot_contracts import artifact_key
from .scopes import fingerprint


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def code_record(repo):
    def git(*args):
        return subprocess.check_output(["git", "--no-optional-locks", "-C", str(repo), *args], text=True).strip()
    source = list((repo / "project/code/pilot").glob("*.py"))
    source += [repo / p for p in ("project/code/pilot_contracts.py", "project/data/pilot_adapter.py",
                                 "project/scripts/run_pilot.py")]
    return dict(commit=git("rev-parse", "HEAD"), branch=git("rev-parse", "--abbrev-ref", "HEAD"),
                dirty=git("status", "--porcelain", "--untracked-files=normal"),
                source_hashes={str(p.relative_to(repo)): file_hash(p) for p in source if p.exists()})


def save_linear_run(root, experiment_id, rows, batch, split, target, result, config, sources, code, seconds):
    if not experiment_id or Path(experiment_id).name != experiment_id or experiment_id in (".", ".."):
        raise ValueError("Experiment ID must be one path component")
    if not sources or any(not isinstance(v, str) or len(v) != 64 for v in sources.values()):
        raise ValueError("Actual SHA-256 input checksums required")
    model = result["model"]
    transform_hash = fingerprint(dict(x_mean=model.scaler.mean.tolist(), x_scale=model.scaler.scale.tolist(),
                                     keep=model.scaler.keep.tolist(), y_mean=model.target_mean.tolist(),
                                     y_scale=model.target_scale.tolist()))
    provenance = dict(code_commit=code["commit"], input_manifest_hash=fingerprint([asdict(r) for r in rows]),
                      split_hash=fingerprint(split), target=target, target_transform_hash=transform_hash,
                      feature_hash=fingerprint(sources), config_hash=fingerprint(config), seed=config["seed"],
                      code_source_hashes=code["source_hashes"], brain_variant=batch.brain_variant)
    key = artifact_key(rows, dict(fit=result["fit_ids"], evaluate=split["evaluate"], forbidden=[]), provenance)
    prep_hash = fingerprint(dict(preprocessing_id=batch.preprocessing_id, brain_variant=batch.brain_variant))
    out = Path(root) / prep_hash / experiment_id
    out.mkdir(parents=True, exist_ok=False)
    model.save(out / "linear_model.npz")
    (out / "metadata.json").write_text(json.dumps(dict(config=config, target=target, code=code,
        preprocessing_id=batch.preprocessing_id, brain_variant=batch.brain_variant,
        participant=batch.participant_id, sources=sources, scope_roles=split,
        provenance=provenance, artifact_key=key, seconds=seconds,
        objective=result["objective"], alpha=result["selected_alpha"], tuning_mse=result["tuning_mse"],
        mse=result["mse"], training_mean_mse=result["training_mean_mse"],
        fitted_voxel_indices=np.flatnonzero(model.scaler.keep).tolist(),
        valid_target_entries=int(result["target_mask"].sum()),
        coverage=dict(brain_valid_fraction=float(batch.brain_valid.mean()),
                      target_valid_fraction=float(batch.target_masks[target].mean())),
        interpretation="descriptive development benchmark; not final preprocessing or confirmatory evidence"), indent=2))
    contents = dict(zip(batch.observation_ids, batch.content_ids))
    with (out / "predictions.tsv").open("w") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["observation_id", "content_id", "participant_id", "target_dimension",
                         "valid", "target", "prediction", "training_mean_prediction"])
        for i, ident in enumerate(result["observation_ids"]):
            for j in range(result["predictions"].shape[1]):
                valid = bool(result["target_mask"][i, j])
                writer.writerow([ident, contents[ident], batch.participant_id, j, valid,
                                 float(result["targets"][i,j]) if valid else "",
                                 float(result["predictions"][i,j]), float(result["mean_predictions"][i,j])])
    return out
