#!/bin/bash
# Track B launcher (cache_soft_labels). HF_HOME set for offline Qwen3-VL. Sbatch needs approval.
set -euo pipefail
REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
export HF_HOME=/pscratch/sd/s/sjmoon/hf_cache
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate
python3 "${REPO_ROOT}/project/code/training/cache_soft_labels.py" --config "${1:?config.yaml required}"
