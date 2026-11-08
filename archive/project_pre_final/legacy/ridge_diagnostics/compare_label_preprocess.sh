#!/bin/bash
# Compare 3 label preprocessing schemes on B1 ridge (decision experiment).
#   zscore | log1p_z | zscore_clip
#
# CPU only, runs in minutes.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/compare_label_preprocess.sh
#
# Pair. project/scripts/compare_label_preprocess.py

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/compare_label_preprocess.py"
