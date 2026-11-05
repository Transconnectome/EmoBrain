#!/bin/bash
# S3 저자 특징 대조. 가볍다. s3_collect 뒤에 돌린다. 사용: bash s3_author_check.sh
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python s3_author_check.py
