#!/bin/bash
#SBATCH --job-name=ccn_cortex
#SBATCH --account=m4641
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn/study1/logs/cortex_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn/study1/logs/cortex_%j.err

set -euo pipefail

ROOT="/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn"
PYTHON="/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python"
SHARED_RANK="${1:-3}"

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-32}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK:-32}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK:-32}"
export MPLCONFIGDIR="$ROOT/study1/data/.matplotlib"

mkdir -p "$ROOT/study1/logs" "$MPLCONFIGDIR"
cd "$ROOT/study1/code/cortical_transformation"

"$PYTHON" -u run_cortical_transformation.py \
  --shared-rank "$SHARED_RANK" \
  --n-pca 100 \
  --max-rank 20 \
  --n-folds 5 \
  --n-shuffles 100
