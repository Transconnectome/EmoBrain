"""Read-only lineage inventory for W01 (issue #6): server source, inputs and baseline runs.

Records, without training or modifying anything:
- source: branch, HEAD, upstream ahead/behind, git status, untracked project files
  (bytes, sha256), interpreter and package versions;
- runs: every brain-decoding run's files, its metrics recomputed by the strict
  summarize (written to <out>/verify/, never into the run folder), the recorded
  source hashes resolved against the current file, the run commit or a supplied
  byte-exact reconstruction, and the recorded inputs against their current bytes;
- preprocessing: per participant response version, config (policy, sdc,
  sdc_existing), STATUS, generating code hash, mask voxel count, qc/runs.json,
  and whether the referenced lab-server sources are reachable from here.

Each item gets one status: present / verified / changed / not accessible / not found.
Brain arrays are not re-hashed here (sizes up to 2 GB each); their audit hashes
are the reference.

Usage: python -m project.data.lineage_audit --repo REPO --out DIR
       [--reconstructed project/scripts/run_pilot.py=PATH ...]
"""
import argparse
import hashlib
import importlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

PRESENT, VERIFIED, CHANGED = "present", "verified", "changed"
NOT_ACCESSIBLE, NOT_FOUND = "not accessible", "not found"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def git(repo, *args):
    r = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def git_blob_sha256(repo, commit, path):
    r = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), "show", f"{commit}:{path}"], capture_output=True)
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None


def source_inventory(repo):
    upstream = git(repo, "rev-parse", "--abbrev-ref", "@{u}")
    counts = git(repo, "rev-list", "--left-right", "--count", "HEAD...@{u}") if upstream else None
    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all") or ""
    untracked = []
    for line in status.splitlines():
        if line.startswith("?? ") and "__pycache__" not in line:
            p = repo / line[3:]
            untracked.append({"path": line[3:], "bytes": p.stat().st_size, "sha256": sha256(p),
                              "mtime": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(p.stat().st_mtime))})
    versions = {}
    for name in ("numpy", "pandas", "scipy", "nibabel", "torch"):
        try:
            versions[name] = importlib.import_module(name).__version__
        except Exception as e:  # pragma: no cover
            versions[name] = f"not importable: {type(e).__name__}"
    return {"branch": git(repo, "rev-parse", "--abbrev-ref", "HEAD"), "head": git(repo, "rev-parse", "HEAD"),
            "upstream": upstream, "ahead_behind": counts, "status_porcelain": status.splitlines(),
            "untracked_files": untracked, "worktrees": (git(repo, "worktree", "list") or "").splitlines(),
            "environment": {"python": sys.executable, "version": sys.version.split()[0],
                            "host": platform.node(), "packages": versions}}


def code_lineage(repo, meta, reconstructed):
    commit = meta["code"]["commit"]
    out = {}
    for path, recorded in sorted(meta["code"]["source_hashes"].items()):
        cur = repo / path
        entry = {"recorded_sha256": recorded}
        if cur.is_file() and sha256(cur) == recorded:
            entry.update(status=VERIFIED, how="current file has the recorded bytes")
        elif git_blob_sha256(repo, commit, path) == recorded:
            entry.update(status=VERIFIED, how=f"recovered from git {commit[:7]} (current file differs)")
        elif path in reconstructed and sha256(reconstructed[path]) == recorded:
            entry.update(status=VERIFIED, how="byte-exact reconstruction (current file differs, untracked at run time)",
                         reconstruction=str(reconstructed[path]))
        else:
            entry.update(status=CHANGED if cur.is_file() else NOT_FOUND,
                         how="run-time bytes not recovered")
        out[path] = entry
    return out


def input_lineage(sources):
    out = {}
    for path, recorded in sorted(sources.items()):
        p = Path(path)
        moved = p.parent.parent / "superseded" / p.parent.name / p.name  # audits moved after supersession
        if not p.exists() and moved.exists():
            out[path] = {"status": VERIFIED if sha256(moved) == recorded else CHANGED, "recorded_sha256": recorded,
                         "moved_to": str(moved), "note": "recorded path moved to superseded/; bytes compared there"}
        elif not p.exists():
            out[path] = {"status": NOT_FOUND}
        else:
            out[path] = {"status": VERIFIED if sha256(p) == recorded else CHANGED, "recorded_sha256": recorded}
    return out


def run_inventory(repo, out, reconstructed):
    from project.baseline.brain_decoding import summarize as sm
    runs = []
    for meta_path in sorted((repo / "project/baseline/brain_decoding/runs").glob("*/*/metadata.json")):
        run = meta_path.parent
        meta = json.loads(meta_path.read_text())
        files = {f.name: {"bytes": f.stat().st_size, "sha256": sha256(f)} for f in sorted(run.iterdir()) if f.is_file()}
        rec = {"experiment_id": run.name, "preprocessing_hash_dir": run.parent.name, "target": meta["target"],
               "participant": meta["participant"], "preprocessing_id": meta["preprocessing_id"],
               "execution": meta["code"].get("execution"), "run_commit": meta["code"]["commit"],
               "scope_counts": {k: len(v) for k, v in meta["scope_roles"].items()},
               "files": files}
        try:
            verified = sm.summarize(run, out_dir=out / "verify" / run.name)
            old = json.loads((run / "summary.json").read_text()) if (run / "summary.json").is_file() else {}
            keys = ("mse", "training_mean_mse", "mse_reduction", "mean_pearson_r", "median_pearson_r")
            diffs = {k: abs(verified[k] - old[k]) for k in keys if k in old and old[k] is not None}
            rd = [abs(a["pearson_r"] - b["pearson_r"]) for a, b in
                  zip(verified["per_dimension"], old.get("per_dimension", []))
                  if a["pearson_r"] is not None and b.get("pearson_r") is not None]
            rec["metrics"] = {"status": VERIFIED, "recomputed": {k: verified[k] for k in keys},
                              "metadata": {k: meta[k] for k in ("mse", "training_mean_mse")},
                              "max_abs_diff_vs_existing_summary": max(diffs.values()) if diffs else None,
                              "max_abs_diff_per_dimension_r": max(rd) if rd else None}
        except Exception as e:
            rec["metrics"] = {"status": CHANGED, "error": f"{type(e).__name__}: {e}"}
        rec["code"] = code_lineage(repo, meta, reconstructed)
        rec["inputs"] = input_lineage(meta["sources"])
        runs.append(rec)
    logs = sorted(p.name for p in (repo / "project/baseline/brain_decoding/runs/logs").glob("*.log"))
    horikawa = [r["experiment_id"] for r in runs if r["participant"].startswith("horikawa/")]
    return {"runs": runs, "logs": logs,
            "horikawa_runs": horikawa or NOT_FOUND,
            "horikawa_note": "no run folder or metadata with a horikawa participant" if not horikawa else ""}


def preprocessing_lineage(scratch):
    from project.data import pilot_adapter as pa
    out = {}
    for cohort, dirname in pa.COHORT_DIRS.items():
        version = pa.RESPONSE_VERSIONS[cohort]
        for subdir in sorted((scratch / dirname).glob("sub-*")):
            d = subdir / version
            key = f"{cohort}/{subdir.name}"
            if not d.is_dir():
                out[key] = {"status": NOT_FOUND, "version": version}
                continue
            cfg = json.loads((d / "preprocessing_config.json").read_text())
            st = json.loads((d / "STATUS.json").read_text())
            code = {f.name: sha256(f) for f in sorted((d / "code").glob("*")) if f.is_file()}
            script_ok = cfg.get("script_sha256") in code.values()
            import nibabel as nib
            mask_vox = int((nib.load(str(d / f"{subdir.name}_mask.nii.gz")).get_fdata() > 0).sum())
            qc = json.loads((d / "qc" / "runs.json").read_text())
            remote = {k: cfg[k] for k in ("whole_brain_mask", "gm_probability_map", "original_samples", "crosswalk")
                      if k in cfg}
            out[key] = {
                "status": VERIFIED if (st.get("state") == "complete" and script_ok
                                       and mask_vox == cfg.get("n_analysis_voxels") == st.get("voxels")) else CHANGED,
                "version": version, "policy": cfg.get("policy"), "sdc": cfg.get("sdc"),
                "sdc_existing": cfg.get("sdc_existing"),
                "sdc_note": "v3 keeps a legacy sdc_existing; sdc describes the correction" if "sdc" in cfg else "",
                "preprocessing_id": pa.preprocessing_id(cohort, cfg),
                "status_json": {k: st.get(k) for k in ("state", "runs", "samples", "voxels", "completed_utc")},
                "generating_code_matches_config_hash": script_ok, "code_sha256": code,
                "mask_voxels": mask_vox, "config_voxels": cfg.get("n_analysis_voxels"),
                "qc_runs": len(qc), "qc_constant_voxel_runs": sum(len(r.get("constant_voxel_indices") or []) for r in qc),
                "sha256": {n: sha256(d / n) for n in (f"{subdir.name}_samples.tsv", f"{subdir.name}_mask.nii.gz",
                                                       "preprocessing_config.json", "STATUS.json", "qc/runs.json")},
                "folders_present": sorted(p.name for p in d.iterdir() if p.is_dir()),
                "lab_server_sources": {k: {"path": v, "status": PRESENT if Path(v).exists() else NOT_ACCESSIBLE}
                                       for k, v in remote.items()},
                "run_level_masks": NOT_ACCESSIBLE + " (only the final intersection mask is on this server)",
            }
    return out


def report_md(src, runs, prep):
    lines = ["# W01 lineage inventory", "", f"Generated {time.strftime('%Y-%m-%d %H:%M %Z')} on {src['environment']['host']}; "
             "read-only (no training, no file in the repository or data folders modified).", "",
             "## Source", "", f"- branch `{src['branch']}`, HEAD `{src['head'][:7]}`, upstream `{src['upstream']}` "
             f"(ahead/behind {src['ahead_behind']})",
             f"- untracked project files: {len(src['untracked_files'])}"]
    lines += [f"  - `{u['path']}` {u['bytes']} B sha256 {u['sha256'][:12]}" for u in src["untracked_files"]]
    lines += [f"- python {src['environment']['version']}, " +
              ", ".join(f"{k} {v}" for k, v in src["environment"]["packages"].items()), "", "## Baseline runs", ""]
    for r in runs["runs"]:
        m = r["metrics"]
        lines += [f"### {r['experiment_id']} ({r['participant']}, {r['target']})", "",
                  f"- run commit `{r['run_commit'][:7]}`, execution {r['execution']}, scope {r['scope_counts']}",
                  f"- metrics: **{m['status']}**" + (f"; recomputed {m['recomputed']}; max |diff| vs existing summary "
                                                     f"{m['max_abs_diff_vs_existing_summary']}, per-dimension r "
                                                     f"{m['max_abs_diff_per_dimension_r']}" if m["status"] == VERIFIED
                                                     else f"; {m.get('error')}"),
                  "- code: " + "; ".join(f"`{p}` {e['status']} ({e['how']})" for p, e in r["code"].items()),
                  "- inputs: " + "; ".join(f"`{Path(p).name}` {e['status']}" + (" (moved to superseded/)" if e.get("moved_to") else "")
                                           for p, e in r["inputs"].items()), ""]
    lines += [f"Horikawa runs: {runs['horikawa_runs']} {runs['horikawa_note']}", f"Logs: {runs['logs']}", "",
              "## Preprocessing", "", "| participant | version | status | sdc / sdc_existing | code hash | mask voxels | qc constant voxel-runs | lab-server sources |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k, v in prep.items():
        if v["status"] == NOT_FOUND:
            lines.append(f"| {k} | {v['version']} | not found | | | | | |")
            continue
        sdc = (v["sdc"] or "")[:28] + " / " + str(v["sdc_existing"])
        reach = {s["status"] for s in v["lab_server_sources"].values()}
        lines.append(f"| {k} | {v['version']} | {v['status']} | {sdc} | {'match' if v['generating_code_matches_config_hash'] else 'MISMATCH'} "
                     f"| {v['mask_voxels']} | {v['qc_constant_voxel_runs']} | {', '.join(sorted(reach))} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", type=Path, default=Path("/pscratch/sd/s/sjmoon/EmoBrain"))
    ap.add_argument("--scratch", type=Path, default=Path("/pscratch/sd/s/sjmoon"))
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--reconstructed", action="append", default=[], help="REPO_PATH=FILE byte-exact reconstruction")
    args = ap.parse_args(argv)
    pairs = [item.split("=", 1) for item in args.reconstructed]
    for _, path in pairs:
        if not Path(path).is_file():
            raise SystemExit(f"reconstruction file not found: {path}")
    args.out.mkdir(parents=True, exist_ok=False)
    recon = {}
    for rel, path in pairs:
        keep = args.out / "recovered_sources" / rel
        keep.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, keep)
        recon[rel] = keep
    src = source_inventory(args.repo)
    runs = run_inventory(args.repo, args.out, recon)
    prep = preprocessing_lineage(args.scratch)
    (args.out / "server_source_inventory.json").write_text(json.dumps(src, indent=2))
    (args.out / "run_lineage.json").write_text(json.dumps(runs, indent=2))
    (args.out / "input_lineage.json").write_text(json.dumps(prep, indent=2))
    (args.out / "run_lineage_check.md").write_text(report_md(src, runs, prep))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
    main()
