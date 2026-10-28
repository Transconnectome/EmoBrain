#!/bin/bash
# 감정어를 지운 사람 캡션 임베딩 (CPU 약 7분). bash 로 실행.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/features/build_caption_noemo.sh
set -euo pipefail
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OMP_NUM_THREADS=16 MKL_NUM_THREADS=16 PYTHONDONTWRITEBYTECODE=1
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/features/build_caption_noemo.py \
  --bundle /pscratch/sd/s/sjmoon/transfer/emobrain_stimulus_features_20261025 \
  --out /pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026 --device cpu
