"""Descriptive summary of one brain-decoding baseline run (no refitting).

Reads <run>/metadata.json and <run>/predictions.tsv written by
project.scripts.run_pilot and writes <run>/summary.json and <run>/summary.md:
overall and per-dimension MSE, MSE reduction relative to the training-mean
predictor, and Pearson r between prediction and target on evaluate rows.

Usage: python -m project.baseline.brain_decoding.summarize EXPERIMENT_ID
       (searches runs/*/EXPERIMENT_ID) or --run-dir PATH.
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def find_run(experiment_id, runs=HERE / "runs"):
    hits = [p for p in runs.glob(f"*/{experiment_id}") if (p / "metadata.json").is_file()]
    if len(hits) != 1:
        raise ValueError(f"Expected one run named {experiment_id} under {runs}, found {len(hits)}")
    return hits[0]


def _mean_r(pred, y, valid):
    rs = []
    for j in range(y.shape[1]):
        m = valid[:, j]
        if m.sum() > 2 and y[m, j].std() > 0 and pred[m, j].std() > 0:
            rs.append(np.corrcoef(pred[m, j], y[m, j])[0, 1])
    return float(np.mean(rs)) if rs else float("nan")


def _reduction(pred, base, y, valid):
    return float(1 - np.square(pred - y)[valid].mean() / np.square(base - y)[valid].mean())


def row_reference(pred, base, y, valid, n=2000, seed=0):
    """Descriptive references on evaluate rows only (no refit, no inference).

    Shuffle: pair each target row with another row's prediction (whole rows, so
    the dimensions keep their joint structure). Bootstrap: resample rows with
    replacement. Rows from two runs of one participant are not independent
    samples of a population, so neither is a significance test.
    """
    rng = np.random.default_rng(seed)
    k = len(y)
    shuffle = np.array([_mean_r(pred[rng.permutation(k)], y, valid) for _ in range(n)])
    boot_red, boot_r = [], []
    for _ in range(n):
        i = rng.integers(0, k, k)
        boot_red.append(_reduction(pred[i], base[i], y[i], valid[i]))
        boot_r.append(_mean_r(pred[i], y[i], valid[i]))
    return dict(n_resamples=n, seed=seed,
                shuffle_mean_r_95th=float(np.nanpercentile(shuffle, 95)),
                shuffle_mean_r_max=float(np.nanmax(shuffle)),
                bootstrap_mse_reduction_95=[float(v) for v in np.nanpercentile(boot_red, [2.5, 97.5])],
                bootstrap_mean_r_95=[float(v) for v in np.nanpercentile(boot_r, [2.5, 97.5])],
                note="descriptive; evaluate rows from two runs of one participant; not a significance test")


def summarize(run):
    meta = json.loads((run / "metadata.json").read_text())
    target = meta["target"]
    names = json.loads((HERE / "codebook" / f"{target}.json").read_text())["columns"]
    rows = list(csv.DictReader((run / "predictions.tsv").open(), delimiter="\t"))
    obs = sorted({r["observation_id"] for r in rows})
    index = {o: i for i, o in enumerate(obs)}
    shape = (len(obs), len(names))
    y, pred, base = np.full(shape, np.nan), np.full(shape, np.nan), np.full(shape, np.nan)
    valid = np.zeros(shape, bool)
    for r in rows:
        i, j = index[r["observation_id"]], int(r["target_dimension"])
        pred[i, j], base[i, j] = float(r["prediction"]), float(r["training_mean_prediction"])
        if r["valid"] == "True":
            valid[i, j], y[i, j] = True, float(r["target"])

    per_dim = []
    for j, name in enumerate(names):
        m = valid[:, j]
        mse = float(np.mean((pred[m, j] - y[m, j]) ** 2))
        mse0 = float(np.mean((base[m, j] - y[m, j]) ** 2))
        r = float(np.corrcoef(pred[m, j], y[m, j])[0, 1]) if m.sum() > 2 and y[m, j].std() > 0 else float("nan")
        per_dim.append(dict(dimension=name, n=int(m.sum()), mse=mse, training_mean_mse=mse0,
                            mse_reduction=1 - mse / mse0 if mse0 > 0 else float("nan"), pearson_r=r))
    rs = np.array([d["pearson_r"] for d in per_dim])
    red = np.array([d["mse_reduction"] for d in per_dim])
    alphas = meta["config"]["alphas"]
    reference = row_reference(pred, base, y, valid)
    out = dict(run=str(run), target=target, participant=meta["participant"],
               preprocessing_id=meta["preprocessing_id"], n_evaluate_rows=len(obs),
               n_fit_plus_tune_rows=len(meta["scope_roles"]["fit"]) + len(meta["scope_roles"]["tune"]),
               selected_alpha=meta["alpha"], alpha_at_grid_edge=meta["alpha"] in (min(alphas), max(alphas)),
               tuning_mse=dict(zip(map(str, alphas), meta["tuning_mse"])),
               mse=meta["mse"], training_mean_mse=meta["training_mean_mse"],
               mse_reduction=1 - meta["mse"] / meta["training_mean_mse"],
               mean_pearson_r=float(np.nanmean(rs)), median_pearson_r=float(np.nanmedian(rs)),
               dims_with_positive_mse_reduction=int(np.sum(red > 0)), n_dims=len(names),
               seconds=meta["seconds"], code_commit=meta["code"]["commit"],
               code_dirty=bool(meta["code"]["dirty"]), reference=reference, per_dimension=per_dim,
               note="one participant, one fixed development split, descriptive only")
    (run / "summary.json").write_text(json.dumps(out, indent=2) + "\n")

    lines = [f"# Brain decoding baseline: {target}", "",
             f"{meta['participant']} · {len(obs)} evaluate rows · fit+tune {out['n_fit_plus_tune_rows']} rows · "
             f"alpha {meta['alpha']:g}{' (grid edge)' if out['alpha_at_grid_edge'] else ''}", "",
             "| Metric | Value |", "| --- | --- |",
             f"| MSE ridge | {out['mse']:.5g} |", f"| MSE training mean | {out['training_mean_mse']:.5g} |",
             f"| MSE reduction vs training mean | {out['mse_reduction']:.3f} |",
             f"| Mean / median Pearson r over dimensions | {out['mean_pearson_r']:.3f} / {out['median_pearson_r']:.3f} |",
             f"| Dimensions with MSE reduction > 0 | {out['dims_with_positive_mse_reduction']} / {len(names)} |",
             f"| Row-bootstrap 95% interval, MSE reduction | {reference['bootstrap_mse_reduction_95'][0]:.3f} to {reference['bootstrap_mse_reduction_95'][1]:.3f} |",
             f"| Row-bootstrap 95% interval, mean r | {reference['bootstrap_mean_r_95'][0]:.3f} to {reference['bootstrap_mean_r_95'][1]:.3f} |",
             f"| Row-shuffle mean r, 95th percentile (max of {reference['n_resamples']}) | {reference['shuffle_mean_r_95th']:.3f} ({reference['shuffle_mean_r_max']:.3f}) |", "",
             "| Dimension | r | MSE reduction |", "| --- | --- | --- |"]
    lines += [f"| {d['dimension']} | {d['pearson_r']:.3f} | {d['mse_reduction']:.3f} |"
              for d in sorted(per_dim, key=lambda d: -np.nan_to_num(d["pearson_r"], nan=-9))]
    lines += ["", "Descriptive development result: one participant, one fixed split, no inference."]
    (run / "summary.md").write_text("\n".join(lines) + "\n")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment_id", nargs="?")
    parser.add_argument("--run-dir", type=Path)
    args = parser.parse_args(argv)
    run = args.run_dir or find_run(args.experiment_id)
    out = summarize(run)
    print(json.dumps({k: v for k, v in out.items() if k != "per_dimension"}, indent=2))


if __name__ == "__main__":
    main()
