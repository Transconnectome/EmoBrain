#!/bin/bash
# S1: 제안한 ROI 370개를 실제로 묶어 점검한다(열 번호 연결, 공통 ROI, 겹침, 시상하부와 BA34 위치, 등록 이상). CPU, 수 분. 뇌 반응은 배열 크기만 본다.
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 "$PY" s1_roi_final_check.py
