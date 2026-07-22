#!/bin/bash
#SBATCH --job-name=ccn_bjepa_fix
#SBATCH --account=m4641
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --time=01:00:00
#SBATCH --array=1-5
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn/study1/logs/bjepa_fix_%A_%a.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn/study1/logs/bjepa_fix_%A_%a.err

set -euo pipefail

ROOT="/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn"
PYTHON="/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python"
POSITION_POLICY="${1:-native}"
PADDING="${2:-mean}"
SUBJECT=$(printf "sub-%02d" "${SLURM_ARRAY_TASK_ID}")

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export PYTHONDONTWRITEBYTECODE=1

mkdir -p "$ROOT/study1/logs"
cd "$ROOT/study1/code/brain_encoder_validation"

"$PYTHON" -u extract_brain_jepa_frozen.py \
  --subject "$SUBJECT" \
  --init resting \
  --position-policy "$POSITION_POLICY" \
  --padding "$PADDING" \
  --batch-size 32 \
  --num-workers "${SLURM_CPUS_PER_TASK:-8}"
