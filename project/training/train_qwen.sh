#!/bin/bash
# Bash launcher for Qwen runs (smoke or full). Sets HF_HOME to the scratch cache
# where predownload_qwen.sh stored the model, so the model loads offline-safe.
# Use this (not the generic train.sh) for any qwen-backbone config.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/training/train_qwen.sh [config.yaml]
#   default config = trackA_e1_qwen_gpusmoke.yaml
#
# Pair. project/training/train.py

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate
export HF_HOME=/pscratch/sd/s/sjmoon/hf_cache
CONFIG="${1:-${REPO_ROOT}/project/configs/trackA_e1_qwen_gpusmoke.yaml}"

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/training/train.py" --config "${CONFIG}"
