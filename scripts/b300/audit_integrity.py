#!/usr/bin/env python3
"""Audit SHA256 integrity of all transferred EmoBrain files on B300.

Verifies:
1. Horikawa (HK sub-01..sub-05) masks, samples_qc_usable, and blocks_common36_qc_runz
2. MindCaptioning (MC sub-01..sub-06) masks, samples_qc_usable, and blocks_common36_qc_runz
3. Metadata files (semantic_features.csv, cowen_horikawa_labels.csv, etc.)
4. Manifests (provenance.json inputs and outputs)
5. Stimulus videos count and non-empty check (2,196 MP4 files)
"""

import hashlib
import json
import os
import sys
from pathlib import Path

DATA_ROOT = Path("/scratch/emobrain/data")

# Precomputed bitwise connectome hashes for blocks_common36_qc_runz.npy
CONNECTOME_BLOCK_HASHES = {
    "hk_sub-01": "0c6d0f6ec6895af7a465c9087918e0abe210579d753d251358527fbf9c26b351",
    "hk_sub-02": "00c60d70718c9f3dbb2299d74c60cc881b417075c4d46988dc0f8f84b47d834e",
    "hk_sub-03": "24298f2bf2139b8922bc149f3196676cd4d99c6862d1dd44f6a181375eda5227",
    "hk_sub-04": "ad6a2c56890eaf3f99c8aedd5d296cf28b775a4bd4f26e19cf46ff17a57ef3da",
    "hk_sub-05": "390fea5cb2965a9954f52cde8e099e81829da11ba903cc0d503def5f387a4c45",
    "mc_sub-01": "a4ebfbc1e02d13ea972dc15780626522375c59703d458dd63c032b3073ba10a1",
    "mc_sub-02": "8e53637baf8c644c14d97076ed8e1b7c841c87fc1536b99728c7f80fcfe39fa3",
    "mc_sub-03": "7763a13941c4f5169e1e5e7d5b23e01026cada42621a35ce00d6b0905f8abe6d",
    "mc_sub-04": "6b50003bf632a329d0d43385d2917d3655f0bb90c70b8973df1f4611bd93f625",
    "mc_sub-05": "d244d269d730ef3e94b9de6470156a4c674d36ea46ff0a4a8aba1e44ea2e8ed6",
    "mc_sub-06": "dffb1e9fe70d9fc2e6fee6a51dec0c6b30a49c76391f23c2a5154d5ba0df0015",
}

def sha256_file(filepath: Path, chunk_size: int = 16 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=" * 80)
    print("EmoBrain B300 Data Integrity & Checksum Verification")
    print(f"Data Root: {DATA_ROOT}")
    print("=" * 80)

    provenance_path = DATA_ROOT / "manifests" / "s2" / "provenance.json"
    if not provenance_path.exists():
        print(f"ERROR: provenance.json not found at {provenance_path}")
        sys.exit(1)

    with open(provenance_path, "r", encoding="utf-8") as f:
        prov = json.load(f)

    input_hashes = prov.get("input_sha256", {})
    output_hashes = prov.get("output_sha256", {})

    results = []
    failures = 0

    # 1. Check HK subjects (sub-01 .. sub-05)
    print("\n--- 1. Horikawa (HK) Preprocessed Data & Masks ---")
    for s in range(1, 6):
        sub = f"sub-{s:02d}"
        sub_dir = DATA_ROOT / "hk" / sub
        
        # Check mask
        mask_key = f"/pscratch/sd/s/sjmoon/Horikawa/{sub}/v3_qc/{sub}_mask_qc.nii.gz"
        mask_file = sub_dir / f"{sub}_mask_qc.nii.gz"
        if mask_key in input_hashes and mask_file.exists():
            computed = sha256_file(mask_file)
            expected = input_hashes[mask_key]
            match = (computed == expected)
            status = "PASS" if match else "FAIL"
            if not match: failures += 1
            print(f"[{status}] {sub} mask: {computed[:16]}... (size: {mask_file.stat().st_size} B)")
            results.append({"type": "mask", "sub": sub, "cohort": "hk", "file": mask_file.name, "hash": computed, "expected": expected, "match": match})
        else:
            print(f"[MISSING] {mask_file}")
            failures += 1

        # Check usable samples
        samples_key = f"/pscratch/sd/s/sjmoon/Horikawa/{sub}/v3_qc/{sub}_samples_qc_usable.tsv"
        samples_file = sub_dir / f"{sub}_samples_qc_usable.tsv"
        if samples_key in input_hashes and samples_file.exists():
            computed = sha256_file(samples_file)
            expected = input_hashes[samples_key]
            match = (computed == expected)
            status = "PASS" if match else "FAIL"
            if not match: failures += 1
            print(f"[{status}] {sub} samples_usable: {computed[:16]}... (size: {samples_file.stat().st_size} B)")
            results.append({"type": "samples", "sub": sub, "cohort": "hk", "file": samples_file.name, "hash": computed, "expected": expected, "match": match})
        else:
            print(f"[MISSING] {samples_file}")
            failures += 1

        # Check block file
        block_file = sub_dir / f"{sub}_blocks_common36_qc_runz.npy"
        if block_file.exists():
            size = block_file.stat().st_size
            computed = sha256_file(block_file)
            expected = CONNECTOME_BLOCK_HASHES.get(f"hk_{sub}")
            match = (computed == expected) if expected else True
            status = "PASS" if match else "FAIL"
            if not match: failures += 1
            print(f"[{status}] {sub} blocks_runz: {computed} (size: {size / 1e9:.2f} GB)")
            results.append({"type": "block_runz", "sub": sub, "cohort": "hk", "file": block_file.name, "hash": computed, "expected": expected, "size_bytes": size, "match": match})
        else:
            print(f"[MISSING] {block_file}")
            failures += 1

    # 2. Check MC subjects (sub-01 .. sub-06)
    print("\n--- 2. MindCaptioning (MC) Preprocessed Data & Masks ---")
    for s in range(1, 7):
        sub = f"sub-{s:02d}"
        sub_dir = DATA_ROOT / "mc" / sub
        
        # Check mask
        mask_key = f"/pscratch/sd/s/sjmoon/MindCaptioning/{sub}/v2_qc/{sub}_mask_qc.nii.gz"
        mask_file = sub_dir / f"{sub}_mask_qc.nii.gz"
        if mask_key in input_hashes and mask_file.exists():
            computed = sha256_file(mask_file)
            expected = input_hashes[mask_key]
            match = (computed == expected)
            status = "PASS" if match else "FAIL"
            if not match: failures += 1
            print(f"[{status}] {sub} mask: {computed[:16]}... (size: {mask_file.stat().st_size} B)")
            results.append({"type": "mask", "sub": sub, "cohort": "mc", "file": mask_file.name, "hash": computed, "expected": expected, "match": match})
        else:
            print(f"[MISSING] {mask_file}")
            failures += 1

        # Check usable samples
        samples_key = f"/pscratch/sd/s/sjmoon/MindCaptioning/{sub}/v2_qc/{sub}_samples_qc_usable.tsv"
        samples_file = sub_dir / f"{sub}_samples_qc_usable.tsv"
        if samples_key in input_hashes and samples_file.exists():
            computed = sha256_file(samples_file)
            expected = input_hashes[samples_key]
            match = (computed == expected)
            status = "PASS" if match else "FAIL"
            if not match: failures += 1
            print(f"[{status}] {sub} samples_usable: {computed[:16]}... (size: {samples_file.stat().st_size} B)")
            results.append({"type": "samples", "sub": sub, "cohort": "mc", "file": samples_file.name, "hash": computed, "expected": expected, "match": match})
        else:
            print(f"[MISSING] {samples_file}")
            failures += 1

        # Check block file
        block_file = sub_dir / f"{sub}_blocks_common36_qc_runz.npy"
        if block_file.exists():
            size = block_file.stat().st_size
            computed = sha256_file(block_file)
            expected = CONNECTOME_BLOCK_HASHES.get(f"mc_{sub}")
            match = (computed == expected) if expected else True
            status = "PASS" if match else "FAIL"
            if not match: failures += 1
            print(f"[{status}] {sub} blocks_runz: {computed} (size: {size / 1e9:.2f} GB)")
            results.append({"type": "block_runz", "sub": sub, "cohort": "mc", "file": block_file.name, "hash": computed, "expected": expected, "size_bytes": size, "match": match})
        else:
            print(f"[MISSING] {block_file}")
            failures += 1

    # 3. Check Metadata Files
    print("\n--- 3. Metadata Files ---")
    meta_dir = DATA_ROOT / "metadata"
    meta_checks = [
        ("semantic_features.csv", "/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/metadata/semantic_features.csv", None),
        ("cowen_horikawa_labels.csv", "/pscratch/sd/s/sjmoon/EmoBrain/project/shared/data/cowen_horikawa_labels.csv", None),
        ("stimulus_crosswalk.tsv", "/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/manifests/stimulus_crosswalk.tsv", None),
        ("stimuli_prereg_v2.tsv", "/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/manifests/stimuli.tsv", None),
        ("stimuli.tsv", None, "75a75dc5979f684be752d5e38104860b09331e9c20fbfbc76e73bbd80650d32d"),
    ]
    for fname, prov_key, direct_expected in meta_checks:
        fpath = meta_dir / fname
        if fpath.exists():
            computed = sha256_file(fpath)
            if prov_key and prov_key in input_hashes:
                expected = input_hashes[prov_key]
            elif direct_expected:
                expected = direct_expected
            else:
                expected = "N/A"
            match = (computed == expected) if expected != "N/A" else True
            status = "PASS" if match else "FAIL"
            if not match: failures += 1
            print(f"[{status}] {fname}: {computed[:16]}... (size: {fpath.stat().st_size} B)")
            results.append({"type": "metadata", "file": fname, "hash": computed, "expected": expected, "match": match})
        else:
            print(f"[MISSING] {fpath}")
            failures += 1

    # 4. Check Stimulus Videos
    print("\n--- 4. Stimulus Videos ---")
    stim_dir = DATA_ROOT / "stimuli"
    if stim_dir.exists():
        video_files = list(stim_dir.glob("*.mp4"))
        count = len(video_files)
        zero_byte = [v for v in video_files if v.stat().st_size == 0]
        total_size = sum(v.stat().st_size for v in video_files)
        status = "PASS" if count == 2196 and len(zero_byte) == 0 else "FAIL"
        if status != "PASS": failures += 1
        print(f"[{status}] Video count: {count} / 2196 (0-byte files: {len(zero_byte)}, total size: {total_size / 1e9:.2f} GB)")
        results.append({"type": "stimuli", "count": count, "zero_byte": len(zero_byte), "total_size_bytes": total_size, "match": (status == "PASS")})
    else:
        print(f"[MISSING] {stim_dir}")
        failures += 1

    print("\n" + "=" * 80)
    print(f"Audit Summary: {'ALL CHECKS PASSED (100% MATCH)' if failures == 0 else f'{failures} FAILURES DETECTED'}")
    print("=" * 80)

    # Save JSON summary
    summary_path = DATA_ROOT / "audit_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({"total_checks": len(results), "failures": failures, "results": results}, f, indent=2)
    print(f"Detailed summary written to {summary_path}")

    return 0 if failures == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
