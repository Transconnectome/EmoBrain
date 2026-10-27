#!/bin/bash
# Perlmutter login node 에서 bash 로 실행. 영역 평균 → (영상 단위 + 피험자 5명 병렬) → 요약.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/run_stage1.sh
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/run_stage1.py
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs
mkdir -p "$LOG"
export OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 OMP_NUM_THREADS=8 PYTHONDONTWRITEBYTECODE=1
"$PY" -u "$CODE" roi > "$LOG/roi.log" 2>&1
"$PY" -u "$CODE" stimulus > "$LOG/stimulus.log" 2>&1 &
for s in 01 02 03 04 05; do "$PY" -u "$CODE" sub --sub $s > "$LOG/sub-$s.log" 2>&1 & done
wait
"$PY" -u "$CODE" summarize > "$LOG/summarize.log" 2>&1
cat "$LOG/summarize.log"
