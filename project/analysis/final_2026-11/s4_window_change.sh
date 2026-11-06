#!/bin/bash
# S4 긴 영상의 창 사이 변화량. CPU로 가볍다. 설계 동결 뒤에만 돈다. 사용: bash s4_window_change.sh <동결 커밋>
set -euo pipefail
FREEZE="${1:?설계 동결 커밋}"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s4_window_change.py --design-freeze "$FREEZE"
