#!/bin/bash
# 조작 실험 결과를 정서 예측 변화로 정리 (원래 특징·조작 특징이 merge 된 뒤, CPU 수 분).
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/perturbation_readout.py
