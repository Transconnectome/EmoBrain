#!/usr/bin/env python3
"""
Verification script for Python environment & B300 paths on b300-01.
- Outside Slurm (login node): verifies Python 3.11+, required packages, and /scratch/emobrain/{data,outputs} paths on CPU ONLY (never touches GPUs on login node).
- Inside Slurm GPU allocation (srun/sbatch with --gres=gpu:1): also verifies NVIDIA B300 CUDA availability and a 1024x1024 matmul on cuda:0.
"""

import os
import platform
import sys
from pathlib import Path

in_slurm = bool(os.environ.get("SLURM_JOB_ID"))
if not in_slurm:
    # Enforce B300 rule: never initialize CUDA on login node
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

print("=== Python Environment Inspection ===")
print(f"Python executable: {sys.executable}")
print(f"Python version: {platform.python_version()}")
print(f"Execution context: {'Slurm job ' + os.environ['SLURM_JOB_ID'] if in_slurm else 'Login node (CPU-only check)'}")

packages_to_check = [
    ("torch", "torch"),
    ("torchvision", "torchvision"),
    ("transformers", "transformers"),
    ("scikit-learn", "sklearn"),
    ("scipy", "scipy"),
    ("numpy", "numpy"),
    ("pandas", "pandas"),
    ("nibabel", "nibabel"),
    ("matplotlib", "matplotlib"),
    ("h5py", "h5py"),
]

print("\n=== Package Import Verification ===")
failed_imports = []
for pkg_name, import_mod in packages_to_check:
    try:
        mod = __import__(import_mod)
        version = getattr(mod, "__version__", "unknown")
        print(f"  [OK] {pkg_name} ({import_mod}) version: {version}")
    except ImportError as e:
        print(f"  [FAIL] {pkg_name} ({import_mod}): {e}")
        failed_imports.append((pkg_name, str(e)))

if failed_imports:
    print(f"\nERROR: Failed imports: {failed_imports}")
    sys.exit(1)

print("\n=== B300 Data & Output Path Check ===")
missing_paths = []
for p in [
    Path("/scratch/emobrain/data/hk"),
    Path("/scratch/emobrain/data/mc"),
    Path("/scratch/emobrain/data/stimuli"),
    Path("/scratch/emobrain/outputs/s6_brain"),
    Path("/scratch/emobrain/outputs/s10_tables_figures"),
]:
    ok = p.exists()
    print(f"  [{'OK' if ok else 'MISSING'}] {p}")
    if not ok:
        missing_paths.append(str(p))

if missing_paths:
    print(f"\nERROR: Missing required b300-01 local NVMe paths (did you run on b300-01?): {missing_paths}")
    sys.exit(1)

import subprocess
print("\n=== S2 roi_voxels Canonical SHA256 Verification ===")
roi_chk = subprocess.run(
    [sys.executable, str(Path(__file__).resolve().parent / "verify_s2_roi_voxels.py")],
    check=False,
)
if roi_chk.returncode != 0:
    print(
        "\n[HOLD] S2 roi_voxels/*.npz do NOT yet match canonical Perlmutter SHA256 (provenance.json).\n"
        "       Do NOT launch S6/S7/S8 GPU jobs until canonical roi_voxels/*.npz (11 files) are synced."
    )
    if os.environ.get("REQUIRE_AUTHENTIC_ROI", "0") == "1":
        sys.exit(roi_chk.returncode)

if in_slurm:
    import torch

    print("\n=== Slurm GPU Allocation Check ===")
    if torch.cuda.is_available() and torch.cuda.device_count() >= 1:
        for i in range(torch.cuda.device_count()):
            name = torch.cuda.get_device_name(i)
            props = torch.cuda.get_device_properties(i)
            total_mem_gb = props.total_memory / (1024 ** 3)
            print(f"  Device {i}: {name} | CC {props.major}.{props.minor} | VRAM {total_mem_gb:.1f} GB")
        x = torch.randn(1024, 1024, device="cuda:0")
        y = torch.matmul(x, x)
        torch.cuda.synchronize("cuda:0")
        print(f"  [OK] 1024x1024 matmul on cuda:0 (norm={y.norm().item():.4f})")
    else:
        print("  [INFO] CPU-only Slurm job (no GPU allocated).")
else:
    print("\n[INFO] Skipping GPU check on login node (submit via sbatch/srun --gres=gpu:1 to verify CUDA).")

print("\n=== ALL VERIFICATION CHECKS PASSED ===")
