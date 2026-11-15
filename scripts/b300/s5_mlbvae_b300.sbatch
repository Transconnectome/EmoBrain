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
#SBATCH --output=outputs/logs/s5_mlbvae_sub%a_%A.log
# [보류/제외 안내] ML-BVAE(30 fold, ~150 GPU-hours)는 핵심 4단계 연구 계획(docs/FUTURE_RESEARCH_PLAN.md)에서
# 과감히 제외(Cut List #2)된 보조 기준선입니다. 리뷰어 추가 요청 등 명시적 사유 없이는 실행하지 마십시오.
# 실행이 꼭 필요한 경우 정품 roi_voxels 검증 통과 후 mkdir -p outputs/logs 뒤 제출합니다.
set -euo pipefail

if [ -z "${SLURM_JOB_ID:-}" ]; then
  echo "오류: B300 GPU 작업은 반드시 sbatch 또는 srun으로만 제출해야 합니다." >&2
  exit 1
fi

ROOT="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$ROOT/scripts/_env.sh"

if [ "${ALLOW_SYNTHETIC_ROI:-0}" != "1" ]; then
  "$PY" "$ROOT/scripts/b300/verify_s2_roi_voxels.py"
fi

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
