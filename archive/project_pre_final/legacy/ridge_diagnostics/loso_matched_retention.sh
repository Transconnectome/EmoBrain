#!/bin/bash
# Fair cross-subject retention with matched training-set size.
# Removes the n_train confound (within 1748 vs LOSO 6992) that made weak
# representations show retention > 1.0 in the first LOSO comparison.
# CPU-only, read-only (writes one JSON report). No sbatch.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/loso_matched_retention.sh
#   bash .../loso_matched_retention.sh all
#   bash .../loso_matched_retention.sh roi_schaefer400tian50_mean brain_jepa_resting_pad-zero

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/loso_matched_retention.py" "$@"
