#!/bin/bash
# S10 Dec-바 ridge판과 CCGP(src/s10_capzone_ridge.py). CPU. 참가자 하나 수십 분(16 thread), caption 수 분, summarize 수 분. 레포 최상위에서 실행한다.
# 사용: bash scripts/s10_capzone_ridge.sh fit <출력 폴더> <동결 커밋> <01~05|caption>
#       bash scripts/s10_capzone_ridge.sh summarize <출력 폴더> <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=16 MKL_NUM_THREADS=16
STEP="${1:?fit|summarize}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?동결 커밋}"
if [ "$STEP" = fit ]; then
  "$PY" s10_capzone_ridge.py fit --participant "${4:?참가자 또는 caption}" --out "$OUT" --design-freeze "$FREEZE" --threads 16
else
  "$PY" s10_capzone_ridge.py summarize --out "$OUT" --design-freeze "$FREEZE"
fi
