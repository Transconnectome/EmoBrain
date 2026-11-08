#!/bin/bash
# 5명 통합 MLP student: 바깥 fold 6개를 병렬로 → 요약 (피험자별 MLP 와 비교). teacher cache 필요. bash 로 실행.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/mlp_pooled.sh
set -euo pipefail
PYT=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/mlp_student.py
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/students
mkdir -p "$LOG"; export OPENBLAS_NUM_THREADS=6 OMP_NUM_THREADS=6 MKL_NUM_THREADS=6 PYTHONDONTWRITEBYTECODE=1
for f in 0 1 2 3 4 5; do "$PYT" -u "$CODE" --pooled-fold $f > "$LOG/mlp_pooled_fold$f.log" 2>&1 & done
wait
"$PYT" -u "$CODE" --summarize-pooled | tee "$LOG/mlp_pooled_summary.log"
