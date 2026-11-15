#!/bin/bash
#SBATCH --job-name=emobrain_s10_repro
#SBATCH --partition=interactive
#SBATCH --nodelist=b300-01
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=outputs/logs/s10_repro_%j.log
# b300-01 공용 산출물(/scratch/emobrain/outputs/)을 읽기 전용으로 읽어,
# 본인 작업 폴더(outputs/s10_repro_<JOBID>/)에 사전등록 판정표·벡터 그림 6종·MASTER_RESULTS_SUMMARY.md를 재생성한다.
# 공용 폴더를 덮어쓰지 않으므로 누구나 안전하게 실행할 수 있다.
# (체크포인트부터 S9·S10 전체를 처음부터 다시 계산할 때는 scripts/s9_s10/s9_*.py 및 s10_metrics_and_tests.py를 별도 실행)
# 사용(레포 최상위에서):
#   mkdir -p outputs/logs && sbatch scripts/b300/s9_s10_cpu_b300.sbatch
set -euo pipefail

ROOT="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
PY="/scratch/envs/centaur/bin/python"
SRC_BASE="/scratch/emobrain/outputs/s10_tables_figures"
REPRO_OUT="${1:-$ROOT/outputs/s10_repro_${SLURM_JOB_ID:-local}}"

mkdir -p "$REPRO_OUT"

export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=4
export PYTHONUNBUFFERED=1

"$PY" "$ROOT/scripts/s9_s10/s10_verdict_and_figures.py" --base-dir "$SRC_BASE" --out-dir "$REPRO_OUT" --mode all
"$PY" "$ROOT/scripts/s9_s10/generate_master_summary.py" --base-dir "$SRC_BASE" --out-dir "$REPRO_OUT"
echo "재생성 완료: $REPRO_OUT"
