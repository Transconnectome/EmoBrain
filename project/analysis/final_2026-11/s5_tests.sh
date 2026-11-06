#!/bin/bash
# S5 합성 자료 시험. 실제 정답, 실제 뇌 반응은 읽지 않는다. 사용: bash s5_tests.sh
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=''
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s5_tests.py
