#!/bin/bash
#SBATCH -A m5361
#SBATCH -C cpu
#SBATCH -q shared
#SBATCH -c 32
#SBATCH -t 02:00:00
#SBATCH -J s10_geo_checks
#SBATCH --array=0-24
# S10 geometry 확인 분석(src/s10_geometry_checks.py). GPU 없음. 규칙은 파이썬 파일 머리말.
# fit 하나(참가자 1명 × 변형 1개)는 CPU 16 core로 30~40분, summarize는 몇 분.
# sbatch(레포 최상위에서 제출): sbatch --export=ALL,OUT=<출력 폴더 절대 경로>,FREEZE=<동결 커밋> -o <로그 폴더>/%x_%a.log scripts/s10_geometry_checks.sh
#   배열 번호 0~24 = 참가자 01~05 × 변형 raw, global, size0, size1, size2
# 직접 실행: bash scripts/s10_geometry_checks.sh fit <출력 폴더> <동결 커밋> <참가자> <변형>
#            bash scripts/s10_geometry_checks.sh summarize <출력 폴더> <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=16 MKL_NUM_THREADS=16
cd "$ROOT/src"
if [ -n "${SLURM_ARRAY_TASK_ID:-}" ]; then
    PARTS=(01 02 03 04 05); VARS=(raw global size0 size1 size2)
    P="${PARTS[$((SLURM_ARRAY_TASK_ID / 5))]}"; V="${VARS[$((SLURM_ARRAY_TASK_ID % 5))]}"
    "$PY" s10_geometry_checks.py fit --participant "$P" --variant "$V" --out "${OUT:?}" --design-freeze "${FREEZE:?}" --threads 16
    exit 0
fi
STEP="${1:?fit|summarize}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?동결 커밋}"
if [ "$STEP" = fit ]; then
    "$PY" s10_geometry_checks.py fit --participant "${4:?참가자}" --variant "${5:?변형}" --out "$OUT" --design-freeze "$FREEZE" --threads 16
else
    "$PY" s10_geometry_checks.py summarize --out "$OUT" --design-freeze "$FREEZE"
fi
