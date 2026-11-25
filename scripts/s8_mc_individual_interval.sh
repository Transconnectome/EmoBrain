#!/bin/bash
# MC 개인 모델 예측의 bootstrap 구간(src/s8_mc_individual_interval.py). GPU 없음, CPU 16 thread로 20분쯤.
# 사용(레포 최상위): bash scripts/s8_mc_individual_interval.sh <s6_brain_final_for_mc> <s8_mc> <s8_mc_individual> <perturb 폴더>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=16 MKL_NUM_THREADS=16
cd "$ROOT/src"
"$PY" -W ignore s8_mc_individual_interval.py --final "${1:?final_for_mc}" --transfer "${2:?s8_mc}" --individual "${3:?s8_mc_individual}" --out "${4:?perturb 폴더}"
