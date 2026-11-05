#!/bin/bash
# S3 회귀 시험. 가볍다(CPU, 약 2분). 사용: bash s3_tests.sh
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 HF_HUB_OFFLINE=1
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s3_tests.py
