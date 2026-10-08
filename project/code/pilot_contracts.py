"""Dependency-free pilot split guards; not a dataset adapter or training runner.

Run these against the FULL audited observation manifest, before selecting a pilot
subset. Connected run groups and canonical IDs must already have been audited.
The guards verify declared scopes, not whether a training routine obeyed them.
"""

from dataclasses import asdict, dataclass
from hashlib import sha256
from itertools import combinations
import json
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Observation:
    row_id: str
    content_id: str
    run_id: str  # Globally qualified: cohort/participant/session/run.
    run_group: str  # Audited connected component, not a raw run number.
    preprocessing_id: str  # Immutable version/checksum, not "latest".
    reserved: bool = False


def _index(rows: Iterable[Observation]) -> dict[str, Observation]:
    result = {}
    content_groups = {}
    run_groups = {}
    for row in rows:
        for name in ("row_id", "content_id", "run_id", "run_group", "preprocessing_id"):
            value = getattr(row, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Missing/non-string {name}")
        if type(row.reserved) is not bool:
            raise ValueError("reserved must be a boolean")
        if row.row_id in result:
            raise ValueError(f"Duplicate observation: {row.row_id}")
        result[row.row_id] = row
        for key, groups in ((row.content_id, content_groups), (row.run_id, run_groups)):
            if key in groups and groups[key] != row.run_group:
                raise ValueError(f"Inconsistent connected run group: {key}")
            groups[key] = row.run_group
    if not result:
        raise ValueError("Empty observation manifest")
    return result


def validate_scopes(
    rows: Iterable[Observation],
    fit_ids: Iterable[str],
    evaluate_ids: Iterable[str],
    forbidden_ids: Iterable[str] = (),
) -> dict[str, int]:
    """Reject observation, canonical-content and connected-run leakage.

    Pilot evaluation cannot access reserved content either. For an OOF fit,
    evaluate_ids are recipients; forbidden_ids include outer test AND current
    inner validation. fit_ids must cover ALL fit/selection dependencies, including
    scalers, PCA, warm-up and hyperparameter selection, not only gradient batches.
    Calling with a trimmed manifest could hide reserved repetitions: don't do so.
    """
    index = _index(rows)
    scopes = {
        "fit": set(fit_ids),
        "evaluate": set(evaluate_ids),
        "forbidden": set(forbidden_ids),
    }
    for name, ids in scopes.items():
        if name != "forbidden" and not ids:
            raise ValueError(f"Empty {name} scope")
        if ids - index.keys():
            raise ValueError(f"Unknown observation IDs in {name}")
    reserved_content = {r.content_id for r in index.values() if r.reserved}
    for name in ("fit", "evaluate"):
        if {index[i].content_id for i in scopes[name]} & reserved_content:
            raise ValueError(f"Reserved content in pilot {name} scope")
    for left, right in combinations(scopes, 2):
        for field in ("row_id", "content_id", "run_group"):
            a = {getattr(index[i], field) for i in scopes[left]}
            b = {getattr(index[i], field) for i in scopes[right]}
            if a & b:
                raise ValueError(f"{field} leakage between {left} and {right}")
    return {name: len(ids) for name, ids in scopes.items()}


def artifact_key(
    rows: Iterable[Observation],
    scopes: Mapping[str, Iterable[str]],
    provenance: Mapping[str, object],
) -> str:
    """Fingerprint declared metadata; this does not checksum input files itself.

    Supply actual checksums in provenance. Include fit/evaluate/forbidden roles;
    for OOF targets add teacher_checkpoint_hash and transform_hash explicitly.
    """
    index = _index(rows)
    required = {
        "code_commit", "input_manifest_hash", "split_hash", "target",
        "target_transform_hash", "feature_hash", "config_hash", "seed",
    }
    if required - provenance.keys():
        raise ValueError(f"Missing provenance: {sorted(required - provenance.keys())}")
    if any(provenance[k] is None or provenance[k] == "" for k in required):
        raise ValueError("Empty provenance field")
    if set(scopes) != {"fit", "evaluate", "forbidden"}:
        raise ValueError("Specify fit, evaluate and forbidden scopes")
    normalized = {name: sorted(set(ids)) for name, ids in scopes.items()}
    validate_scopes(index.values(), normalized["fit"], normalized["evaluate"],
                    normalized["forbidden"])
    payload = {
        "schema": "emobrain-pilot-contract-v1",
        "observations": [asdict(index[i]) for i in sorted(index)],
        "scopes": normalized,
        "provenance": dict(provenance),
    }
    return sha256(json.dumps(payload, sort_keys=True, allow_nan=False,
                             separators=(",", ":")).encode()).hexdigest()
