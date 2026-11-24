#!/bin/bash
# Sanity check for HorikawaDataset (pooled 5-subject × 2185-stim).
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/datasets_smoke.sh
#
# Pair. project/scripts/datasets_smoke.py

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/datasets_smoke.py"
