#!/bin/bash
# 시각 특징 비교 사다리: 인자로 준 특징마다 피험자 5명 × (내용만·뇌→특징→정서 / 뇌+특징) 단위를 병렬로. 끝나면 사다리 요약.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/vision_ladder.sh hk_vision1000 clip_vitl14
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/run_stage1.py
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/ladder
mkdir -p "$LOG"; export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
for f in "$@"; do
  for s in 01 02 03 04 05; do
    for part in content plus; do "$PY" -u "$CODE" unit --sub $s --unit "$f:$part" > "$LOG/unit_sub-${s}_${f}_${part}.log" 2>&1 & done
  done
done
wait
"$PY" -u "$CODE" summarize | tee "$LOG/summarize_vision.log"
