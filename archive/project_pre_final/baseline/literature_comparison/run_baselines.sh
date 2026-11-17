#!/bin/bash
# 공정 비교 baseline 묶음 실행. bash 로 실행. 인자: 모델(ridge|mlp|ged) [장치(cpu|cuda), GED 만]
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/run_baselines.sh ridge
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/run_baselines.sh mlp
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/run_baselines.sh ged cuda   (GPU 권장)
# 프로토콜 2개(ours, lit) × 입력(ridge·mlp: roi469·subroi4, ged: subroi4) × 피험자 5명. 피험자는 병렬, 나머지는 차례로.
set -euo pipefail
MODEL=$1; DEV=${2:-cpu}
PY=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
D=/pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison
LOG=$D/runs/logs; mkdir -p "$LOG"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
FEATS="roi469 subroi4"; [ "$MODEL" = "ged" ] && FEATS="subroi4"
for proto in ours lit; do
  for feat in $FEATS; do
    for s in 01 02 03 04 05; do
      "$PY" -u $D/run_baselines.py --protocol $proto --features $feat --model $MODEL --sub $s --device $DEV > "$LOG/${proto}_${feat}_${MODEL}_sub-$s.log" 2>&1 &
    done
    wait
  done
done
echo "$MODEL 완료"
