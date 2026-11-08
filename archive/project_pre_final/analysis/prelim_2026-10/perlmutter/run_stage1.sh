#!/bin/bash
# Perlmutter login node 에서 bash 로 실행. 영역 평균 → 피험자 5명 × 단위 병렬 → 합치기·요약·랩서버 재현 대조.
# 단위: [뇌만 → 의미 73 전체], 사람 캡션 (내용만·경유 / 뇌+내용), V-JEPA 2 (내용만·경유 / 뇌+내용)
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/run_stage1.sh [--skip-roi]
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/run_stage1.py
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/ladder
mkdir -p "$LOG"
export PYTHONDONTWRITEBYTECODE=1
[ "${1:-}" = "--skip-roi" ] || "$PY" -u "$CODE" roi > "$LOG/roi.log" 2>&1
run() {  # 스레드 수, 피험자, 단위...
  local t=$1 s=$2; shift 2
  for u in "$@"; do
    OPENBLAS_NUM_THREADS=$t OMP_NUM_THREADS=$t MKL_NUM_THREADS=$t "$PY" -u "$CODE" unit --sub $s --unit "$u" > "$LOG/unit_sub-${s}_${u/:/_}.log" 2>&1
  done
}
for s in 01 02 03 04 05; do
  run 3 $s brain hk_semantic73:all &
  run 3 $s caption_human_mpnet:content &
  run 3 $s caption_human_mpnet:plus &
  run 4 $s vjepa2_vitg_final:content &
  run 4 $s vjepa2_vitg_final:plus &
done
wait
OPENBLAS_NUM_THREADS=8 "$PY" -u "$CODE" summarize > "$LOG/summarize.log" 2>&1
cat "$LOG/summarize.log"
