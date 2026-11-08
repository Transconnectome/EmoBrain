#!/bin/bash
# S4 합성 자료 시험. 실제 정답, 뇌 반응은 읽지 않는다. 사용: bash s4_tests.sh
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=''
"$PY" "$ROOT/tests/s4_tests.py"
