#!/bin/bash
# S4 긴 영상의 창 사이 변화량. CPU로 가볍다. 설계 동결 뒤에만 돈다. 사용: bash s4_window_change.sh <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
FREEZE="${1:?설계 동결 커밋}"
export OMP_NUM_THREADS=4
"$PY" s4_window_change.py --design-freeze "$FREEZE"
