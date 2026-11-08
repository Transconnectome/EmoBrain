#!/bin/bash
# S1: 34개 라벨 열 대조와 MC 최종 시험 72개 목록 (CPU, 수 초).
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
"$PY" s1_labels_mc72.py
