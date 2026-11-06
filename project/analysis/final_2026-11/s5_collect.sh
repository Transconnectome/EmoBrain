#!/bin/bash
# S5 결과 점검과 층별 지표. CPU로 돈다. 모든 과제가 끝난 뒤 돌린다. 사용: bash s5_collect.sh <동결 커밋>
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s5_collect.py --design-freeze "${1:?설계 동결 커밋}"
