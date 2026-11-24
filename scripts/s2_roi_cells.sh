#!/bin/bash
# ROI 칸 번호(8칸, 입력층 점검의 칸 평균). CPU, 참가자당 수 초. login node에서 bash로 돌린다. s5_common이 torch를 읽으므로 GPU 단계의 Python을 쓴다.
# 사용(레포 최상위에서): bash scripts/s2_roi_cells.sh [--check]
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
"$PY" s2_roi_cells.py "$@"
