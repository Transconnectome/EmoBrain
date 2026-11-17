#!/bin/bash
# S10 평정을 부분으로 나눠 영역마다 읽기(src/s10_rating_parts.py). GPU 없음. 규칙과 미리 적은 가설은 파이썬 파일 머리말.
# parts는 몇 분(평정과 feature만), fit은 참가자당 몇 분(CPU 16 thread), summarize는 몇 초.
# 사용(레포 최상위): bash scripts/s10_rating_parts.sh parts <출력 폴더 절대 경로> <동결 커밋>
#                   bash scripts/s10_rating_parts.sh fit <출력 폴더> <동결 커밋> <참가자 01~05>
#                   bash scripts/s10_rating_parts.sh summarize <출력 폴더> <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
STEP="${1:?parts|fit|summarize}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?동결 커밋}"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=16 MKL_NUM_THREADS=16
cd "$ROOT/src"
if [ "$STEP" = fit ]; then
    "$PY" s10_rating_parts.py fit --participant "${4:?참가자}" --out "$OUT" --design-freeze "$FREEZE" --threads 16
else
    "$PY" s10_rating_parts.py "$STEP" --out "$OUT" --design-freeze "$FREEZE" --threads 16
fi
