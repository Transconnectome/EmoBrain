#!/bin/bash
# 시각 모델 임베딩(CLIP, DINOv2, VideoMAE)을 표준 형식으로 (몇 초). bash 로 실행.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/features/build_vision_features.sh
set -euo pipefail
PYTHONDONTWRITEBYTECODE=1 /pscratch/sd/s/sjmoon/tribev2/.venv/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/features/build_vision_features.py \
  --bundle /pscratch/sd/s/sjmoon/transfer/emobrain_stimulus_features_20261025 --out /pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026
