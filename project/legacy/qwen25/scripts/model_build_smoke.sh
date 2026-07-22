#!/bin/bash
# CPU wiring smoke for the swappable model skeleton.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/model_build_smoke.sh
#
# Pair. project/scripts/model_build_smoke.py
# CPU only, no downloads (stub backbone). Not an sbatch job.

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/model_build_smoke.py"
