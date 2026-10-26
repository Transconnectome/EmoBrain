"""Small synthetic-tested evaluation interfaces; no scientific defaults frozen."""
import numpy as np

from project.code.pilot_contracts import validate_scopes
from .baseline import LinearBenchmark


def fit_content_probe(rows, observation_ids, stage, references, fit_ids, evaluate_ids,
                      forbidden_ids=(), alpha=10.):
    """One frozen-stage linear probe; references have explicit row identity."""
    validate_scopes(rows, fit_ids, evaluate_ids, forbidden_ids)
    if len(set(observation_ids)) != len(observation_ids) or len(stage) != len(observation_ids) or len(references) != len(stage):
        raise ValueError("Probe identity/shape mismatch")
    if not np.isfinite(stage).all() or not np.isfinite(references).all():
        raise ValueError("Probe features must be finite")
    lookup = {ident: i for i, ident in enumerate(observation_ids)}
    fi, ei = ([lookup[i] for i in scope] for scope in (fit_ids, evaluate_ids))
    model = LinearBenchmark.fit(stage[fi], np.ones_like(stage[fi], dtype=bool),
                                references[fi], np.ones_like(references[fi], dtype=bool), alpha)
    return model, model.predict(stage[ei], np.ones_like(stage[ei], dtype=bool))


def commonality_scores(brain, valid, training_mean, predictions):
    """Analysis 1b with identical rows/masks and a common training-intercept SSE."""
    if set(predictions) != {"G", "GC", "GE", "GCE"}:
        raise ValueError("Supply G, GC, GE and GCE predictions on identical observations")
    if valid.shape != brain.shape or valid.dtype != bool or not valid.any():
        raise ValueError("Nonempty common brain mask required")
    reference = np.broadcast_to(training_mean, brain.shape)
    if not np.isfinite(brain[valid]).all() or not np.isfinite(reference[valid]).all():
        raise ValueError("Nonfinite common reference")
    denominator = float(np.square(brain[valid] - reference[valid]).sum())
    if denominator <= 1e-12:
        raise ValueError("Degenerate training-intercept denominator")
    sse = {}
    for name, pred in predictions.items():
        if pred.shape != brain.shape or not np.isfinite(pred[valid]).all():
            raise ValueError("Predictions must share finite evaluated entries and brain shape")
        sse[name] = float(np.square(brain[valid] - pred[valid]).sum())
    q = {name: 1 - v / denominator for name, v in sse.items()}
    return dict(denominator=denominator, sse=sse, q=q,
                content_increment=q["GC"] - q["G"], affect_increment=q["GE"] - q["G"],
                joint_increment=q["GCE"] - q["G"],
                content_given_affect=q["GCE"] - q["GE"],
                affect_given_content=q["GCE"] - q["GC"],
                shared_predictive_component=q["GC"] + q["GE"] - q["GCE"] - q["G"])


def retrieval(predicted, references, content_ids, top_k=1):
    """Cosine retrieval; collapse repeated canonical candidates and queries.

    Repeated fixed content references must agree; query predictions are averaged
    per content. Ties receive their worst rank, so tied vectors cannot yield an
    optimistic top-k merely through row order.
    """
    if predicted.shape != references.shape or len(content_ids) != len(predicted):
        raise ValueError("Retrieval rows/dimensions are misaligned")
    if not np.isfinite(predicted).all() or not np.isfinite(references).all():
        raise ValueError("Nonfinite retrieval features")
    ids = sorted(set(content_ids))
    if len(ids) < 2 or not 1 <= top_k <= len(ids):
        raise ValueError("At least two canonical candidates and valid top-k required")
    p, r = [], []
    for ident in ids:
        use = np.array([c == ident for c in content_ids])
        ref = references[use]
        if not np.allclose(ref, ref[0], rtol=1e-5, atol=1e-7):
            raise ValueError("Conflicting references within canonical content")
        r.append(ref[0])
        p.append(predicted[use].mean(axis=0))
    p, r = np.array(p), np.array(r)
    pn, rn = np.linalg.norm(p, axis=1), np.linalg.norm(r, axis=1)
    if np.any(pn == 0) or np.any(rn == 0):
        raise ValueError("Zero-vector cosine reference/query")
    similarities = (p / pn[:, None]) @ (r / rn[:, None]).T
    ranks = (similarities >= np.diag(similarities)[:, None] - 1e-12).sum(axis=1)
    return dict(candidate_count=len(ids), top_k=top_k, chance=top_k / len(ids),
                accuracy=float((ranks <= top_k).mean()), median_rank=float(np.median(ranks)),
                ranks=ranks.tolist(), content_ids=ids)


def linear_cka(x, y, x_ids, y_ids, reference_fit_id):
    if tuple(x_ids) != tuple(y_ids) or not reference_fit_id or len(x) != len(x_ids):
        raise ValueError("CKA requires aligned observations and one reference fit")
    if len(x) < 3 or len(y) != len(x) or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Invalid CKA inputs")
    x, y = x - x.mean(axis=0), y - y.mean(axis=0)
    den = np.linalg.norm(x.T @ x) * np.linalg.norm(y.T @ y)
    if den <= 1e-12:
        raise ValueError("Degenerate CKA")
    return float(np.square(x.T @ y).sum() / den)


def perturb_tokens(brain, valid, selected, null):
    """Zero only valid selected tokens; keep the original missingness mask."""
    selected, null = tuple(selected), tuple(null)
    if brain.ndim != 3 or valid.shape != brain.shape or valid.dtype != bool:
        raise ValueError("Expected (observation, ROI, feature) and boolean validity")
    if not selected or len(set(selected)) != len(selected) or len(set(null)) != len(null):
        raise ValueError("Nonempty unique token sets required")
    if len(selected) != len(null) or set(selected) & set(null):
        raise ValueError("Matched disjoint token sets required")
    if min(selected + null) < 0 or max(selected + null) >= brain.shape[1]:
        raise ValueError("Token index out of bounds")
    if not np.array_equal(valid[:, selected].sum(axis=(1, 2)), valid[:, null].sum(axis=(1, 2))):
        raise ValueError("Null must match valid feature count per observation")
    out = {}
    for name, tokens in (("selected", selected), ("null", null)):
        changed = brain.copy()
        changed[:, tokens] = np.where(valid[:, tokens], 0, changed[:, tokens])
        delta = np.where(valid, changed - brain, 0)
        out[name] = dict(brain=changed, magnitude=np.linalg.norm(delta.reshape(len(brain), -1), axis=1),
                         missing_entries=int((~valid[:, tokens]).sum()))
    return out
