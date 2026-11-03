#!/bin/bash
# S1: 튀는 블록 5개와 sub-03 run 31~33의 FD, DVARS 비교 (CPU, 수 초).
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11/s1_abnormal_motion.py
