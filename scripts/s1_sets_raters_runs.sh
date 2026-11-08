#!/bin/bash
# S1: 중복 15개 구성, 평정자 수 역산, MC run 구성, 8초 반복 종료 시점 (CPU, 수십 초).
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
"$PY" s1_sets_raters_runs.py
