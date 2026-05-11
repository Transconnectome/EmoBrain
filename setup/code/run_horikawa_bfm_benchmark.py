#!/usr/bin/env python3
"""Run Horikawa probes on freshly extracted BFM embeddings.

The default embedding roots are NetFeeliX fresh-output directories. This script
refuses legacy cache roots.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path("/pscratch/sd/s/sjmoon")
NETFEELIX = ROOT / "NetFeeliX"
PYTHON = ROOT / "brain-jepa-env/bin/python"
EVALUATOR = ROOT / "EmoDe/evaluation/downstream_eval.py"
DEFAULT_META = ROOT / "Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/horikawa_meta_data_with_dimension_binary.csv"
DEFAULT_SPLIT = ROOT / "EmoDe/Foundation_baseline/SwiFT_v2/data/splits/Horikawa/pretraining"
FRESH_ROOT = NETFEELIX / "setup/results/fresh_embeddings/horikawa"


class BenchmarkModel:
    def __init__(self, name, model_arg, fresh_emb_root):
        self.name = name
        self.model_arg = model_arg
        self.fresh_emb_root = fresh_emb_root


MODELS = {
    "swift_v2": BenchmarkModel("SwiFT-v2", "swift_v2", FRESH_ROOT / "swift_v2/pooled"),
    "brain_jepa": BenchmarkModel("Brain-JEPA", "brain_jepa", FRESH_ROOT / "brain_jepa/embeddings/all"),
    "neurostorm": BenchmarkModel("NeuroSTORM", "neurostorm", FRESH_ROOT / "neurostorm"),
    "brain_lm": BenchmarkModel("BrainLM", "brain_lm", FRESH_ROOT / "brain_lm"),
}


def looks_like_legacy_cache(path):
    text = str(path)
    return "/Horikawa_embedding/extract_embedding/" in text or "/EmoDe/evaluation/results/" in text


def count_embedding_files(model_arg, emb_root):
    if not emb_root.exists():
        return 0
    if model_arg == "brain_jepa":
        return len(list(emb_root.glob("sub-*_stimulus_*.pt"))) + len(list(emb_root.glob("sub-*_stimulus_*/frame0.pt")))
    if model_arg == "neurostorm":
        return len(list(emb_root.glob("sub-*/sub-*_stimulus_*.pt"))) + len(list(emb_root.glob("sub-*_stimulus_*/frame0.pt")))
    if model_arg == "brain_lm":
        return len(list(emb_root.glob("Horikawa*/embeddings/all/sub-*_stimulus-*/frame0.pt")))
    return len(list(emb_root.glob("sub-*_stimulus_*/frame0.pt")))


def build_command(model, emb_root, args, output_dir):
    cmd = [
        str(PYTHON),
        "-u",
        str(EVALUATOR),
        "--model",
        model.model_arg,
        "--emb_root",
        str(emb_root),
        "--meta_path",
        str(args.meta_path),
        "--split_dir",
        str(args.split_dir),
        "--output_dir",
        str(output_dir),
        "--tasks",
    ]
    cmd.extend(args.tasks)
    cmd.append("--decoders")
    cmd.extend(args.decoders)
    if args.subjects:
        cmd.extend(["--subjects"] + args.subjects)
    if args.use_gpu:
        cmd.append("--use_gpu")
    return cmd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=list(MODELS.keys()), choices=list(MODELS.keys()))
    parser.add_argument("--tasks", nargs="+", default=["valence", "arousal", "emotion34"], choices=["valence", "arousal", "emotion34"])
    parser.add_argument("--decoders", nargs="+", default=["linear"], choices=["linear", "mlp"])
    parser.add_argument("--subjects", nargs="*", default=None)
    parser.add_argument("--meta-path", default=str(DEFAULT_META))
    parser.add_argument("--split-dir", default=str(DEFAULT_SPLIT))
    parser.add_argument("--out-root", default=str(NETFEELIX / "setup/results/horikawa_bfm_fresh"))
    parser.add_argument("--log-dir", default=str(NETFEELIX / "setup/logs"))
    parser.add_argument("--emb-root", action="append", default=[], help="Override as model=/fresh/path. Legacy cache roots are refused.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--use-gpu", action="store_true")
    args = parser.parse_args()

    overrides = {}
    for item in args.emb_root:
        if "=" not in item:
            raise ValueError("--emb-root must look like model=/path")
        model_key, path = item.split("=", 1)
        overrides[model_key] = Path(path)

    out_root = Path(args.out_root)
    log_dir = Path(args.log_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("MKL_NUM_THREADS", "1")

    runs = []
    for model_key in args.models:
        model = MODELS[model_key]
        emb_root = overrides.get(model_key, model.fresh_emb_root)
        if looks_like_legacy_cache(emb_root):
            raise RuntimeError(f"Refusing legacy cache embedding root for {model.name}: {emb_root}")

        n_embeddings = count_embedding_files(model.model_arg, emb_root)
        if n_embeddings == 0:
            raise RuntimeError(
                f"No fresh embeddings found for {model.name}: {emb_root}. "
                "Run fresh extraction first."
            )

        output_dir = out_root / model.model_arg
        output_dir.mkdir(parents=True, exist_ok=True)
        cmd = build_command(model, emb_root, args, output_dir)
        log_path = log_dir / f"horikawa_bfm_fresh_{model.model_arg}_{time.strftime('%Y%m%d_%H%M%S')}.log"
        print(" ".join(cmd))

        if args.dry_run:
            runs.append({"model": model.name, "status": "dry_run", "emb_root": str(emb_root), "n_embeddings": n_embeddings, "command": cmd})
            continue

        with log_path.open("w", encoding="utf-8") as log_f:
            proc = subprocess.run(cmd, cwd=str(EVALUATOR.parent), env=env, stdout=log_f, stderr=subprocess.STDOUT)
        status = "ok" if proc.returncode == 0 else "failed"
        runs.append({"model": model.name, "status": status, "returncode": proc.returncode, "emb_root": str(emb_root), "n_embeddings": n_embeddings, "log_path": str(log_path)})
        if proc.returncode != 0:
            sys.exit(proc.returncode)

    summary_path = out_root / "run_summary.json"
    summary_path.write_text(json.dumps(runs, indent=2), encoding="utf-8")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
