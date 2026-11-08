#!/bin/bash
# S2: 분할, 내용 구역, 이름표 짝, ROI, CAB-NP 묶음, MC 표를 파일로 고정한다. 앞 단계부터 순서대로 돈다. CPU, login node, 약 10분. 실패하면 멈춘다.
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 "$PY_CPU" s2_manifest.py --stage "${1:-all}"
