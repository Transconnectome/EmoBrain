"""Masked, training-only dual ridge benchmark for T005 (not CAT-34 BCE).

Reuse the adapter's StudentBatch by structural interface. Invalid brain entries
are imputed with the fitted training mean and therefore become zero after
scaling; all-unobserved/constant training columns are excluded and recorded.
No ROI averaging, clipping, global PCA, or evaluation-dependent selection.
"""
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from project.code.pilot_contracts import validate_scopes


TARGET_DIMS = {"cat34": 34, "affect14": 14}


def checked_arrays(batch, target):
    if target not in TARGET_DIMS:
        raise ValueError("Only verified cat34/affect14 interfaces are implemented")
    ids = tuple(batch.observation_ids)
    if not ids or len(set(ids)) != len(ids) or len(batch.content_ids) != len(ids):
        raise ValueError("Empty, duplicate or misaligned batch IDs")
    x, mask = np.asarray(batch.brain), np.asarray(batch.brain_valid)
    if x.ndim != 2 or x.shape[0] != len(ids) or mask.shape != x.shape or mask.dtype != bool:
        raise ValueError("brain and boolean brain_valid must have shape (rows, voxels)")
    if not np.isfinite(x[mask]).all() or np.any(~mask.any(axis=1)):
        raise ValueError("Nonfinite valid brain values or all-masked observation")
    y = np.asarray(batch.targets[target])
    ym = np.asarray(batch.target_masks[target])
    if y.shape != (len(ids), TARGET_DIMS[target]) or ym.shape != y.shape or ym.dtype != bool:
        raise ValueError("Target dimension or boolean target mask mismatch")
    if not np.isfinite(y[ym]).all():
        raise ValueError("Nonfinite valid targets")
    if target == "cat34" and np.any((y[ym] < 0) | (y[ym] > 1)):
        raise ValueError("CAT-34 must contain unnormalized proportions in [0, 1]")
    return x, mask, y, ym


def row_indices(batch, ids):
    lookup = {key: i for i, key in enumerate(batch.observation_ids)}
    ids = tuple(ids)
    if len(set(ids)) != len(ids) or not ids:
        raise ValueError("Empty or duplicate requested IDs")
    try:
        return np.array([lookup[key] for key in ids], dtype=int)
    except KeyError as exc:
        raise ValueError(f"Missing batch observation {exc.args[0]}") from exc


@dataclass
class MaskedScaler:
    mean: np.ndarray
    scale: np.ndarray
    keep: np.ndarray

    @classmethod
    def fit(cls, x, mask):
        count = mask.sum(axis=0)
        mean = np.where(mask, x, 0).sum(axis=0, dtype=np.float64) / np.maximum(count, 1)
        centered = np.where(mask, x - mean, 0)
        var = np.square(centered).sum(axis=0) / np.maximum(count, 1)
        keep = (count > 0) & (var > 1e-12)
        if not keep.any():
            raise ValueError("No variable observed training features")
        return cls(mean, np.where(var > 1e-12, np.sqrt(var), 1), keep)

    def transform(self, x, mask):
        if x.shape != mask.shape or x.shape[1] != len(self.mean):
            raise ValueError("Feature/mask shape differs from fitted voxel mapping")
        z = (x[:, self.keep] - self.mean[self.keep]) / self.scale[self.keep]
        return np.where(mask[:, self.keep], z, 0)


@dataclass
class LinearBenchmark:
    scaler: MaskedScaler
    weights: np.ndarray
    target_mean: np.ndarray
    target_scale: np.ndarray
    alpha: float

    @classmethod
    def fit(cls, x, mask, y, ym, alpha):
        if not np.isfinite(alpha) or alpha <= 0:
            raise ValueError("Ridge alpha must be finite and positive")
        if np.any(ym.sum(axis=0) == 0):
            raise ValueError("A target dimension has no training labels")
        scaler = MaskedScaler.fit(x, mask)
        z = scaler.transform(x, mask)
        count = ym.sum(axis=0)
        mean = np.where(ym, y, 0).sum(axis=0, dtype=np.float64) / count
        var = np.where(ym, (y - mean) ** 2, 0).sum(axis=0) / count
        scale = np.where(var > 1e-12, np.sqrt(var), 1)
        weights = np.empty((z.shape[1], y.shape[1]))
        # Solve all targets with the same missingness pattern together. Do not
        # build the large voxel dot product once per affect dimension.
        patterns = {}
        for j in range(y.shape[1]):
            patterns.setdefault(ym[:, j].tobytes(), []).append(j)
        for columns in patterns.values():
            use = ym[:, columns[0]]
            a = z[use]
            yz = (y[use][:, columns] - mean[columns]) / scale[columns]
            dual = np.linalg.solve(a @ a.T + alpha * np.eye(len(a)), yz)
            weights[:, columns] = a.T @ dual
        return cls(scaler, weights, mean, scale, float(alpha))

    def predict(self, brain, brain_valid):
        return self.scaler.transform(brain, brain_valid) @ self.weights * self.target_scale + self.target_mean

    def save(self, path):
        with Path(path).open("xb") as fh:
            np.savez(fh, mean=self.scaler.mean, scale=self.scaler.scale,
                     keep=self.scaler.keep, weights=self.weights,
                     target_mean=self.target_mean, target_scale=self.target_scale,
                     alpha=self.alpha)

    @classmethod
    def load(cls, path):
        with np.load(path, allow_pickle=False) as a:
            return cls(MaskedScaler(a["mean"], a["scale"], a["keep"]), a["weights"],
                       a["target_mean"], a["target_scale"], float(a["alpha"]))


def masked_mse(pred, y, mask):
    if pred.shape != y.shape or mask.shape != y.shape or mask.dtype != bool or not mask.any():
        raise ValueError("MSE requires matching predictions and nonempty boolean mask")
    if not np.isfinite(pred[mask]).all() or not np.isfinite(y[mask]).all():
        raise ValueError("Nonfinite evaluated entries")
    return float(np.square(pred[mask] - y[mask]).mean())


def validate_split(rows, batch, split):
    if set(split) != {"fit", "tune", "evaluate"}:
        raise ValueError("Explicit fit/tune/evaluate scopes required")
    # FULL manifest is intentionally retained, including unselected test repeats.
    validate_scopes(rows, split["fit"], split["tune"], split["evaluate"])
    validate_scopes(rows, split["fit"] + split["tune"], split["evaluate"])
    lookup = {r.row_id: r for r in rows}
    selected = sum((list(split[k]) for k in ("fit", "tune", "evaluate")), [])
    row_indices(batch, selected)
    for ident, content in zip(batch.observation_ids, batch.content_ids):
        if ident not in lookup or lookup[ident].content_id != content:
            raise ValueError("Batch content identity disagrees with full manifest")
        if lookup[ident].preprocessing_id != batch.preprocessing_id:
            raise ValueError("Batch preprocessing differs from observation manifest")


def run_linear(rows, batch, split, target, alphas=(1.0, 10.0, 100.0)):
    """Tune within A=fit+tune, refit on A, then score E exactly once."""
    rows = list(rows)
    validate_split(rows, batch, split)
    x, xm, y, ym = checked_arrays(batch, target)
    fi, ti, ei = (row_indices(batch, split[k]) for k in ("fit", "tune", "evaluate"))
    if not alphas or len(set(alphas)) != len(alphas):
        raise ValueError("Supply a nonempty unique declared alpha grid")
    scores = []
    for alpha in alphas:
        model = LinearBenchmark.fit(x[fi], xm[fi], y[fi], ym[fi], alpha)
        scores.append(masked_mse(model.predict(x[ti], xm[ti]), y[ti], ym[ti]))
    alpha = alphas[int(np.argmin(scores))]
    ai = np.concatenate([fi, ti])
    model = LinearBenchmark.fit(x[ai], xm[ai], y[ai], ym[ai], alpha)
    pred = model.predict(x[ei], xm[ei])
    mean_pred = np.broadcast_to(model.target_mean, pred.shape).copy()
    return dict(model=model, predictions=pred, mean_predictions=mean_pred,
                observation_ids=tuple(split["evaluate"]), targets=y[ei], target_mask=ym[ei],
                selected_alpha=float(alpha), tuning_mse=scores,
                mse=masked_mse(pred, y[ei], ym[ei]),
                training_mean_mse=masked_mse(mean_pred, y[ei], ym[ei]),
                fit_ids=list(split["fit"]) + list(split["tune"]),
                objective="linear MSE benchmark; predictions in original units; no clipping")
