#!/bin/bash
#SBATCH --job-name=bjepa_short
#SBATCH --account=m4641
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --time=01:00:00
#SBATCH --array=0-34
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation/logs/extract_%A_%a.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation/logs/extract_%A_%a.err

set -euo pipefail

ROOT="/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation"
PYTHON="/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python"
TASK_ID="${SLURM_ARRAY_TASK_ID:-${1:-}}"

if [[ -z "$TASK_ID" || "$TASK_ID" == "all" ]]; then
  for TASK in $(seq 0 34); do
    bash "$0" "$TASK"
  done
  exit 0
fi

if (( TASK_ID < 0 || TASK_ID > 34 )); then
  echo "Task ID must be between 0 and 34, or use 'all'."
  exit 2
fi

SUBJECT_INDEX=$((TASK_ID % 5 + 1))
CONDITION_INDEX=$((TASK_ID / 5))
SUBJECT=$(printf "sub-%02d" "$SUBJECT_INDEX")

CONDITIONS=(
  "pretrained:native:mean"
  "scratch:native:mean"
  "pretrained:temporal_mean:mean"
  "pretrained:temporal_center:mean"
  "pretrained:native:zero"
  "pretrained:native:spatial_only"
  "pretrained:native:time_shuffle"
)
IFS=: read -r INIT POSITION PERTURBATION <<< "${CONDITIONS[$CONDITION_INDEX]}"

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-8}"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$ROOT/logs"
cd "$ROOT/horikawa_extraction"

echo "Task $TASK_ID: subject=$SUBJECT init=$INIT position=$POSITION input=$PERTURBATION"

"$PYTHON" -u run_horikawa_extraction.py \
  --subject "$SUBJECT" \
  --init "$INIT" \
  --position-policy "$POSITION" \
  --perturbation "$PERTURBATION" \
  --batch-size 32 \
  --num-workers "${SLURM_CPUS_PER_TASK:-8}"
