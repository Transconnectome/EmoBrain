#!/bin/bash
# 시각 특징과 캡션 특징의 겹침 (CKA·RSA, 서로 예측, 정서 예측 분산 분할). 자극 수준, CPU.
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/feature_overlap.py
