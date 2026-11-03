#!/bin/bash
# S1: HK 이상 block과 이상 run 목록 (0단계와 같은 정의, CPU, 피험자당 1~2분).
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11/s1_abnormal_blocks.py
