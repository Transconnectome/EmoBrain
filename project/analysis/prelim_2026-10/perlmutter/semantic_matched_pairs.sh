#!/bin/bash
# 의미를 맞춘 영상 쌍 분석 (34개 감정, 저수준·층별 시각 특징, 자극 수준, CPU 10~20분). build_lowlevel_motion.sh 를 먼저 돌린다.
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/semantic_matched_pairs.py
