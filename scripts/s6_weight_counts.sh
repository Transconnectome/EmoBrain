#!/bin/bash
# F8. 조건별 학습 가중치 수 표. ROI 표만 읽는다(CPU, 수 분). 사용: bash s6_weight_counts.sh 32,64,128
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=''
"$PY" s6_train.py --weight-counts "${1:?d 값}"
