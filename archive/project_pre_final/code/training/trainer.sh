#!/bin/bash
# Config-driven trainer launcher (spec §8-2). Sets HF_HOME so Qwen3-VL / ViT load
# offline-safe from the scratch cache. CPU stub configs run anywhere; qwen configs
# need a GPU. Sbatch requires prior approval.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/trainer.sh <config.yaml>

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate
export HF_HOME=/pscratch/sd/s/sjmoon/hf_cache

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/code/training/trainer.py" --config "${1:?config.yaml required}"
