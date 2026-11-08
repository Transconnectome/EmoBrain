#!/bin/bash
# Measure brain cross-subject ISC (noise ceiling estimator).
#
# CPU only, runs in minutes.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/measure_brain_isc.sh
#
# Pair. project/scripts/measure_brain_isc.py
# Output. project/shared/results/noise_ceiling/brain_isc.json

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/measure_brain_isc.py"
