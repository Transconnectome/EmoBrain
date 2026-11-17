#!/bin/bash
# 캡션 평가어의 영향 (평가어 지운 캡션과의 비교) 과 시각 특징의 평가어 예측 (자극 수준, CPU 수 분).
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/evaluative_words_test.py
