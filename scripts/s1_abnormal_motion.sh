#!/bin/bash
# S1: 튀는 블록 5개와 sub-03 run 31~33의 FD, DVARS 비교 (CPU, 수 초).
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
"$PY" s1_abnormal_motion.py
