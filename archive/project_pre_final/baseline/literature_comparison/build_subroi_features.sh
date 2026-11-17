#!/bin/bash
# GED 식 영역 하위 구역 평균, 피험자 5명 (피험자당 약 15초). bash 로 실행.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/build_subroi_features.sh
set -euo pipefail
for s in 01 02 03 04 05; do
  OPENBLAS_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1 /pscratch/sd/s/sjmoon/tribev2/.venv/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/build_subroi_features.py --sub $s
done
