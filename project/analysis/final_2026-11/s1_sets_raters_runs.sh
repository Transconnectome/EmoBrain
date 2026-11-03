#!/bin/bash
# S1: 중복 15개 구성, 평정자 수 역산, MC run 구성, 8초 반복 종료 시점 (CPU, 수십 초).
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11/s1_sets_raters_runs.py
