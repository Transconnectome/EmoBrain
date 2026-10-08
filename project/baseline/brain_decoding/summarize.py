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
               code_dirty=bool(meta["code"]["dirty"]), per_dimension=per_dim,
               note="one participant, one fixed development split, descriptive only")
    (run / "summary.json").write_text(json.dumps(out, indent=2) + "\n")

    lines = [f"# Brain decoding baseline: {target}", "",
             f"{meta['participant']} · {len(obs)} evaluate rows · fit+tune {out['n_fit_plus_tune_rows']} rows · "
             f"alpha {meta['alpha']:g}{' (grid edge)' if out['alpha_at_grid_edge'] else ''}", "",
             "| Metric | Value |", "| --- | --- |",
             f"| MSE ridge | {out['mse']:.5g} |", f"| MSE training mean | {out['training_mean_mse']:.5g} |",
             f"| MSE reduction vs training mean | {out['mse_reduction']:.3f} |",
             f"| Mean / median Pearson r over dimensions | {out['mean_pearson_r']:.3f} / {out['median_pearson_r']:.3f} |",
             f"| Dimensions with MSE reduction > 0 | {out['dims_with_positive_mse_reduction']} / {len(names)} |", "",
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
