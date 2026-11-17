#!/bin/bash
# 랩서버 표준 형식 특징 만들기 (Perlmutter login node, bash 로 실행). GPU 가 있으면 cuda, 없으면 cpu.
# bash /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/features/build_lab_features.sh
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
BUNDLE=/pscratch/sd/s/sjmoon/transfer/emobrain_stimulus_features_20261025
OUT=/pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026
DEVICE=$(nvidia-smi -L >/dev/null 2>&1 && echo cuda || echo cpu)
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
"$PY" /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/features/build_lab_features.py \
  --bundle "$BUNDLE" --out "$OUT" --device "$DEVICE"
