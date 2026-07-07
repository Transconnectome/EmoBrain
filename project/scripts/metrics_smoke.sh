#!/bin/bash
# Sanity check for evaluation metrics.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/metrics_smoke.sh
#
# Pair. project/scripts/metrics_smoke.py

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/metrics_smoke.py"
