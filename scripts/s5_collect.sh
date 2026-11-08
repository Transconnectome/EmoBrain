#!/bin/bash
# S5 결과 점검과 층별 지표. CPU로 돈다. 모든 과제가 끝난 뒤 돌린다. 사용: bash s5_collect.sh <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=8
"$PY" s5_collect.py --design-freeze "${1:?설계 동결 커밋}"
