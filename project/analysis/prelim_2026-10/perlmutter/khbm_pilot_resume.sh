#!/bin/bash
# KHBM 예비 분석에서 끊긴 뒷부분: 바꿔 끼우기(결과가 없을 때만), 요약, 뇌 쪽 선형 모델(참가자별 병렬). 끝나면 17_khbm_pilot/DONE을 만든다.
# 세션과 분리해 실행: setsid nohup bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/khbm_pilot_resume.sh > /dev/null 2>&1 &
set -uo pipefail
PYT=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/khbm_pilot.py
OD=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/17_khbm_pilot
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/khbm_pilot
export OMP_NUM_THREADS=6 OPENBLAS_NUM_THREADS=6 MKL_NUM_THREADS=6 PYTHONDONTWRITEBYTECODE=1 PYTHONWARNINGS=ignore
rm -f "$OD/DONE"
[ -f "$OD/swap/swap_effects.tsv" ] || "$PYT" -u "$CODE" --stage swap > "$LOG/swap.log" 2>&1
OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 "$PYT" -u "$CODE" --stage summary > "$LOG/summary.log" 2>&1 &
for s in 01 02 03 04 05; do "$PYT" -u "$CODE" --stage linear --sub $s > "$LOG/linear_sub-$s.log" 2>&1 & done
wait
date > "$OD/DONE"
