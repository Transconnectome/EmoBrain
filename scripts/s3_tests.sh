#!/bin/bash
# S3 회귀 시험. 가볍다(CPU, 약 2분). 사용: bash s3_tests.sh
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=4 HF_HUB_OFFLINE=1
"$PY" "$ROOT/tests/s3_tests.py"
