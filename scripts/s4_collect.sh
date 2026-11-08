#!/bin/bash
# S4 결과 점검과 요약 표. CPU로 가볍다. 과제가 모두 끝난 뒤 돌린다. 사용: bash s4_collect.sh <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
FREEZE="${1:?설계 동결 커밋}"
export OMP_NUM_THREADS=4
"$PY" s4_collect.py --design-freeze "$FREEZE"
