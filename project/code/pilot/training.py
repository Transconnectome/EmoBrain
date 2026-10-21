"""Fixed-budget CPU teacher/student smoke path with explicit nested scopes.

No warm-up, early stopping or teacher hyperparameter search is performed. The
declared configuration is fixed before recipient predictions. Only student
guidance weight is selected on inner validation, then OOF is regenerated in A.
Real-data connection requires separately audited ROI features/content inputs.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

import numpy as np
import torch

from project.code.pilot_contracts import validate_scopes
from .baseline import MaskedScaler, TARGET_DIMS, masked_mse
from .models import BrainStudent, JointTeacher, ModelConfig, student_objective, supervised
from .scopes import fingerprint, nested_plan, oof_cache_key


@dataclass
class TensorData:
    observation_ids: tuple
    content_ids: tuple
    brain: np.ndarray
    brain_valid: np.ndarray
    participants: np.ndarray
    targets: np.ndarray
    target_valid: np.ndarray
    video: np.ndarray
    caption: np.ndarray
    content_valid: np.ndarray


@dataclass(frozen=True)
class FitConfig:
    seed: int = 0
    steps: int = 3
    learning_rate: float = .001

    def __post_init__(self):
        if not 1 <= self.steps <= 100 or not 0 < self.learning_rate < 1:
            raise ValueError("Bounded smoke configuration required")


@dataclass
class TargetScale:
    mean: np.ndarray
    scale: np.ndarray

    @classmethod
    def fit(cls, y, valid, target):
        if valid.dtype != bool or y.shape != valid.shape or not np.isfinite(y[valid]).all():
            raise ValueError("Invalid target mask or finite values")
        count = valid.sum(axis=0)
        if np.any(count == 0):
            raise ValueError("Unobserved training target dimension")
        if target == "cat34":
            if np.any((y[valid] < 0) | (y[valid] > 1)):
                raise ValueError("Invalid CAT-34 proportion")
            return cls(np.zeros(y.shape[1]), np.ones(y.shape[1]))
        mean = np.where(valid, y, 0).sum(0) / count
        sd = np.sqrt(np.where(valid, (y - mean) ** 2, 0).sum(0) / count)
        return cls(mean, np.where(sd > 1e-6, sd, 1))

    def transform(self, y):
        return (y - self.mean) / self.scale

    def inverse(self, y):
        return y * self.scale + self.mean


def state_hash(model):
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        digest.update(name.encode())
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def indices(data, ids):
    lookup = {key: i for i, key in enumerate(data.observation_ids)}
    if len(lookup) != len(data.observation_ids):
        raise ValueError("Duplicate tensor observation IDs")
    try:
        return np.array([lookup[key] for key in ids], dtype=int)
    except KeyError as exc:
        raise ValueError("Tensor data missing scope row") from exc


def validate_data(rows, data, cfg):
    n = len(data.observation_ids)
    if data.brain.shape != (n, cfg.rois, cfg.brain_features) or data.brain_valid.shape != data.brain.shape:
        raise ValueError("Brain tensor dimensions do not match config")
    if data.brain_valid.dtype != bool or not np.isfinite(data.brain[data.brain_valid]).all():
        raise ValueError("Invalid brain mask/values")
    if data.targets.shape != (n, TARGET_DIMS[cfg.target]) or data.target_valid.shape != data.targets.shape or data.target_valid.dtype != bool:
        raise ValueError("Target tensor dimensions/mask do not match config")
    if data.video.shape != (n, cfg.video_dim) or data.caption.shape != (n, cfg.caption_dim) or data.content_valid.shape != (n, 2) or data.content_valid.dtype != bool:
        raise ValueError("Content tensor dimensions/mask mismatch")
    lookup = {r.row_id: r for r in rows}
    if len(data.content_ids) != n or len(set(data.observation_ids)) != n:
        raise ValueError("Tensor ID mismatch")
    for ident, content in zip(data.observation_ids, data.content_ids):
        if ident not in lookup or lookup[ident].content_id != content:
            raise ValueError("Tensor content differs from full manifest")
    selected = [lookup[i] for i in data.observation_ids]
    if len({r.preprocessing_id for r in selected}) != 1:
        raise ValueError("Smoke path requires one preprocessing version")
    if data.participants.shape != (n,) or not np.issubdtype(data.participants.dtype, np.integer):
        raise ValueError("Integer participant indices required")


def paired_content_permutation(data, fit_indices, seed):
    """One shared V/S permutation at canonical-content level within fit scope."""
    ids = [data.content_ids[i] for i in fit_indices]
    groups = sorted(set(ids))
    if len(groups) < 2:
        raise ValueError("Shuffled teacher needs multiple fit contents")
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(groups))
    # A seeded cycle guarantees wrong pairing for each canonical content.
    mapping = {groups[order[j]]: groups[order[(j + 1) % len(groups)]] for j in range(len(groups))}
    representatives = {}
    for i in fit_indices:
        key = data.content_ids[i]
        if key in representatives:
            ref = representatives[key]
            if not np.array_equal(data.content_valid[i], data.content_valid[ref]):
                raise ValueError("Repeated content validity differs")
            for j, array in enumerate((data.video, data.caption)):
                if data.content_valid[i, j] and not np.allclose(array[i], array[ref]):
                    raise ValueError("Repeated content features differ")
        representatives.setdefault(key, i)
    return np.array([representatives[mapping[key]] for key in ids])


@dataclass
class FitResult:
    model: object
    brain_scaler: MaskedScaler
    target_scaler: TargetScale
    fit_ids: tuple
    history: list
    transform_hash: str


def _brain_tensor(data, use, scaler):
    shape = data.brain[use].shape
    x, valid = data.brain[use].reshape(len(use), -1), data.brain_valid[use].reshape(len(use), -1)
    # Preserve anatomical feature positions; omitted training columns stay masked.
    out = np.zeros(x.shape, dtype=np.float32)
    out[:, scaler.keep] = scaler.transform(x, valid)
    valid = valid & scaler.keep[None]
    return torch.tensor(out.reshape(shape)), torch.tensor(valid.reshape(shape))


def fit_model(rows, data, cfg, fit_cfg, fit_ids, evaluate_ids, forbidden_ids,
              teacher=False, guidance=None, weight=0., shuffled=False):
    validate_scopes(rows, fit_ids, evaluate_ids, forbidden_ids)
    validate_data(rows, data, cfg)
    use = indices(data, fit_ids)
    if set(data.participants[indices(data, evaluate_ids)]) - set(data.participants[use]):
        raise ValueError("Evaluation requests an untrained participant map")
    x = data.brain[use].reshape(len(use), -1)
    valid = data.brain_valid[use].reshape(len(use), -1)
    scaler = MaskedScaler.fit(x, valid)
    ts = TargetScale.fit(data.targets[use], data.target_valid[use], cfg.target)
    transform_hash = fingerprint(dict(mean=scaler.mean.tolist(), scale=scaler.scale.tolist(),
                                      keep=scaler.keep.tolist(), y_mean=ts.mean.tolist(), y_scale=ts.scale.tolist()))
    torch.manual_seed(fit_cfg.seed)
    model = JointTeacher(cfg) if teacher else BrainStudent(cfg)
    optimizer = torch.optim.AdamW(model.parameters(), lr=fit_cfg.learning_rate)
    b, bm = _brain_tensor(data, use, scaler)
    participants = torch.tensor(data.participants[use], dtype=torch.long)
    y, ym = torch.tensor(ts.transform(data.targets[use]), dtype=torch.float32), torch.tensor(data.target_valid[use])
    if guidance is not None:
        # OOF arrays are stored in ORIGINAL target units, never fold z-scores.
        if set(guidance) != set(fit_ids):
            raise ValueError("Guidance must cover exactly the student fit recipients")
        g = torch.tensor(ts.transform(np.stack([guidance[i] for i in fit_ids])), dtype=torch.float32)
    else:
        g = None
    content_use = paired_content_permutation(data, use, fit_cfg.seed) if shuffled else use
    history = []
    for _ in range(fit_cfg.steps):
        optimizer.zero_grad(set_to_none=True)
        if teacher:
            logits = model(b, bm, participants,
                           torch.tensor(data.video[content_use], dtype=torch.float32),
                           torch.tensor(data.caption[content_use], dtype=torch.float32),
                           torch.tensor(data.content_valid[content_use]))["logits"]
            label = supervised(logits, y, ym, cfg.target)
            terms = dict(total=label, label=label, distillation=label * 0)
        else:
            logits = model(b, bm, participants)["logits"]
            terms = student_objective(logits, y, ym, cfg.target, g,
                                      torch.ones_like(g, dtype=torch.bool) if g is not None else None, weight)
        if not torch.isfinite(terms["total"]):
            raise ValueError("Nonfinite training objective")
        terms["total"].backward()
        optimizer.step()
        history.append({k: float(v.detach()) for k, v in terms.items()})
    return FitResult(model, scaler, ts, tuple(fit_ids), history, transform_hash)


def predict(fit, data, ids):
    use = indices(data, ids)
    brain, valid = _brain_tensor(data, use, fit.brain_scaler)
    participant = torch.tensor(data.participants[use], dtype=torch.long)
    fit.model.eval()
    with torch.no_grad():
        if isinstance(fit.model, JointTeacher):
            out = fit.model(brain, valid, participant, torch.tensor(data.video[use], dtype=torch.float32),
                            torch.tensor(data.caption[use], dtype=torch.float32), torch.tensor(data.content_valid[use]))
        else:
            out = fit.model(brain, valid, participant)
        values = out["logits"].sigmoid() if fit.model.cfg.target == "cat34" else out["logits"]
    return fit.target_scaler.inverse(values.numpy()), out


def save_fit(fit, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "config.json").write_text(json.dumps(dict(model=asdict(fit.model.cfg),
        teacher=isinstance(fit.model, JointTeacher), fit_ids=fit.fit_ids,
        history=fit.history, transform_hash=fit.transform_hash), indent=2))
    torch.save(fit.model.state_dict(), directory / "state.pt")
    np.savez(directory / "transforms.npz", mean=fit.brain_scaler.mean,
             scale=fit.brain_scaler.scale, keep=fit.brain_scaler.keep,
             target_mean=fit.target_scaler.mean, target_scale=fit.target_scaler.scale)


def load_fit(directory):
    directory = Path(directory)
    cfg = json.loads((directory / "config.json").read_text())
    model = (JointTeacher if cfg["teacher"] else BrainStudent)(ModelConfig(**cfg["model"]))
    model.load_state_dict(torch.load(directory / "state.pt", map_location="cpu", weights_only=True))
    with np.load(directory / "transforms.npz", allow_pickle=False) as a:
        scaler = MaskedScaler(a["mean"], a["scale"], a["keep"])
        ts = TargetScale(a["target_mean"], a["target_scale"])
    return FitResult(model, scaler, ts, tuple(cfg["fit_ids"]), cfg["history"], cfg["transform_hash"])


def generate_oof(rows, data, cfg, fit_cfg, plan, provenance, shuffled=False):
    if not provenance.get("aggregate_input_digest"):
        raise ValueError("Missing OOF aggregate_input_digest; verify inputs before fitting")
    guidance, ledger = {}, []
    for scope in plan:
        fit = fit_model(rows, data, cfg, fit_cfg, scope.fit, scope.evaluate, scope.forbidden,
                        teacher=True, shuffled=shuffled)
        prediction, _ = predict(fit, data, scope.evaluate)
        prov = dict(provenance, target=cfg.target, target_transform_hash=fit.transform_hash,
                    teacher_checkpoint_hash=state_hash(fit.model), transform_hash=fit.transform_hash,
                    config_hash=fingerprint(dict(model=asdict(cfg), fit=asdict(fit_cfg), shuffled=shuffled)))
        key = oof_cache_key(rows, scope, prov)
        for ident, value in zip(scope.evaluate, prediction):
            if ident in guidance:
                raise ValueError("Repeated OOF recipient")
            guidance[ident] = value
        ledger.append(dict(scope=asdict(scope), key=key, provenance=prov, fit=fit,
                           dependency_ids={name: list(scope.fit) for name in
                                           ("brain_scaler", "target_scaler", "gradient_fit")},
                           selection="fixed declared teacher settings; no warm-up/early stopping/tuning"))
    return guidance, ledger


def run_nested(rows, data, cfg, fit_cfg, split, provenance, weights=(0.5,), shuffled=False):
    """One pilot inner split and final refit; all teachers exclude recipients."""
    if not weights or any(not np.isfinite(w) or w <= 0 for w in weights):
        raise ValueError("Positive declared student guidance weights required")
    plan = nested_plan(rows, split)
    inner_g, inner_ledger = generate_oof(rows, data, cfg, fit_cfg, plan["inner"], provenance, shuffled)
    val = indices(data, split["tune"])
    scores = []
    for weight in weights:
        fit = fit_model(rows, data, cfg, fit_cfg, split["fit"], split["tune"], split["evaluate"],
                        guidance=inner_g, weight=weight)
        pred, _ = predict(fit, data, split["tune"])
        scores.append(masked_mse(pred, data.targets[val], data.target_valid[val]))
    selected = float(weights[int(np.argmin(scores))])
    final_g, final_ledger = generate_oof(rows, data, cfg, fit_cfg, plan["final"], provenance, shuffled)
    a = split["fit"] + split["tune"]
    guided = fit_model(rows, data, cfg, fit_cfg, a, split["evaluate"], [], guidance=final_g, weight=selected)
    direct = fit_model(rows, data, cfg, fit_cfg, a, split["evaluate"], [])
    guided_prediction, stages = predict(guided, data, split["evaluate"])
    direct_prediction, _ = predict(direct, data, split["evaluate"])
    return dict(guided=guided, direct=direct, selected_weight=selected, tuning_mse=scores,
                predictions=guided_prediction, direct_predictions=direct_prediction,
                stage=stages["student_stage"].numpy(), inner_oof=inner_ledger, final_oof=final_ledger,
                guidance_original_units=final_g)
