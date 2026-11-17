#!/bin/bash
# S3 저자 특징 대조. 가볍다. s3_collect 뒤에 돌린다. 사용: bash s3_author_check.sh
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=4
"$PY_CPU" s3_author_check.py
