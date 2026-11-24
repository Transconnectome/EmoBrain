#!/bin/bash
#SBATCH --job-name=emobrain_step2_post
#SBATCH --partition=gpu
#SBATCH --nodelist=b300-01
#SBATCH --ntasks=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=96G
#SBATCH --time=03:00:00
#SBATCH --output=outputs/logs/step2_post_s9_s10_%j.log
# Step 2 완료 직후 S9 전체(경로 교체 2-2/1-1/1-2, 최근접 쌍 O33, K1/K1a, 13네트워크 교란 6-4b) 및
# S10 전체(Table 1~7, 사전등록 6-1 판정표, 벡터 그림 6종, MASTER_RESULTS_SUMMARY.md) 일괄 재계산.
# 제출 예시:
#   sbatch --dependency=afterok:<STEP1_JOBID>:<STEP2_ARRAY_JOBID> scripts/b300/step2_post_s9_s10_b300.sbatch
set -euo pipefail

if [ -z "${SLURM_JOB_ID:-}" ]; then
  echo "오류: B300 GPU/후처리 작업은 반드시 sbatch 또는 srun으로만 제출해야 합니다." >&2
  exit 1
fi

ROOT="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
source "$ROOT/scripts/_env.sh"

echo "[Step 2 Post] 1. 정품 S2 roi_voxels SHA256 검증..."
"$PY" "$ROOT/scripts/b300/verify_s2_roi_voxels.py"

OUT_ROOT="/scratch/emobrain/outputs"
BACKUP_ROOT="/scratch/emobrain/outputs_v1_synthetic_roi"
MARKER="$OUT_ROOT/s10_tables_figures/.authentic_roi_verified"

if [ ! -f "$MARKER" ]; then
  mkdir -p "$BACKUP_ROOT/s9_analysis"
  for rel in "s9_analysis/interchange" "s9_analysis/pair_comparison" "s9_analysis/network_perturbation" "s10_tables_figures"; do
    if [ -e "$OUT_ROOT/$rel" ] && [ ! -e "$BACKUP_ROOT/$rel" ]; then
      mv "$OUT_ROOT/$rel" "$BACKUP_ROOT/$rel"
    fi
  done
  mkdir -p "$OUT_ROOT/s10_tables_figures"
  "$PY" "$ROOT/scripts/b300/verify_s2_roi_voxels.py" --json > "$MARKER"
fi

export OMP_NUM_THREADS=8
export MKL_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
export PYTHONUNBUFFERED=1

echo "[Step 2 Post] 2. S9-1/S9-2 경로 교체(2-2, 1-1, 1-2) 및 최근접 쌍(O33)..."
SLURM_USE_GPU=1 "$PY" "$ROOT/scripts/s9_s10/s9_interchange_and_pairs.py"

echo "[Step 2 Post] 3. S9-3 K1(34정서) 및 K1a+B4(14차원) (S6 C-1/D-1 포함 전체)..."
CUDA_VISIBLE_DEVICES="" "$PY" "$ROOT/scripts/s9_s10/s9_pathway_k1_k1a.py"

echo "[Step 2 Post] 4. S9-4 13개 뇌 묶음 입력 교란(6-4b)..."
SLURM_USE_GPU=1 "$PY" "$ROOT/scripts/s9_s10/s9_network_perturbation.py"

echo "[Step 2 Post] 5. S10 통계 표(Table 1~7) 및 10,000회 순열·부트스트랩 검정..."
SLURM_USE_GPU=1 "$PY" "$ROOT/scripts/s9_s10/s10_metrics_and_tests.py"

echo "[Step 2 Post] 6. S10 사전등록 6-1 통합 판정표·벡터 그림 6종·MASTER_RESULTS_SUMMARY.md 생성..."
mkdir -p "$OUT_ROOT/s10_tables_figures/s9_summary"
cp -r "$OUT_ROOT/s9_analysis/"* "$OUT_ROOT/s10_tables_figures/s9_summary/"
CUDA_VISIBLE_DEVICES="" "$PY" "$ROOT/scripts/s9_s10/s10_verdict_and_figures.py" --base-dir "$OUT_ROOT/s10_tables_figures" --mode all
CUDA_VISIBLE_DEVICES="" "$PY" "$ROOT/scripts/s9_s10/generate_master_summary.py" --base-dir "$OUT_ROOT/s10_tables_figures"

echo "[Step 2 Post] 정품 ROI 기반 S9·S10 전체 갱신 완료!"
