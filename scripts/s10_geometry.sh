#!/bin/bash
# S10 네트워크별 정서 표현 형식 탐색(src/s10_geometry.py). GPU 없음. fit은 참가자당 15분 안팎(CPU 16 thread), summarize는 몇 분. 규칙은 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s10_geometry.sh fit <출력 폴더 절대 경로> <동결 커밋> <참가자 01~05>
#                   bash scripts/s10_geometry.sh summarize <출력 폴더 절대 경로> <동결 커밋>
set -euo pipefail
source "$(dirname "$0")/_env.sh"
STEP="${1:?fit|summarize}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?동결 커밋}"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=16
cd "$ROOT/src"
if [ "$STEP" = fit ]; then
    "$PY" s10_geometry.py fit --participant "${4:?참가자}" --out "$OUT" --design-freeze "$FREEZE" --threads 16
else
    "$PY" s10_geometry.py summarize --out "$OUT" --design-freeze "$FREEZE"
fi
