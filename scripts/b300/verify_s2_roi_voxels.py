#!/usr/bin/env python3
"""Verify canonical Perlmutter SHA256 & structural integrity of S2 roi_voxels/*.npz (11 subjects).

Hard gate for Step 1 (S5/K1/K1a) and Step 2 (S6 core) on b300-01:
- Checks all 11 files ({hk_sub-01..05, mc_sub-01..06}.npz) against canonical SHA256 hashes
  recorded in manifests/s2/provenance.json (Glasser HCP360 + ANTs PickAtlas 10 subcortical ROIs).
- Also verifies the 7 required .npz keys, 370 ROI names/order against manifests/s2/roi_table.tsv,
  and per-ROI voxel counts against manifests/s2/roi_voxel_counts.tsv.
- Exits 0 ONLY when all 11 files match provenance.json SHA256 bit-for-bit.
  Exits 2 when synthetic/placeholder files are present (e.g., pre-fix spherical approximation).
  Exits 1 when files are missing or structurally invalid.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
import paths as P  # noqa: E402

SUBJECTS = (
    [("hk", f"{i:02d}") for i in range(1, 6)]
    + [("mc", f"{i:02d}") for i in range(1, 7)]
)
REQUIRED_KEYS = ("roi", "offsets", "columns", "n_columns", "affine", "shape", "mask_sha256")
PROV_PREFIX = "/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/s2_manifest/roi_voxels"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validated_geometry(z, n_rois: int):
    """Validate stored geometry before any integer conversion.

    Integer-valued numeric arrays are accepted; fractional, nonfinite and
    out-of-int64 values are rejected rather than truncated or wrapped.
    Cross-ROI column overlap is intentionally allowed.
    """
    def integers(key, shape=None):
        value = np.asarray(z[key])
        if shape is not None and value.shape != shape:
            raise ValueError(f"{key} shape must be {shape}")
        if value.dtype.kind not in "iuf":
            raise ValueError(f"{key} must contain integers")
        if (not np.isfinite(value).all() or (value < 0).any()
                or (value >= 2**63).any() or (value != np.floor(value)).any()):
            raise ValueError(f"{key} must contain nonnegative int64 values")
        return value.astype(np.int64)

    offsets = integers("offsets", (n_rois + 1,))
    cols = integers("columns")
    if cols.ndim != 1:
        raise ValueError("columns must be one-dimensional")
    n_col = int(integers("n_columns", ()))
    if n_col <= 0:
        raise ValueError("n_columns must be positive")
    if offsets[0] != 0 or (np.diff(offsets) < 0).any():
        raise ValueError("offsets must start at zero and be nondecreasing")
    if offsets[-1] != len(cols) or (cols >= n_col).any():
        raise ValueError("column index out of bounds or offsets length mismatch")
    shape = integers("shape", (3,))
    if (shape <= 0).any():
        raise ValueError("spatial shape dimensions must be positive")
    affine = np.asarray(z["affine"])
    if (affine.shape != (4, 4) or affine.dtype.kind not in "iuf"
            or not np.isfinite(affine).all()):
        raise ValueError("affine must be a finite numeric 4x4 matrix")
    return offsets, cols, n_col


def verify_all(roi_dir: Path) -> dict:
    prov = json.loads((REPO / "manifests/s2/provenance.json").read_text(encoding="utf-8"))
    in_sha = prov["input_sha256"]
    roi_table = pd.read_csv(REPO / "manifests/s2/roi_table.tsv", sep="\t")
    expected_rois = roi_table["roi"].astype(str).tolist()
    counts_df = pd.read_csv(REPO / "manifests/s2/roi_voxel_counts.tsv", sep="\t")

    rows = []
    n_authentic = 0
    n_synthetic = 0
    n_missing_or_bad = 0

    for cohort, s in SUBJECTS:
        tag = f"{cohort}_sub-{s}"
        prov_key = f"{PROV_PREFIX}/{tag}.npz"
        expected_sha = in_sha[prov_key]
        mask_prov_key = (
            f"/pscratch/sd/s/sjmoon/{'Horikawa' if cohort == 'hk' else 'MindCaptioning'}/"
            f"sub-{s}/{'v3_qc' if cohort == 'hk' else 'v2_qc'}/sub-{s}_mask_qc.nii.gz"
        )
        expected_mask_sha = in_sha[mask_prov_key]
        fpath = roi_dir / f"{tag}.npz"

        if not fpath.exists():
            n_missing_or_bad += 1
            rows.append({
                "tag": tag,
                "status": "MISSING",
                "sha256": None,
                "expected_sha256": expected_sha,
                "unique_voxels": None,
                "n_columns": None,
                "coverage_frac": None,
                "detail": f"missing file: {fpath}",
            })
            continue

        actual_sha = sha256_file(fpath)
        try:
            with np.load(fpath, allow_pickle=False) as z:
                missing_keys = [k for k in REQUIRED_KEYS if k not in z.files]
                if missing_keys:
                    raise ValueError(f"missing keys {missing_keys}")
                rois = [str(x) for x in z["roi"].tolist()]
                if rois != expected_rois:
                    raise ValueError("370 ROI names/order mismatch vs roi_table.tsv")
                offsets, cols, n_col = validated_geometry(z, len(expected_rois))
                mask_sha = str(z["mask_sha256"])
                if mask_sha != expected_mask_sha:
                    raise ValueError(f"mask_sha256 mismatch ({mask_sha[:12]} != {expected_mask_sha[:12]})")
                sub_counts = (
                    counts_df[
                        (counts_df["cohort"] == cohort)
                        & (counts_df["participant"] == f"sub-{s}")
                    ]
                    .set_index("roi")
                    .loc[expected_rois, "n_voxels"]
                    .to_numpy(np.int64)
                )
                if not np.array_equal(np.diff(offsets), sub_counts):
                    raise ValueError("per-ROI voxel counts mismatch vs roi_voxel_counts.tsv")
                if len(cols) != int(offsets[-1]) or (cols < 0).any() or (cols >= n_col).any():
                    raise ValueError("column index out of bounds")
                n_unique = int(len(np.unique(cols)))
                cov = round(n_unique / max(1, n_col), 4)
        except Exception as exc:
            n_missing_or_bad += 1
            rows.append({
                "tag": tag,
                "status": "STRUCTURAL_ERROR",
                "sha256": actual_sha,
                "expected_sha256": expected_sha,
                "unique_voxels": None,
                "n_columns": None,
                "coverage_frac": None,
                "detail": str(exc),
            })
            continue

        if actual_sha == expected_sha:
            n_authentic += 1
            status = "AUTHENTIC_PASS"
            detail = "matches provenance.json SHA256"
        else:
            n_synthetic += 1
            status = "HASH_MISMATCH_SYNTHETIC"
            detail = (
                f"SHA256 {actual_sha[:12]}... != canonical {expected_sha[:12]}... "
                f"(replace from Perlmutter {PROV_PREFIX}/{tag}.npz)"
            )

        rows.append({
            "tag": tag,
            "status": status,
            "sha256": actual_sha,
            "expected_sha256": expected_sha,
            "unique_voxels": n_unique,
            "n_columns": n_col,
            "coverage_frac": cov,
            "detail": detail,
        })

    return {
        "roi_dir": str(roi_dir),
        "total": len(SUBJECTS),
        "authentic": n_authentic,
        "hash_mismatch_synthetic": n_synthetic,
        "missing_or_error": n_missing_or_bad,
        "all_authentic": (n_authentic == len(SUBJECTS)),
        "subjects": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--roi-dir",
        type=Path,
        default=Path(os.environ.get("S5_ROI_VOXELS", P.OUT / "s2_manifest/roi_voxels")),
        help="Directory containing {hk,mc}_sub-XX.npz",
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON summary only")
    args = ap.parse_args()

    report = verify_all(args.roi_dir)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"=== S2 roi_voxels Canonical Provenance Check ({report['roi_dir']}) ===")
        for r in report["subjects"]:
            cov_s = f"{100.0 * r['coverage_frac']:.1f}% ({r['unique_voxels']}/{r['n_columns']})" if r["coverage_frac"] is not None else "N/A"
            print(f"  [{r['status']:<23}] {r['tag']:<10} | unique={cov_s:<22} | {r['detail']}")
        print(
            f"\nSummary: authentic={report['authentic']}/{report['total']}, "
            f"synthetic_mismatch={report['hash_mismatch_synthetic']}, "
            f"missing_or_error={report['missing_or_error']}"
        )
        if not report["all_authentic"]:
            print(
                "\nACTION REQUIRED: Copy the 11 canonical files from Perlmutter:\n"
                f"  {PROV_PREFIX}/{{hk_sub-01..05,mc_sub-01..06}}.npz\n"
                f"into {report['roi_dir']}/ and re-run this check.",
                file=sys.stderr,
            )

    if report["all_authentic"]:
        return 0
    if report["missing_or_error"] > 0:
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
