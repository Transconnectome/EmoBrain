#!/bin/bash
# 희소성 통제 MLP student (34개 범주 양성 가중치), 피험자 5명 병렬 → 요약. teacher cache 필요. bash 로 실행.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/mlp_balanced.sh
set -euo pipefail
PYT=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/mlp_student.py
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/students
mkdir -p "$LOG"; export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
for s in 01 02 03 04 05; do "$PYT" -u "$CODE" --sub $s --balanced > "$LOG/mlp_balanced_sub-$s.log" 2>&1 & done
wait
"$PYT" -u "$CODE" --summarize --balanced | tee "$LOG/mlp_balanced_summary.log"
