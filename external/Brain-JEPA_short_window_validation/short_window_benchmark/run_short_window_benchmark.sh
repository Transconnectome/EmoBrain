#!/bin/bash
#SBATCH --job-name=bjepa_bench
#SBATCH --account=m4641
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=06:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation/logs/benchmark_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation/logs/benchmark_%j.err

set -euo pipefail

ROOT="/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation"
PYTHON="/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python"
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-32}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-32}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK:-32}"
export PYTHONDONTWRITEBYTECODE=1
export MPLCONFIGDIR="$ROOT/outputs/.matplotlib"
mkdir -p "$ROOT/logs" "$MPLCONFIGDIR"
cd "$ROOT/short_window_benchmark"
"$PYTHON" -u run_short_window_benchmark.py "$@"
