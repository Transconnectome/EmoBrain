#!/bin/bash
#SBATCH --job-name=emobrain_step2_s6
#SBATCH --partition=gpu
#SBATCH --nodelist=b300-01
#SBATCH --array=1-6%6
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=outputs/logs/step2_s6_fold%a_%A.log
# Step 2 (정품 ROI 기반 S6 핵심 11개 조건 의존성-닫힘 학습, Fold 1~6 병렬).
# - 전체 21개 조건(~290 runs/fold) 중 중복·저효율 보조 조건(D-3_paired, D-3, C-1_grad, D-4,
#   multimodal, E-고정/학습, D-2, 섞기 대조군 2종)을 생략하고,
#   사전등록 [2-1], [2-2], [2-3(가)~(바) 6개 전체], 1-2(가)/(나), O33, K1/K1a, 6-4b, F7/N22에
#   필수적인 핵심 11개 조건(117 runs/fold, GPU 시간 약 60% 절감, 약 4.5~5.5시간)만 정확히 학습한다.
# - 타 사용자 GPU 점유 시 제출 시점에 `--array=1-6%4` 또는 `--array=1-6%2`로 동시 실행 수를 조절한다.
set -euo pipefail

if [ -z "${SLURM_JOB_ID:-}" ]; then
  echo "오류: B300 GPU 작업은 반드시 sbatch 또는 srun으로만 제출해야 합니다." >&2
  exit 1
fi

ROOT="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$ROOT/scripts/_env.sh"

FOLD="${SLURM_ARRAY_TASK_ID:?SLURM_ARRAY_TASK_ID 필요 (1..6)}"
CONFIG="${1:-$ROOT/configs/s6/run_config.json}"
FREEZE="${2:-f5c8569}"

# S.ORDER 순서를 엄수한 의존성-닫힘 핵심 11개 조건
CORE_CONDITIONS="brain_only,brain_only_featdec,brain_decoded,brain_decoded_additive,brain_only_distill,brain_decoded_distill,feature_encoder,brain_decoded_sep,control_label_smoothing,brain_only_pool,brain_decoded_pool"

echo "[Step 2 Fold ${FOLD}] 1. 정품 S2 roi_voxels SHA256 게이트 검증..."
"$PY" "$ROOT/scripts/b300/verify_s2_roi_voxels.py"

S6_ROOT="/scratch/emobrain/outputs/s6_brain"
BACKUP_S6="/scratch/emobrain/outputs_v1_synthetic_roi/s6_brain"
FOLD_MARKER="$S6_ROOT/.authentic_roi_verified_fold${FOLD}"

mkdir -p "$S6_ROOT" "$BACKUP_S6"
if [ ! -f "$FOLD_MARKER" ]; then
  if [ -d "$S6_ROOT/outer_fold${FOLD}" ] && [ ! -e "$BACKUP_S6/outer_fold${FOLD}" ]; then
    echo "[Step 2 Fold ${FOLD}] 2. 기존 v1 합성 ROI outer_fold${FOLD} 백업 이동 -> $BACKUP_S6/outer_fold${FOLD}"
    mv "$S6_ROOT/outer_fold${FOLD}" "$BACKUP_S6/outer_fold${FOLD}"
  fi
  "$PY" "$ROOT/scripts/b300/verify_s2_roi_voxels.py" --json > "$FOLD_MARKER"
fi

export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export CUBLAS_WORKSPACE_CONFIG=:4096:8
export PYTHONUNBUFFERED=1

echo "[Step 2 Fold ${FOLD}] 3. S6 핵심 11개 조건 학습 시작 (outer_fold${FOLD})..."
"$PY" s6_train.py \
  --plan "outer_fold${FOLD}" \
  --conditions "$CORE_CONDITIONS" \
  --config "$CONFIG" \
  --design-freeze "$FREEZE" \
  --device cuda

echo "[Step 2 Fold ${FOLD}] 완료!"
