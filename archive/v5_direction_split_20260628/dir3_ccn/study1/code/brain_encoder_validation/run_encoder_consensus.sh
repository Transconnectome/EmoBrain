#!/bin/bash
#SBATCH --job-name=ccn_bfm_consensus
#SBATCH --account=m4641
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=06:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn/study1/logs/bfm_consensus_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn/study1/logs/bfm_consensus_%j.err

set -euo pipefail

ROOT="/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn"
PYTHON="/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python"

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-32}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-32}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK:-32}"
export PYTHONDONTWRITEBYTECODE=1
export MPLCONFIGDIR="$ROOT/study1/data/.matplotlib"

mkdir -p "$ROOT/study1/logs" "$MPLCONFIGDIR"
cd "$ROOT/study1/code/brain_encoder_validation"

"$PYTHON" -u run_encoder_consensus.py
