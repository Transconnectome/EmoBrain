#!/bin/bash
# Training loop launcher (bash, CPU config). Not sbatch.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/training/train.sh <config.yaml>
#   default config = project/configs/trackA_e1_stub_cpu.yaml
#
# Pair. project/training/train.py
# The real Qwen run (GPU) uses a cuda config through sbatch (prior approval).

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate
CONFIG="${1:-${REPO_ROOT}/project/configs/trackA_e1_stub_cpu.yaml}"

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/training/train.py" --config "${CONFIG}"
