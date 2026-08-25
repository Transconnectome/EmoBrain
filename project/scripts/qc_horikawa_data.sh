#!/bin/bash
# QC / QA of the Horikawa preprocessed data (ROI timeseries, MNI volumes, raw).
# CPU-only, read-only (writes one JSON report). No sbatch.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/qc_horikawa_data.sh

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/qc_horikawa_data.py"
