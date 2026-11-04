#!/bin/bash
# S1: 저자 공개 피질하 mask가 새 mask보다 큰 이유가 경계 처리인지 잰다. s1_subcortex_rebuild.sh의 변환을 다시 쓴다. 뇌 반응은 읽지 않는다.
# 6명씩 병렬, CPU, login node 약 5분. 어느 단계든 실패하면 멈춘다.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11/s1_subcortex_size_check.py
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=2
printf '%s\n' "hk 01" "hk 02" "hk 03" "hk 04" "hk 05" "mc 01" "mc 02" "mc 03" "mc 04" "mc 05" "mc 06" | xargs -P 6 -L 1 bash -c '"$0" "$1" --cohort "$2" --sub "$3"' "$PY" "$CODE"
"$PY" "$CODE" --summary
