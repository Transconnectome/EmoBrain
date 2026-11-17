#!/bin/bash
# 학습 자료 양의 효과: run 묶음을 유지한 채 fold 수를 늘린 분할(ours10 = 학습 약 90%, ours46 = 약 98%)에서 ridge·MLP (469개 영역 평균).
# ours (6겹, 83%) 결과는 run_baselines.sh 가 만든다. bash 로 실행.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison/run_foldsize.sh
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
D=/pscratch/sd/s/sjmoon/EmoBrain/project/baseline/literature_comparison
LOG=$D/runs/logs; mkdir -p "$LOG"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONDONTWRITEBYTECODE=1
for proto in ours10 ours46; do
  for model in ridge mlp; do
    for s in 01 02 03 04 05; do
      "$PY" -u $D/run_baselines.py --protocol $proto --features roi469 --model $model --sub $s > "$LOG/${proto}_roi469_${model}_sub-$s.log" 2>&1 &
    done
  done
  wait
done
echo "fold 수 비교 완료"
