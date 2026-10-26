"""Descriptive summary of one brain-decoding baseline run (no refitting).

Reads <run>/metadata.json and <run>/predictions.tsv written by
project.scripts.run_pilot and writes summary.json and summary.md (into the run
folder, or --out-dir to leave an existing summary untouched): overall and
per-dimension MSE, MSE reduction relative to the training-mean predictor, and
Pearson r between prediction and target on evaluate rows.

Every reported number is recomputed from the valid cells of predictions.tsv.
The run fails (SummaryError) when metadata disagrees with that recomputation,
when the TSV has duplicate, missing, out-of-range or non-finite cells, when its
observations differ from the recorded evaluate scope, or when the codebook
contract pinned in the run metadata is missing or changed, when participant or
content IDs disagree with the run's pinned audit manifest, or when the recorded
alpha is not the tuning-MSE minimum of the declared grid. A training-mean MSE
at or below ZERO_DENOMINATOR makes the MSE reduction undefined (null).

Usage: python -m project.baseline.brain_decoding.summarize EXPERIMENT_ID
       (searches runs/*/EXPERIMENT_ID) or --run-dir PATH [--out-dir PATH].
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REQUIRED_COLUMNS = ("observation_id", "content_id", "participant_id", "target_dimension",
                    "valid", "target", "prediction", "training_mean_prediction")
REL_TOL, ABS_TOL = 1e-9, 1e-12   # metadata vs recomputed overall metrics
ZERO_DENOMINATOR = 1e-12          # training-mean MSE at or below this: reduction undefined
N_RESAMPLES = 2000                # row shuffle and row bootstrap (descriptive references)


class SummaryError(ValueError):
    """Run outputs are inconsistent; nothing is summarized."""


def find_run(experiment_id, runs=HERE / "runs"):
    hits = [p for p in runs.glob(f"*/{experiment_id}") if (p / "metadata.json").is_file()]
    if len(hits) != 1:
        raise ValueError(f"Expected one run named {experiment_id} under {runs}, found {len(hits)}")
    return hits[0]


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pinned_codebook(meta):
    """Dimension names from the codebook contract the run itself verified (path + sha256)."""
    target = meta["target"]
    hits = [(p, h) for p, h in meta.get("sources", {}).items()
            if Path(p).name == f"{target}.json" and Path(p).parent.name == "codebook"]
    if len(hits) != 1:
        raise SummaryError(f"Run metadata pins {len(hits)} codebook contracts for {target}, expected 1")
    path, recorded = hits[0]
    if not Path(path).is_file():
        raise SummaryError(f"Pinned codebook contract is missing: {path}")
    if _sha256(path) != recorded:
        raise SummaryError(f"Pinned codebook contract changed since the run: {path}")
    record = json.loads(Path(path).read_text())
    if record.get("target") != target or not record.get("columns"):
        raise SummaryError("Pinned codebook contract does not describe this target")
    return list(record["columns"])


def _pinned_file(meta, pattern):
    """(path, recorded sha256) of the one source matching ``pattern``; an audit folder
    moved into a sibling superseded/ folder is followed and its bytes compared there."""
    hits = [(Path(p), h) for p, h in meta.get("sources", {}).items() if Path(p).match(pattern)]
    if len(hits) != 1:
        raise SummaryError(f"Run metadata pins {len(hits)} sources matching {pattern}, expected 1")
    path, recorded = hits[0]
    moved = path.parent.parent / "superseded" / path.parent.name / path.name
    path = path if path.is_file() else moved
    if not path.is_file():
        raise SummaryError(f"Pinned source is missing: {hits[0][0]}")
    if _sha256(path) != recorded:
        raise SummaryError(f"Pinned source changed since the run: {path}")
    return path


def pinned_identities(meta):
    """row_id -> (participant_id, content_id) from the run's pinned audit manifest."""
    import pandas as pd
    path = _pinned_file(meta, "manifest_*.tsv.gz")
    m = pd.read_csv(path, sep="\t", usecols=["row_id", "participant_id", "content_id"])
    return dict(zip(m.row_id, zip(m.participant_id, m.content_id)))


def _finite(text, what):
    try:
        value = float(text)
    except ValueError:
        raise SummaryError(f"Non-numeric {what}: {text!r}") from None
    if not math.isfinite(value):
        raise SummaryError(f"Non-finite {what}: {text!r}")
    return value


def load_predictions(run, names, evaluate_ids, participant=None, identities=None):
    """Cell arrays ordered as the recorded evaluate scope; fail closed on any defect.

    With ``participant`` every cell must carry it; with ``identities`` (row_id ->
    (participant_id, content_id) from the pinned manifest) each observation's
    participant and content must match the manifest, consistently across dimensions.
    """
    with (run / "predictions.tsv").open() as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        missing_cols = set(REQUIRED_COLUMNS) - set(reader.fieldnames or ())
        if missing_cols:
            raise SummaryError(f"predictions.tsv lacks columns {sorted(missing_cols)}")
        rows = list(reader)
    evaluate_ids = list(evaluate_ids)
    if len(set(evaluate_ids)) != len(evaluate_ids) or not evaluate_ids:
        raise SummaryError("Recorded evaluate scope is empty or has duplicate IDs")
    index = {o: i for i, o in enumerate(evaluate_ids)}
    shape = (len(evaluate_ids), len(names))
    y, pred, base = (np.full(shape, np.nan) for _ in range(3))
    valid, seen = np.zeros(shape, bool), np.zeros(shape, bool)
    for r in rows:
        if r["observation_id"] not in index:
            raise SummaryError(f"Observation outside the evaluate scope: {r['observation_id']}")
        if participant is not None and r["participant_id"] != participant:
            raise SummaryError(f"Cell participant {r['participant_id']!r} is not the run participant {participant!r}")
        if identities is not None:
            expected = identities.get(r["observation_id"])
            if expected is None or (r["participant_id"], r["content_id"]) != expected:
                raise SummaryError(f"Observation {r['observation_id']} identity "
                                   f"{(r['participant_id'], r['content_id'])} disagrees with the pinned manifest {expected}")
        try:
            j = int(r["target_dimension"])
        except ValueError:
            raise SummaryError(f"Non-integer target_dimension {r['target_dimension']!r}") from None
        if not 0 <= j < len(names):
            raise SummaryError(f"target_dimension {j} outside 0..{len(names) - 1}")
        i = index[r["observation_id"]]
        if seen[i, j]:
            raise SummaryError(f"Duplicate cell ({r['observation_id']}, {j})")
        seen[i, j] = True
        pred[i, j] = _finite(r["prediction"], "prediction")
        base[i, j] = _finite(r["training_mean_prediction"], "training-mean prediction")
        if r["valid"] == "True":
            valid[i, j], y[i, j] = True, _finite(r["target"], "valid target")
        elif r["valid"] != "False" or r["target"] != "":
            raise SummaryError(f"Invalid cell must be valid=False with empty target: {r}")
    if not seen.all():
        i, j = np.argwhere(~seen)[0]
        raise SummaryError(f"{int((~seen).sum())} missing cells, e.g. ({evaluate_ids[i]}, {j})")
    if not valid.any():
        raise SummaryError("No valid target cells")
    return evaluate_ids, y, pred, base, valid


def _reduction(mse, mse0):
    return None if mse0 <= ZERO_DENOMINATOR else 1 - mse / mse0


def _pearson(a, b):
    if len(a) < 3 or a.std() == 0 or b.std() == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def _check_close(name, recorded, recomputed):
    if not isinstance(recorded, (int, float)) or not np.isclose(recorded, recomputed, rtol=REL_TOL, atol=ABS_TOL):
        raise SummaryError(f"{name}: metadata {recorded!r} disagrees with predictions.tsv {recomputed!r}")


def _mean_r(pred, y, valid):
    rs = [_pearson(pred[valid[:, j], j], y[valid[:, j], j]) for j in range(y.shape[1])]
    rs = [r for r in rs if r is not None]
    return float(np.mean(rs)) if rs else float("nan")


def _cell_reduction(pred, base, y, valid):
    r = _reduction(np.square(pred - y)[valid].mean(), np.square(base - y)[valid].mean())
    return float("nan") if r is None else r


def row_reference(pred, base, y, valid, n=None, seed=0):
    """Descriptive references on evaluate rows only (no refit, no inference).

    Shuffle: pair each target row with another row's prediction (whole rows, so
    the dimensions keep their joint structure). Bootstrap: resample rows with
    replacement. Rows from two runs of one participant are not independent
    samples of a population, so neither is a significance test. Resamples with
    an undefined value (zero denominator or no variance) are dropped and counted.
    """
    n = N_RESAMPLES if n is None else n
    rng = np.random.default_rng(seed)
    k = len(y)
    shuffle = np.array([_mean_r(pred[rng.permutation(k)], y, valid) for _ in range(n)])
    boot_red, boot_r = [], []
    for _ in range(n):
        i = rng.integers(0, k, k)
        boot_red.append(_cell_reduction(pred[i], base[i], y[i], valid[i]))
        boot_r.append(_mean_r(pred[i], y[i], valid[i]))
    boot_red, boot_r = np.array(boot_red), np.array(boot_r)

    def interval(x):
        x = x[np.isfinite(x)]
        return [float(v) for v in np.percentile(x, [2.5, 97.5])] if len(x) else None

    finite_shuffle = shuffle[np.isfinite(shuffle)]
    return dict(n_resamples=n, seed=seed,
                undefined_resamples=dict(shuffle=int(n - len(finite_shuffle)),
                                         bootstrap_mse_reduction=int((~np.isfinite(boot_red)).sum()),
                                         bootstrap_mean_r=int((~np.isfinite(boot_r)).sum())),
                shuffle_mean_r_95th=float(np.percentile(finite_shuffle, 95)) if len(finite_shuffle) else None,
                shuffle_mean_r_max=float(finite_shuffle.max()) if len(finite_shuffle) else None,
                bootstrap_mse_reduction_95=interval(boot_red),
                bootstrap_mean_r_95=interval(boot_r),
                note="descriptive; evaluate rows from two runs of one participant; not a significance test")


def _fmt(x, spec=".3f"):
    return "undefined" if x is None else format(x, spec)


def summarize(run, out_dir=None):
    run = Path(run)
    meta = json.loads((run / "metadata.json").read_text())
    if meta.get("target") not in ("cat34", "affect14"):
        raise SummaryError(f"Unsupported target {meta.get('target')!r}")
    target = meta["target"]
    names = pinned_codebook(meta)
    obs, y, pred, base, valid = load_predictions(run, names, meta["scope_roles"]["evaluate"],
                                                 participant=meta["participant"],
                                                 identities=pinned_identities(meta))
    alphas = meta["config"]["alphas"]
    if meta["alpha"] not in alphas or len(meta["tuning_mse"]) != len(alphas):
        raise SummaryError("Selected alpha or tuning MSE does not match the declared grid")
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in meta["tuning_mse"]):
        raise SummaryError("Non-finite tuning MSE")
    # Same rule as the benchmark: first alpha with the smallest tuning MSE.
    if meta["alpha"] != alphas[int(np.argmin(meta["tuning_mse"]))]:
        raise SummaryError(f"Selected alpha {meta['alpha']!r} is not the tuning-MSE minimum "
                           f"{alphas[int(np.argmin(meta['tuning_mse']))]!r}")

    # Overall metrics: mean over all valid cells, as in the fitted benchmark.
    mse = float(np.square(pred - y)[valid].mean())
    mse0 = float(np.square(base - y)[valid].mean())
    _check_close("mse", meta["mse"], mse)
    _check_close("training_mean_mse", meta["training_mean_mse"], mse0)

    per_dim = []
    for j, name in enumerate(names):
        m = valid[:, j]
        if not m.any():
            per_dim.append(dict(dimension=name, n=0, mse=None, training_mean_mse=None,
                                mse_reduction=None, pearson_r=None))
            continue
        d_mse = float(np.mean((pred[m, j] - y[m, j]) ** 2))
        d_mse0 = float(np.mean((base[m, j] - y[m, j]) ** 2))
        per_dim.append(dict(dimension=name, n=int(m.sum()), mse=d_mse, training_mean_mse=d_mse0,
                            mse_reduction=_reduction(d_mse, d_mse0), pearson_r=_pearson(pred[m, j], y[m, j])))
    # Consistency of the two aggregation levels: overall MSE = valid-cell-weighted per-dimension MSE.
    weighted = sum(d["n"] * d["mse"] for d in per_dim if d["n"]) / sum(d["n"] for d in per_dim)
    _check_close("valid-cell-weighted per-dimension mse", mse, weighted)

    rs = [d["pearson_r"] for d in per_dim if d["pearson_r"] is not None]
    reductions = [d["mse_reduction"] for d in per_dim if d["mse_reduction"] is not None]
    reference = row_reference(pred, base, y, valid)
    out = dict(run=str(run), target=target, participant=meta["participant"],
               preprocessing_id=meta["preprocessing_id"], n_evaluate_rows=len(obs),
               n_valid_cells=int(valid.sum()),
               n_fit_plus_tune_rows=len(meta["scope_roles"]["fit"]) + len(meta["scope_roles"]["tune"]),
               selected_alpha=meta["alpha"], alpha_at_grid_edge=meta["alpha"] in (min(alphas), max(alphas)),
               tuning_mse=dict(zip(map(str, alphas), meta["tuning_mse"])),
               mse=mse, training_mean_mse=mse0, mse_reduction=_reduction(mse, mse0),
               metrics_source="recomputed from valid predictions.tsv cells; metadata agrees within "
                              f"rtol {REL_TOL:g}, atol {ABS_TOL:g}",
               mean_pearson_r=float(np.mean(rs)) if rs else None,
               median_pearson_r=float(np.median(rs)) if rs else None,
               undefined_r_dimensions=[d["dimension"] for d in per_dim if d["pearson_r"] is None],
               undefined_reduction_dimensions=[d["dimension"] for d in per_dim if d["mse_reduction"] is None],
               dims_with_positive_mse_reduction=int(sum(r > 0 for r in reductions)), n_dims=len(names),
               seconds=meta["seconds"], code_commit=meta["code"]["commit"],
               code_dirty=bool(meta["code"]["dirty"]), reference=reference, per_dimension=per_dim,
               note="one participant, one fixed development split, descriptive only")
    dest = Path(out_dir) if out_dir else run
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "summary.json").write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")

    b95, r95 = reference["bootstrap_mse_reduction_95"], reference["bootstrap_mean_r_95"]
    lines = [f"# Brain decoding baseline: {target}", "",
             f"{meta['participant']} · {len(obs)} evaluate rows · fit+tune {out['n_fit_plus_tune_rows']} rows · "
             f"alpha {meta['alpha']:g}{' (grid edge)' if out['alpha_at_grid_edge'] else ''}", "",
             "| Metric | Value |", "| --- | --- |",
             f"| MSE ridge | {mse:.5g} |", f"| MSE training mean | {mse0:.5g} |",
             f"| MSE reduction vs training mean | {_fmt(out['mse_reduction'])} |",
             f"| Mean / median Pearson r over dimensions | {_fmt(out['mean_pearson_r'])} / {_fmt(out['median_pearson_r'])} |",
             f"| Dimensions with MSE reduction > 0 | {out['dims_with_positive_mse_reduction']} / {len(names)} |",
             f"| Row-bootstrap 95% interval, MSE reduction | {'undefined' if b95 is None else f'{b95[0]:.3f} to {b95[1]:.3f}'} |",
             f"| Row-bootstrap 95% interval, mean r | {'undefined' if r95 is None else f'{r95[0]:.3f} to {r95[1]:.3f}'} |",
             f"| Row-shuffle mean r, 95th percentile (max of {reference['n_resamples']}) | "
             f"{_fmt(reference['shuffle_mean_r_95th'])} ({_fmt(reference['shuffle_mean_r_max'])}) |", "",
             "| Dimension | r | MSE reduction |", "| --- | --- | --- |"]
    lines += [f"| {d['dimension']} | {_fmt(d['pearson_r'])} | {_fmt(d['mse_reduction'])} |"
              for d in sorted(per_dim, key=lambda d: -9 if d["pearson_r"] is None else -d["pearson_r"])]
    lines += ["", "All numbers recomputed from predictions.tsv. Descriptive development result: "
                  "one participant, one fixed split, no inference."]
    (dest / "summary.md").write_text("\n".join(lines) + "\n")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment_id", nargs="?")
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--out-dir", type=Path, help="write summary here instead of the run folder")
    args = parser.parse_args(argv)
    run = args.run_dir or find_run(args.experiment_id)
    out = summarize(run, args.out_dir)
    print(json.dumps({k: v for k, v in out.items() if k != "per_dimension"}, indent=2))


if __name__ == "__main__":
    main()
