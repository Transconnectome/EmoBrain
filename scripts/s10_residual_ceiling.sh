#!/bin/bash
# S10 6-4d 잔차의 noise ceiling(평정자 표본 잡음 기준). CPU, 로그인 노드, 수 초. 레포 최상위에서 실행한다.
# 사용: bash scripts/s10_residual_ceiling.sh
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
"$PY_CPU" s10_residual_ceiling.py --stats "$OUT_ROOT/s10_stats/beyond_scene"
