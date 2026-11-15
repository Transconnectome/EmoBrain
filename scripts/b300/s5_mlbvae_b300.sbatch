#!/bin/bash
#SBATCH --job-name=emobrain_mlbvae
#SBATCH --partition=gpu
#SBATCH --nodelist=b300-01
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=12
#SBATCH --mem=48G
#SBATCH --time=24:00:00
#SBATCH --array=1-5%2
#SBATCH --output=/scratch/emobrain/outputs/logs/s5_mlbvae_sub%a_%A.log
# b300-01 전용 S5 ML-BVAE 잔여 fold 재개용 Slurm 배열 스크립트 (이미 완료된 fold는 자동 건너뜀).
# 사용(레포 최상위에서):
#   sbatch scripts/b300/s5_mlbvae_b300.sbatch
set -euo pipefail

if [ -z "${SLURM_JOB_ID:-}" ]; then
  echo "오류: B300 GPU 작업은 반드시 sbatch 또는 srun으로만 제출해야 합니다." >&2
  exit 1
fi

ROOT="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$ROOT/scripts/_env.sh"

SUB="$(printf "%02d" "${SLURM_ARRAY_TASK_ID:?}")"
FREEZE="${1:-f5c8569}"
FOLDS="${2:-}"

export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export PYTHONUNBUFFERED=1

"$PY" s5_baselines.py \
  --task mlbvae \
  --participant "$SUB" \
  --design-freeze "$FREEZE" \
  --device cuda \
  --folds "$FOLDS"
