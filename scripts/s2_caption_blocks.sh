#!/bin/bash
# S2 캡션 구역(D-바). CPU, 1분 안쪽, 로그인 노드. 규칙은 src/s2_caption_blocks.py 머리말. 레포 최상위에서 실행한다.
# 사용: bash scripts/s2_caption_blocks.sh
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 "$PY_CPU" s2_caption_blocks.py
