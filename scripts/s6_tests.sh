#!/bin/bash
# S6 합성 자료 시험. 실제 정답, 실제 뇌 반응은 읽지 않는다. 사용: bash s6_tests.sh [--timing]
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=''
"$PY" "$ROOT/tests/s6_tests.py" "$@"
