#!/bin/bash
# 선형 pilot 의 teacher 변형 대조. 인자로 준 변형을 동시에, 변형마다 피험자 5명 병렬로 돌린다. 끝나면 변형 요약.
# 변형 = 내용 특징을 + 로 이은 이름, 뒤에 :shuffle 을 붙이면 pairing 대조.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/teacher_controls.sh vjepa2_vitg_final caption_human_mpnet
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/linear_distill.py
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/linear_distill
mkdir -p "$LOG"; export OPENBLAS_NUM_THREADS=4 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
for v in "$@"; do
  t=${v%%:*}; extra=""; tag=$t
  [ "$v" != "$t" ] && { extra="--shuffle"; tag=${t}_shuffled; }
  for s in 01 02 03 04 05; do "$PY" -u "$CODE" --sub $s --teacher "$t" $extra > "$LOG/${tag}_sub-$s.log" 2>&1 & done
done
wait
"$PY" -u "$CODE" --summarize-variants | tee "$LOG/summary_variants.log"
