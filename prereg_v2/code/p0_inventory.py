"""Phase 0 / A1-1. Dataset inventory with checksums.

Scientific question
-------------------
Which files actually exist on this system, and do they correspond to what the
project documents claim?

What this excludes
------------------
Without a file-level inventory with content hashes, a later mismatch between a
document's stated sample size and the analysed data cannot be attributed to
either a document error or a silent file change. It also cannot distinguish a
dataset that was never acquired from one that was moved.

Outputs
-------
manifests/file_inventory.tsv   one row per hashed file
manifests/datasets.tsv         one row per declared asset with existence verdict
manifests/declared_paths.json  verdicts on paths referenced inside data files
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from _assets import (  # noqa: E402
    ASSETS,
    DECLARED_PATHS_TO_VERIFY,
    DESIGN_DOCS,
    MANIFESTS,
    provenance,
    sha256_file,
    write_json,
    write_tsv,
)

SCRIPT = "prereg_v2/code/p0_inventory.py"


def dir_summary(path: Path) -> dict:
    """Size and file count without content hashing, for very large trees."""
    n_files, total = 0, 0
    exts: dict[str, int] = {}
    for root, _dirs, files in os.walk(path, onerror=lambda e: None):
        for f in files:
            try:
                total += (Path(root) / f).stat().st_size
                n_files += 1
                exts[Path(f).suffix] = exts.get(Path(f).suffix, 0) + 1
            except OSError:
                pass
    return {"n_files": n_files, "total_bytes": total, "extensions": exts}


def main() -> None:
    prov = provenance(SCRIPT)
    file_rows, asset_rows = [], []

    for name, spec in ASSETS.items():
        path = Path(spec["path"])
        exists = path.exists()
        row = {
            "asset": name,
            "declared_role": spec["declared"],
            "path": str(path),
            "kind": spec["kind"],
            "exists": exists,
        }

        if not exists:
            row.update(n_files=0, total_bytes=0, content_hashed=False,
                       note="PATH DOES NOT EXIST")
            asset_rows.append(row)
            print(f"  [MISSING]  {name}: {path}")
            continue

        if spec["kind"] == "absence_check":
            row.update(n_files=0, total_bytes=0, content_hashed=False,
                       note="declared in prereg_v2; path exists but contents unverified")
            asset_rows.append(row)
            print(f"  [PRESENT?] {name}: {path}")
            continue

        if spec["kind"] == "dir_summary":
            s = dir_summary(path)
            top = sorted(s["extensions"].items(), key=lambda kv: -kv[1])[:4]
            row.update(n_files=s["n_files"], total_bytes=s["total_bytes"],
                       content_hashed=False,
                       note="size and count only; extensions "
                            + ", ".join(f"{k or '<none>'}={v}" for k, v in top))
            asset_rows.append(row)
            print(f"  [SUMMARY]  {name}: {s['n_files']} files, "
                  f"{s['total_bytes'] / 1e9:.2f} GB")
            continue

        targets = ([path] if spec["kind"] == "file"
                   else sorted(path.glob(spec["glob"])))
        total = 0
        for t in targets:
            st = t.stat()
            file_rows.append({
                "asset": name,
                "path": str(t),
                "filename": t.name,
                "size_bytes": st.st_size,
                "mtime_utc": pd.Timestamp(st.st_mtime, unit="s", tz="UTC").isoformat(),
                "sha256": sha256_file(t) if spec["hash_contents"] else "",
            })
            total += st.st_size
        row.update(n_files=len(targets), total_bytes=total,
                   content_hashed=bool(spec["hash_contents"]), note="")
        asset_rows.append(row)
        print(f"  [HASHED]   {name}: {len(targets)} files, {total / 1e6:.1f} MB")

    # Paths referenced inside data files or in the preprocessing provenance.
    declared = {}
    for label, p in DECLARED_PATHS_TO_VERIFY.items():
        declared[label] = {"path": str(p), "exists": Path(p).exists()}
        state = "EXISTS" if declared[label]["exists"] else "DOES NOT EXIST"
        print(f"  [DECLARED] {label}: {state}")

    # Hash the design documents themselves so every later claim is traceable
    # to the exact document text it was checked against.
    docs = {}
    for d in sorted(DESIGN_DOCS.glob("*.md")):
        docs[d.name] = {"path": str(d), "size_bytes": d.stat().st_size,
                        "sha256": sha256_file(d)}
        print(f"  [DOC]      {d.name}: {d.stat().st_size} bytes")

    write_tsv(MANIFESTS / "file_inventory.tsv", pd.DataFrame(file_rows), prov)
    write_tsv(MANIFESTS / "datasets.tsv", pd.DataFrame(asset_rows), prov)
    write_json(MANIFESTS / "declared_paths.json",
               {"provenance": prov, "declared_paths": declared,
                "design_documents": docs})


if __name__ == "__main__":
    main()
