#!/bin/bash
# 선형 teacher–student pilot (Perlmutter login node, bash). 피험자 5명 병렬 → 요약.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/linear_distill.sh
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/linear_distill.py
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs
mkdir -p "$LOG"
export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
for s in 01 02 03 04 05; do "$PY" -u "$CODE" --sub $s > "$LOG/distill_sub-$s.log" 2>&1 & done
wait
"$PY" -u "$CODE" --summarize > "$LOG/distill_summary.log" 2>&1
cat "$LOG/distill_summary.log"
