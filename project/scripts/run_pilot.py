"""T005 bounded CPU baseline: metadata plan by default, explicit execution only.

Run as ``python -m project.scripts.run_pilot --audit-dir PATH --target cat34``.
Baseline configs, codebook contracts and runs live in project/baseline/brain_decoding/.
Execution also requires --execute --codebook-contract PATH --experiment-id ID
inside a scheduler allocation, or with --login-node for the bounded CPU baseline
(user decision 2026-10-07). No data download, GPU use, or implicit training.
"""
import argparse
import json
import os
from pathlib import Path
import time


def prepare(audit_dir, config, target):
    import pandas as pd
    from project.data import pilot_adapter as pa
    from project.code.pilot_contracts import validate_scopes

    audit_dir = Path(audit_dir)
    if (audit_dir / "SUPERSEDED.md").exists():
        raise ValueError("Superseded audit; select its reviewed successor explicitly")
    audit = json.loads((audit_dir / "audit.json").read_text())
    if config["stage"] != "development" or config["full_training"] is not False:
        raise ValueError("Only bounded development configuration is supported")
    cohort = pa.require_development_cohort(config["participant"])  # Horikawa develops; MindCaptioning is test
    if set(config["roles"]) != {"fit", "tune", "evaluate"} or any(type(n) is not int or n < 1 for n in config["roles"].values()):
        raise ValueError("Positive fit/tune/evaluate component counts required")
    m = pd.read_csv(audit_dir / f"manifest_{cohort}.tsv.gz", sep="\t")
    if m.reserved.dtype != bool:
        raise ValueError("Reserved flags must be explicit booleans")
    if not m.reserved.any():  # audits before 2026-10-08 left Horikawa-only manifests unmarked
        raise ValueError("Manifest marks no reserved content; rebuild the audit")
    rows = pa.to_observations(m)  # Keep the full manifest, not just selected rows.
    selected = pa.select_dev_subset(m, config["participant"], config["roles"])
    usable = set(m.loc[m.annotation_status == "ok", "row_id"])
    split = {role:[i for i in ids if i in usable] for role,ids in selected.items()}
    quarantine = {role:[i for i in ids if i not in usable] for role,ids in selected.items()}
    validate_scopes(rows, split["fit"], split["tune"], split["evaluate"])
    validate_scopes(rows, split["fit"] + split["tune"], split["evaluate"])
    ids = sum(split.values(), [])
    nvox = audit["inventory"]["participants"][config["participant"]][config["brain_variant"]]["shape"][1]
    if len(ids) > config["max_rows"] or nvox > config["max_voxels"]:
        raise ValueError("Declared bounded pilot row/voxel budget exceeded")
    if len(ids) > 512 or sum(config["roles"].values()) > 12:
        raise ValueError("Full/expanded training is outside this runner's scope")
    chosen = m.set_index("row_id").loc[ids].reset_index()
    if chosen.preprocessing_id.nunique() != 1 or chosen.participant_id.nunique() != 1:
        raise ValueError("First pilot requires one participant/preprocessing version")
    record = dict(mode="metadata plan only; no arrays loaded or model fitted", target=target,
                  participant=config["participant"], preprocessing_id=chosen.preprocessing_id.iloc[0],
                  row_counts={k:len(v) for k,v in split.items()},
                  quarantine_ids=quarantine, split=split, voxel_count=nvox,
                  brain_bytes_float32=len(ids)*nvox*4,
                  requested_memory_gib=config["estimated_memory_gib"],
                  requested_wall_minutes=config["requested_wall_minutes"],
                  estimate_status=config["estimate_status"],
                  codebook_status=audit["codebook"],
                  audit_git=audit["git"],
                  execution_requirements=["reviewed target codebook contract",
                      "revalidated current full manifest and actual input file checksums",
                      "scheduler allocation; one target per separate run"],
                  joint_cohort_scope="not used here; joint manifest connectivity requires a separate research decision")
    return audit, m, rows, chosen, split, record


def verify_codebook(path, target, audit):
    from project.code.pilot.artifacts import file_hash
    if path is None:
        raise ValueError("Actual target codebook verification is required before real-data fitting")
    record = json.loads(Path(path).read_text())
    required = {"target", "columns", "reference_path", "reference_sha256", "reviewed_by", "scale_description"}
    if required - record.keys() or any(not record[k] for k in required):
        raise ValueError("Incomplete reviewed codebook contract")
    expected = audit["codebook"]["cat34_order" if target == "cat34" else "affect14_columns"]
    if record["target"] != target or record["columns"] != expected:
        raise ValueError("Target codebook/order mismatch")
    if file_hash(record["reference_path"]) != record["reference_sha256"]:
        raise ValueError("Codebook evidence checksum mismatch")
    return {str(path): file_hash(path), record["reference_path"]: record["reference_sha256"]}


def verify_inputs(audit, m, chosen, config, *, content=False, paths=None):
    from project.data import pilot_adapter as pa
    paths = pa.DEFAULT_PATHS if paths is None else paths
    digest = pa.check_inventory(audit["inventory"], paths, config["participant"],
                                config["brain_variant"], content=content)
    fresh, info = pa.build_manifest(paths, cohorts=[config["participant"].split("/")[0]])
    labels, _ = pa.load_labels(paths)
    fresh = pa.attach_annotation(fresh, pa.annotation_join(fresh, labels, info["canonical_map"]))
    fields = ["row_id", "content_id", "run_id", "run_group", "preprocessing_id", "reserved",
              "participant_id", "array_row", "annotation_status", "annotation_video"]
    # Re-audit all rows: cannot hide newly reserved/repeated/ambiguous content.
    if not m[fields].sort_values("row_id").reset_index(drop=True).equals(fresh[fields].sort_values("row_id").reset_index(drop=True)):
        raise ValueError("Full manifest changed since audit; rebuild the audit before fitting")
    participant = config["participant"]
    cohort, sub = participant.split("/")
    base = pa.response_dir(paths, cohort, sub)
    records = dict(audit["inventory"]["participants"][participant]["dependencies"][config["brain_variant"]]["files"])
    deps = pa.student_dependencies(paths, cohort, sub, config["brain_variant"])
    if content:
        records.update(audit["inventory"]["shared"]["content_dependencies"]["files"])
        deps.update(pa.content_dependencies(paths))
    source = {str(deps[name]): item["sha256"] for name, item in records.items()}
    source["aggregate_input_digest"] = digest
    cfg = json.loads((base / "preprocessing_config.json").read_text())
    if cfg.get("sdc_existing") in (None, "", "unknown") or not cfg.get("policy"):
        raise ValueError("Unknown preprocessing/SDC version")
    if pa.preprocessing_id(cohort, cfg) != chosen.preprocessing_id.iloc[0]:
        raise ValueError("Preprocessing identity mismatch")
    return source


def load_verified_inputs(audit, manifest, chosen, config, target, *, content=False, paths=None):
    """Check audited dependencies before loading, and batch digests before fitting.

    The optional content path prepares aligned frozen features for future callers;
    it does not create ROI tensors, substitute captions, or launch a teacher.
    """
    from project.data import pilot_adapter as pa

    paths = pa.DEFAULT_PATHS if paths is None else paths
    sources = verify_inputs(audit, manifest, chosen, config, content=content, paths=paths)
    batch = pa.load_student_batch(chosen, paths=paths, brain_variant=config["brain_variant"],
                                  target_spaces=[target])
    inv = audit["inventory"]
    student_files = inv["participants"][config["participant"]]["dependencies"][config["brain_variant"]]["files"]
    student_digest = pa.aggregate_digest(student_files) if content else sources["aggregate_input_digest"]
    if batch.input_digest != student_digest:
        raise ValueError("Student inputs changed between audit verification and batch loading")
    features = None
    if content:
        features = pa.load_content_features(chosen, paths=paths)
        if features.input_digest != pa.aggregate_digest(inv["shared"]["content_dependencies"]["files"]):
            raise ValueError("Content inputs changed between audit verification and feature loading")
    return batch, features, sources


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument("--target", choices=("cat34", "affect14"), required=True)
    parser.add_argument("--config", type=Path, default=Path("project/baseline/brain_decoding/config.json"))
    parser.add_argument("--output-root", type=Path, default=Path("project/baseline/brain_decoding/runs"))
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--codebook-contract", type=Path)
    parser.add_argument("--experiment-id")
    parser.add_argument("--participant", help="override config participant, e.g. horikawa/sub-01")
    parser.add_argument("--login-node", action="store_true",
                        help="explicitly allow the bounded baseline outside a SLURM allocation")
    args = parser.parse_args(argv)
    config = json.loads(args.config.read_text())
    if args.participant:
        config["participant"] = args.participant  # recorded in metadata.json with the config
    # Set thread bounds before importing numerical libraries.
    os.environ["OPENBLAS_NUM_THREADS"] = str(config["cpu_threads"])
    os.environ["OMP_NUM_THREADS"] = str(config["cpu_threads"])
    audit, manifest, rows, chosen, split, plan = prepare(args.audit_dir, config, args.target)
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return
    if not os.environ.get("SLURM_JOB_ID") and not args.login_node:
        raise ValueError("Real-data fits require a scheduler allocation or explicit --login-node")
    if not args.experiment_id:
        raise ValueError("A new experiment ID is required")
    sources = verify_codebook(args.codebook_contract, args.target, audit)
    from project.code.pilot.artifacts import file_hash, code_record, save_linear_run
    from project.code.pilot.scopes import fingerprint
    from project.code.pilot.baseline import run_linear
    repo = Path(__file__).resolve().parents[2]
    code = code_record(repo)
    code["execution"] = dict(host=os.uname().nodename, slurm_job_id=os.environ.get("SLURM_JOB_ID"),
                             mode="slurm" if os.environ.get("SLURM_JOB_ID") else "login-node")
    if code["branch"] != "docs/unify-study-design-20261006":
        raise ValueError("Pilot must run on the assigned work branch")
    if not (repo / "project/code/pilot_contracts.py").is_file():
        raise ValueError("Synchronize the assigned handoff before a real-data run")
    if Path(args.experiment_id).name != args.experiment_id or args.experiment_id in (".", ".."):
        raise ValueError("Experiment ID must be one path component")
    prep_hash = fingerprint(dict(preprocessing_id=chosen.preprocessing_id.iloc[0],
                                brain_variant=config["brain_variant"]))
    output_root = args.output_root if args.output_root.is_absolute() else repo / args.output_root
    if (output_root / prep_hash / args.experiment_id).exists():
        raise FileExistsError("Experiment output exists; use a new experiment ID")
    sources[str(args.audit_dir / "audit.json")] = file_hash(args.audit_dir / "audit.json")
    manifest_file = args.audit_dir / f"manifest_{config['participant'].split('/')[0]}.tsv.gz"
    sources[str(manifest_file)] = file_hash(manifest_file)
    batch, _, checked_sources = load_verified_inputs(audit, manifest, chosen, config, args.target)
    sources.update(checked_sources)
    start = time.monotonic()
    result = run_linear(rows, batch, split, args.target, config["alphas"])
    output = save_linear_run(output_root, args.experiment_id, rows, batch, split,
                             args.target, result, config, sources, code, time.monotonic()-start)
    print(json.dumps(dict(output=str(output), mse=result["mse"], training_mean_mse=result["training_mean_mse"])))


if __name__ == "__main__":
    main()
