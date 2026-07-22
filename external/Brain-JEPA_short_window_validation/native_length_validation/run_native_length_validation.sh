#!/bin/bash
#SBATCH --job-name=bjepa_native16
#SBATCH --account=m4641
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --time=04:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation/logs/native_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation/logs/native_%j.err

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: bash run_native_length_validation.sh INPUT_NPY_OR_NPZ [NPZ_KEY] [NORMALIZATION_NPZ]"
  exit 2
fi

ROOT="/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation"
PYTHON="/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python"
INPUT="$1"
KEY="${2:-timeseries}"
NORMALIZATION="${3:-}"
ARGS=(--input "$INPUT" --key "$KEY" --device cuda)
if [[ -n "$NORMALIZATION" ]]; then
  ARGS+=(--normalization-params "$NORMALIZATION")
fi

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$ROOT/logs"
cd "$ROOT/native_length_validation"
"$PYTHON" -u run_native_length_validation.py "${ARGS[@]}"
