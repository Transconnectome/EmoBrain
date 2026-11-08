#!/bin/bash
# Sanity check for supervised and structure losses.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/losses_smoke.sh
#
# Pair. project/scripts/losses_smoke.py

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/losses_smoke.py"
