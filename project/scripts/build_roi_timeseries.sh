#!/bin/bash
# Build ROI time-series pt files (per subject) from raw CSV time-series.
#
# Reads. /pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI/time_series/sub-XX/...
# Writes. project/shared/data/roi_timeseries/sub-XX.pt   (5 files, ~180 MB each)
#
# Pair. project/scripts/build_roi_timeseries.py
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/build_roi_timeseries.sh

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/build_roi_timeseries.py"
