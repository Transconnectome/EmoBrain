#!/bin/bash
# teacher cache → soft BCE 선형 student (34개 범주) + MLP student (34개·14개) 를 피험자 5명 병렬로 → 요약.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/students.sh [--skip-cache]
set -euo pipefail
D=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter
PY=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python             # numpy·scipy (soft BCE)
PYT=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python        # torch (MLP)
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/students
mkdir -p "$LOG"; export PYTHONDONTWRITEBYTECODE=1
if [ "${1:-}" != "--skip-cache" ]; then
  for s in 01 02 03 04 05; do OPENBLAS_NUM_THREADS=6 OMP_NUM_THREADS=6 "$PY" -u $D/teacher_cache.py --sub $s > "$LOG/teacher_cache_sub-$s.log" 2>&1 & done
  wait
fi
for s in 01 02 03 04 05; do
  OPENBLAS_NUM_THREADS=6 OMP_NUM_THREADS=6 "$PY" -u $D/softbce_student.py --sub $s > "$LOG/softbce_sub-$s.log" 2>&1 &
  OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 "$PYT" -u $D/mlp_student.py --sub $s > "$LOG/mlp_sub-$s.log" 2>&1 &
done
wait
"$PY" -u $D/softbce_student.py --summarize > "$LOG/softbce_summary.log" 2>&1
"$PYT" -u $D/mlp_student.py --summarize > "$LOG/mlp_summary.log" 2>&1
cat "$LOG/softbce_summary.log" "$LOG/mlp_summary.log"
