#!/bin/bash
# S1: 참가자별 voxel 수, 피질하 10개 정의, 원 논문 fold 배정, 이름표 73개와 34개 범주의 공개 파일 대조 (CPU, 수 초).
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
PYTHONDONTWRITEBYTECODE=1 "$PY_CPU" s1_public_checks.py
