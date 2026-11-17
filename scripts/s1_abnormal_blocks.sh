#!/bin/bash
# S1: HK 이상 block과 이상 run 목록 (0단계와 같은 정의, CPU, 피험자당 1~2분).
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
"$PY" s1_abnormal_blocks.py
