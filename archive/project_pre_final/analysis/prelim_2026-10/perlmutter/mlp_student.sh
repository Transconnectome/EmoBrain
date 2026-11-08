#!/bin/bash
# MLP student 만 피험자 5명 병렬로 → 요약 (teacher cache 가 있어야 한다). bash 로 실행.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/mlp_student.sh
set -euo pipefail
PYT=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/mlp_student.py
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/students
mkdir -p "$LOG"; export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
for s in 01 02 03 04 05; do "$PYT" -u "$CODE" --sub $s > "$LOG/mlp_sub-$s.log" 2>&1 & done
wait
"$PYT" -u "$CODE" --summarize | tee "$LOG/mlp_summary.log"
