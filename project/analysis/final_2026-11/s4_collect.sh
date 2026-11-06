#!/bin/bash
# S4 결과 점검과 요약 표. CPU로 가볍다. 과제가 모두 끝난 뒤 돌린다. 사용: bash s4_collect.sh <동결 커밋>
set -euo pipefail
FREEZE="${1:?설계 동결 커밋}"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s4_collect.py --design-freeze "$FREEZE"
