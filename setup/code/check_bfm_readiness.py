#!/usr/bin/env python3
"""Check readiness for a fresh Horikawa BFM benchmark.

This script intentionally does not inspect old embedding caches under
`Horikawa_embedding/extract_embedding` and does not summarize old EmoDe result
JSONs. It checks source code/checkpoint availability and fresh NetFeeliX output
directories only.
"""

import argparse
import json
from pathlib import Path


ROOT = Path("/pscratch/sd/s/sjmoon")
NETFEELIX = ROOT / "NetFeeliX"
FRESH_ROOT = NETFEELIX / "setup/results/fresh_embeddings/horikawa"


class ModelSpec:
    def __init__(self, name, model_arg, code_path, extractor_path, checkpoint_path, fresh_output_dir, fresh_emb_root, status_note):
        self.name = name
        self.model_arg = model_arg
        self.code_path = code_path
        self.extractor_path = extractor_path
        self.checkpoint_path = checkpoint_path
        self.fresh_output_dir = fresh_output_dir
        self.fresh_emb_root = fresh_emb_root
        self.status_note = status_note


MODEL_SPECS = [
    ModelSpec(
        name="SwiFT-v2",
        model_arg="swift_v2",
        code_path=ROOT / "EmoDe/Foundation_baseline/SwiFT_v2",
        extractor_path=ROOT / "SwiFT_v2/project/main_embedding_extraction.py",
        checkpoint_path=Path("/pscratch/sd/j/jubchoi/Newdata_Phase3_MR0p6/UAH_P2_51M_MR_0p6_L1e-4/best.pt"),
        fresh_output_dir=FRESH_ROOT / "swift_v2/raw",
        fresh_emb_root=FRESH_ROOT / "swift_v2/pooled",
        status_note="requires SwiFT extraction plus pooling into fresh_emb_root",
    ),
    ModelSpec(
        name="Brain-JEPA",
        model_arg="brain_jepa",
        code_path=ROOT / "EmoDe/Foundation_baseline/Brain-JEPA",
        extractor_path=ROOT / "EmoDe/Foundation_baseline/Brain-JEPA/run_embedding_extraction_horikawa.py",
        checkpoint_path=ROOT / "EmoDe/Foundation_baseline/Brain-JEPA/pretrained_models/jepa-ep300.pth",
        fresh_output_dir=FRESH_ROOT / "brain_jepa",
        fresh_emb_root=FRESH_ROOT / "brain_jepa/embeddings/all",
        status_note="extractor writes embeddings/all under fresh_output_dir",
    ),
    ModelSpec(
        name="NeuroSTORM",
        model_arg="neurostorm",
        code_path=ROOT / "EmoDe/Foundation_baseline/NeuroSTORM",
        extractor_path=ROOT / "EmoDe/Foundation_baseline/NeuroSTORM/run_embedding_extraction_horikawa.py",
        checkpoint_path=ROOT / "EmoDe/Foundation_baseline/NeuroSTORM/output/neurostorm/pt_neurostorm_mae_ratio0.5.ckpt",
        fresh_output_dir=FRESH_ROOT / "neurostorm",
        fresh_emb_root=FRESH_ROOT / "neurostorm",
        status_note="extractor writes sub-XX/sub-XX_stimulus_N.pt under fresh_emb_root",
    ),
    ModelSpec(
        name="BrainLM",
        model_arg="brain_lm",
        code_path=ROOT / "EmoDe/Foundation_baseline/BrainLM",
        extractor_path=None,
        checkpoint_path=None,
        fresh_output_dir=FRESH_ROOT / "brain_lm",
        fresh_emb_root=FRESH_ROOT / "brain_lm",
        status_note="fresh Horikawa extractor still needs implementation/confirmation",
    ),
]


def count_fresh_embeddings(model_arg, fresh_emb_root):
    if not fresh_emb_root.exists():
        return 0
    if model_arg == "brain_jepa":
        return len(list(fresh_emb_root.glob("sub-*_stimulus_*.pt"))) + len(list(fresh_emb_root.glob("sub-*_stimulus_*/frame0.pt")))
    if model_arg == "brain_lm":
        return len(list(fresh_emb_root.glob("Horikawa*/embeddings/all/sub-*_stimulus-*/frame0.pt")))
    if model_arg == "neurostorm":
        return len(list(fresh_emb_root.glob("sub-*/sub-*_stimulus_*.pt"))) + len(list(fresh_emb_root.glob("sub-*_stimulus_*/frame0.pt")))
    return len(list(fresh_emb_root.glob("sub-*_stimulus_*/frame0.pt")))


def inspect_model(spec):
    checkpoint_exists = None if spec.checkpoint_path is None else spec.checkpoint_path.exists()
    fresh_count = count_fresh_embeddings(spec.model_arg, spec.fresh_emb_root)
    return {
        "name": spec.name,
        "model_arg": spec.model_arg,
        "code_path": str(spec.code_path),
        "code_exists": spec.code_path.exists(),
        "extractor_path": str(spec.extractor_path) if spec.extractor_path is not None else None,
        "extractor_exists": spec.extractor_path.exists() if spec.extractor_path is not None else False,
        "checkpoint_path": str(spec.checkpoint_path) if spec.checkpoint_path is not None else None,
        "checkpoint_exists": checkpoint_exists,
        "fresh_output_dir": str(spec.fresh_output_dir),
        "fresh_emb_root": str(spec.fresh_emb_root),
        "fresh_embedding_count": fresh_count,
        "fresh_ready_for_probe": fresh_count > 0,
        "status_note": spec.status_note,
    }


def markdown_report(rows):
    lines = [
        "# Fresh BFM Readiness",
        "",
        "This report is for the fresh Horikawa benchmark only. Old caches are deliberately ignored.",
        "",
        "| BFM | Code | Extractor | Checkpoint | Fresh embeddings | Probe-ready | Note |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        checkpoint = "n/a" if row["checkpoint_exists"] is None else "yes" if row["checkpoint_exists"] else "no"
        lines.append(
            "| {name} | {code} | {extractor} | {checkpoint} | {fresh_n} | {ready} | {note} |".format(
                name=row["name"],
                code="yes" if row["code_exists"] else "no",
                extractor="yes" if row["extractor_exists"] else "no",
                checkpoint=checkpoint,
                fresh_n=row["fresh_embedding_count"],
                ready="yes" if row["fresh_ready_for_probe"] else "no",
                note=row["status_note"],
            )
        )
    lines.extend(
        [
            "",
            "Fresh embedding root:",
            "",
            "```text",
            str(FRESH_ROOT),
            "```",
            "",
            "Run fresh extraction first, then run the BFM probe wrapper against these fresh roots.",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", default=str(NETFEELIX / "setup/results/bfm_fresh_readiness.json"))
    parser.add_argument("--output-md", default=str(NETFEELIX / "setup/results/bfm_fresh_readiness.md"))
    args = parser.parse_args()

    rows = [inspect_model(spec) for spec in MODEL_SPECS]
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    output_md.write_text(markdown_report(rows), encoding="utf-8")
    print(f"Wrote {output_json}")
    print(f"Wrote {output_md}")


if __name__ == "__main__":
    main()
