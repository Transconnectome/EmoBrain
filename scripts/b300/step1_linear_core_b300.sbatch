#!/bin/bash
#SBATCH --job-name=emobrain_step1_linear
#SBATCH --partition=gpu
#SBATCH --nodelist=b300-01
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=96G
#SBATCH --time=04:00:00
#SBATCH --output=outputs/logs/step1_linear_%j.log
# Step 1 (전뇌 선형 핵심 사슬 정품 재실행 + 비순환·구역·네트워크 보강 분석).
# 조건:
#   1) verify_s2_roi_voxels.py가 11/11 정품 SHA256(provenance.json) 일치(exit 0)할 때만 실행된다.
#   2) 기존 합성 ROI 기반 v1 산출물(roi_cells, s5_ridge, s5_collect, pathway_k1_k1a)은 삭제하지 않고
#      /scratch/emobrain/outputs_v1_synthetic_roi/ 아래로 보존 이동한 뒤 깨끗하게 재생성한다.
#   3) src/ 코드는 단 1바이트도 수정하지 않는다(START_CODE SHA256 100% 보존).
set -euo pipefail

if [ -z "${SLURM_JOB_ID:-}" ]; then
  echo "오류: B300 GPU 작업은 반드시 sbatch 또는 srun으로만 제출해야 합니다." >&2
  exit 1
fi

ROOT="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$ROOT/scripts/_env.sh"
FREEZE="${1:-f5c8569}"

echo "[Step 1] 1. 정품 S2 roi_voxels 11개 SHA256 게이트 검증..."
"$PY" "$ROOT/scripts/b300/verify_s2_roi_voxels.py"

OUT_ROOT="/scratch/emobrain/outputs"
BACKUP_ROOT="/scratch/emobrain/outputs_v1_synthetic_roi"
MARKER="$OUT_ROOT/s5_ridge/.authentic_roi_verified"

if [ ! -f "$MARKER" ]; then
  echo "[Step 1] 2. 기존 v1 합성 ROI 산출물 백업 이동 -> $BACKUP_ROOT ..."
  mkdir -p "$BACKUP_ROOT/s2_manifest" "$BACKUP_ROOT/s9_analysis"
  for rel in "s2_manifest/roi_cells" "s5_ridge" "s5_collect" "s9_analysis/pathway_k1_k1a"; do
    if [ -e "$OUT_ROOT/$rel" ] && [ ! -e "$BACKUP_ROOT/$rel" ]; then
      mv "$OUT_ROOT/$rel" "$BACKUP_ROOT/$rel"
    fi
  done
  mkdir -p "$OUT_ROOT/s5_ridge"
  "$PY" "$ROOT/scripts/b300/verify_s2_roi_voxels.py" --json > "$MARKER"
fi

export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export CUBLAS_WORKSPACE_CONFIG=:4096:8
export PYTHONUNBUFFERED=1

echo "[Step 1] 3. S2 ROI 8-cell 좌표 재생성 (s2_roi_cells.py)..."
"$PY" s2_roi_cells.py

echo "[Step 1] 4. S5 64개 층 선형 복원 및 핵심 기준선 (ridge, soft_bce, signal, zone, h2020, mlp)..."
for S in 01 02 03 04 05; do
  echo "  -> sub-${S}: s5_decoding"
  "$PY" s5_decoding.py --participant "$S" --design-freeze "$FREEZE" --device cuda
  for TASK in ridge soft_bce signal zone h2020 mlp; do
    echo "  -> sub-${S}: s5_baselines (${TASK})"
    "$PY" s5_baselines.py --task "$TASK" --participant "$S" --design-freeze "$FREEZE" --device cuda
  done
done

echo "[Step 1] 5. S5 뇌 비사용 영상 기준선 확인 (video: length, lowlevel)..."
"$PY" s5_baselines.py --task video --participant "" --design-freeze "$FREEZE" --device cuda

echo "[Step 1] 6. S5 무결성 수집 및 층별 지표 집계 (s5_collect.py)..."
"$PY" s5_collect.py --design-freeze "$FREEZE"

echo "[Step 1] 7. S9-3 K1(34정서) 및 K1a+B4(14차원) 경로 평가..."
CUDA_VISIBLE_DEVICES="" "$PY" "$ROOT/scripts/s9_s10/s9_pathway_k1_k1a.py"

echo "[Step 1] 8. Step 1 선형 심화 3종 (정서어 제거 K1 비순환성, K1_zone 5구역 일반화, 13네트워크 LONO/SNO)..."
"$PY" "$ROOT/scripts/s9_s10/step1_linear_enrichments.py" --device cuda

echo "[Step 1] 모든 전뇌 선형 핵심 파이프라인 및 심화 분석 완료!"
