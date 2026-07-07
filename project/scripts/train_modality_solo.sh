#!/bin/bash
# B2 baseline. Single-modality ridge to 34D (brain / video / caption).
#
# CPU only, runs in minutes.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/train_modality_solo.sh
#
# Pair. project/training/train_modality_solo.py
# Output. project/shared/results/baseline/b2_modality_solo.json

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/training/train_modality_solo.py"
