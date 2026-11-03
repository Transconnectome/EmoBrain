#!/bin/bash
# S1: 34개 라벨 열 대조와 MC 최종 시험 72개 목록 (CPU, 수 초).
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11/s1_labels_mc72.py
