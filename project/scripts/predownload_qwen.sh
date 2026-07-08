#!/bin/bash
# Pre-download the Qwen backbone on a LOGIN node (internet) into scratch HF cache.
# Run ONCE before submitting the GPU sbatch. Compute nodes are offline.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/predownload_qwen.sh
#   QWEN_MODEL=Qwen/Qwen2.5-1.5B-Instruct bash .../predownload_qwen.sh
#
# Pair. project/scripts/predownload_qwen.py

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate
export HF_HOME=/pscratch/sd/s/sjmoon/hf_cache

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/predownload_qwen.py"
