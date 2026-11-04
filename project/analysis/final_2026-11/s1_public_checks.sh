#!/bin/bash
# S1: 참가자별 voxel 수, 피질하 10개 정의, 원 논문 fold 배정, 이름표 73개와 34개 범주의 공개 파일 대조 (CPU, 수 초).
set -euo pipefail
PYTHONDONTWRITEBYTECODE=1 /pscratch/sd/s/sjmoon/tribev2/.venv/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11/s1_public_checks.py
