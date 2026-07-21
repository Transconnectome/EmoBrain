#!/bin/bash
# Spatial resolution ladder on the tylee NIfTI volumes.
# Does finer spatial detail beat the 450-ROI ceiling (~0.31)?
# CPU-only, read-only on the source volumes. No sbatch.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/spatial_resolution_ladder.sh
#   bash .../spatial_resolution_ladder.sh sub-01 sub-02 sub-03

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/spatial_resolution_ladder.py" "$@"
