"""Recipient-excluded plans and cache validation, retaining the full manifest."""
from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from project.code.pilot_contracts import artifact_key, validate_scopes


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class TeacherScope:
    fit: tuple[str, ...]
    evaluate: tuple[str, ...]
    forbidden: tuple[str, ...]


def oof_plan(rows, allowed_ids, forbidden_ids):
    rows = list(rows)
    index = {r.row_id: r for r in rows}
    allowed_ids, forbidden_ids = tuple(allowed_ids), tuple(forbidden_ids)
    if len(set(allowed_ids)) != len(allowed_ids) or any(i not in index for i in allowed_ids):
        raise ValueError("Invalid OOF allowed IDs")
    groups = sorted({index[i].run_group for i in allowed_ids})
    if len(groups) < 2:
        raise ValueError("OOF needs at least two independent allowed components")
    plan = []
    for group in groups:
        recipient = tuple(sorted(i for i in allowed_ids if index[i].run_group == group))
        fit = tuple(sorted(set(allowed_ids) - set(recipient)))
        validate_scopes(rows, fit, recipient, forbidden_ids)
        plan.append(TeacherScope(fit, recipient, tuple(sorted(forbidden_ids))))
    return plan


def nested_plan(rows, split):
    if set(split) != {"fit", "tune", "evaluate"}:
        raise ValueError("Explicit inner-training, inner-validation and outer-test required")
    validate_scopes(rows, split["fit"], split["tune"], split["evaluate"])
    return dict(inner=oof_plan(rows, split["fit"], split["tune"] + split["evaluate"]),
                final=oof_plan(rows, split["fit"] + split["tune"], split["evaluate"]))


def oof_cache_key(rows, scope, provenance):
    for field in ("teacher_checkpoint_hash", "transform_hash", "aggregate_input_digest"):
        if not provenance.get(field):
            raise ValueError(f"Missing OOF {field}")
    return artifact_key(rows, asdict(scope), provenance)


def require_cache(stored_key, expected_key):
    if not stored_key or stored_key != expected_key:
        raise ValueError("OOF cache provenance mismatch; regenerate affected artifacts")


def validate_bridge(rows, discovery_ids, calibration_ids, test_ids):
    """2d boundary interface only; shared test content is forbidden in discovery.

    Discovery and calibration may share training stimuli across cohorts. They
    are checked against test separately, not falsely required to be disjoint.
    """
    validate_scopes(rows, discovery_ids, test_ids)
    validate_scopes(rows, calibration_ids, test_ids)
    return {"discovery": list(discovery_ids), "calibration": list(calibration_ids),
            "test": list(test_ids), "predictor_input": "content only; no test brain/affect"}
