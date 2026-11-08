#!/bin/bash
# 색·밝기·선명도·움직임 저수준 특징 28개 (영상 2196개, CPU 10분 안팎).
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/features/build_lowlevel_motion.py "$@"
