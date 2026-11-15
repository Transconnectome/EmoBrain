#!/bin/bash
#SBATCH --job-name=emobrain_s6
#SBATCH --partition=gpu
#SBATCH --nodelist=b300-01
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --output=outputs/logs/s6_%x_%j.log
# b300-01 전용 S6 뇌 모델 학습 Slurm 스크립트.
# 필수 규칙:
#   1) B300 GPU는 반드시 sbatch/srun으로만 실행한다(로그인 노드 SSH/tmux 직접 실행 금지).
#   2) 제출 전 mkdir -p outputs/logs 실행 필요. 개인 작업 시 export S6_OUT=$PWD/outputs/s6_brain 설정 권장.
#   3) 정품 Glasser+PickAtlas roi_voxels 교체(verify_s2_roi_voxels.py 통과) 전에는 GPU 실행을 자동 차단한다.
# 사용(레포 최상위에서):
#   mkdir -p outputs/logs
#   sbatch scripts/b300/s6_train_b300.sbatch outer_fold1 brain_only,brain_decoded
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

PLAN="${1:?분할 이름 필요 (예: zone_block1_fold1_excluded, final_for_mc, outer_fold1)}"
CONDITIONS="${2:?쉼표로 나눈 조건 필요 (예: brain_only,brain_decoded)}"
CONFIG="${3:-$ROOT/configs/s6/run_config.json}"
FREEZE="${4:-f5c8569}"

export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export CUBLAS_WORKSPACE_CONFIG=:4096:8
export PYTHONUNBUFFERED=1

"$PY" s6_train.py \
  --plan "$PLAN" \
  --conditions "$CONDITIONS" \
  --config "$CONFIG" \
  --design-freeze "$FREEZE" \
  --device cuda
