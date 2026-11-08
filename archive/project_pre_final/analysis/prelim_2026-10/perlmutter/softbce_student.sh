#!/bin/bash
# soft BCE 선형 student 만 피험자 5명 병렬로 → 요약·효과 크기 (teacher cache 재사용). bash 로 실행.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/softbce_student.sh
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/softbce_student.py
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/students
mkdir -p "$LOG"; export OPENBLAS_NUM_THREADS=6 OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 PYTHONDONTWRITEBYTECODE=1
for s in 01 02 03 04 05; do "$PY" -u "$CODE" --sub $s > "$LOG/softbce_sub-$s.log" 2>&1 & done
wait
{ "$PY" -u "$CODE" --summarize; "$PY" -u "$CODE" --effect-size; } | tee "$LOG/softbce_summary.log"
