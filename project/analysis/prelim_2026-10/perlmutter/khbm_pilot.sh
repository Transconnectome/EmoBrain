#!/bin/bash
# KHBM 초록용 빠른 예비 분석 (CPU). 선형과 영역 분해, 공유 MLP 6 fold를 병렬로 돌린 뒤 바꿔 끼우기와 요약.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/khbm_pilot.sh
set -uo pipefail
PYT=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/khbm_pilot.py
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/khbm_pilot
mkdir -p "$LOG"; export OMP_NUM_THREADS=5 OPENBLAS_NUM_THREADS=5 MKL_NUM_THREADS=5 PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=ignore
OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 "$PYT" -u "$CODE" --stage linear > "$LOG/linear.log" 2>&1 &
OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 "$PYT" -u "$CODE" --stage hierarchy > "$LOG/hierarchy.log" 2>&1 &
for f in 0 1 2 3 4 5; do "$PYT" -u "$CODE" --stage mlp --fold $f > "$LOG/mlp_fold$f.log" 2>&1 & done
wait
"$PYT" -u "$CODE" --stage swap > "$LOG/swap.log" 2>&1
OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 "$PYT" -u "$CODE" --stage summary > "$LOG/summary.log" 2>&1
echo 끝
