#!/bin/bash
# B1 baseline. Ridge regression fMRI ROI mean -> 34D emotion (NO LLM).
#
# CPU only, runs in minutes. No SLURM needed.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/train_baseline_ridge.sh
#
# Pair. project/training/train_baseline_ridge.py
# Output. project/shared/results/baseline/b1_ridge_metrics.json

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/training/train_baseline_ridge.py"
