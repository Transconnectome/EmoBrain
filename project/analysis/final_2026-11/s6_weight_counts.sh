#!/bin/bash
# F8. 조건별 학습 가중치 수 표. ROI 표만 읽는다(CPU, 수 분). 사용: bash s6_weight_counts.sh 32,64,128
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=''
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s6_train.py --weight-counts "${1:?d 값}"
