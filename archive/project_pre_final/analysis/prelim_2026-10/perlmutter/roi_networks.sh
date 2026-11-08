#!/bin/bash
# 영역 묶음별 분석, 피험자 5명 병렬 → 요약. bash 로 실행.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/roi_networks.sh
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/roi_networks.py
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/roi_networks
mkdir -p "$LOG"; export OPENBLAS_NUM_THREADS=6 OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 PYTHONDONTWRITEBYTECODE=1
for s in 01 02 03 04 05; do "$PY" -u "$CODE" --sub $s > "$LOG/sub-$s.log" 2>&1 & done
wait
"$PY" -u "$CODE" --summarize | tee "$LOG/summary.log"
