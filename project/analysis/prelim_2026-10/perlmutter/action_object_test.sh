#!/bin/bash
# 캡션의 동작 단어 대 물체 단어를 시각 특징으로 예측 (영상 모델의 시간 정보 확인, 자극 수준, CPU 수 분).
set -euo pipefail
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/action_object_test.py
