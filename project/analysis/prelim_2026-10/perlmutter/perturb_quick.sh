#!/bin/bash
# 채도·밝기 조작 빠른 확인판 (영상 약 80개 × 조작 9개, CLIP·DINOv2, CPU 20~40분).
set -euo pipefail
export HF_HOME=/pscratch/sd/s/sjmoon/.cache/huggingface HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 CUDA_VISIBLE_DEVICES=""
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/perturb_quick.py "$@"
