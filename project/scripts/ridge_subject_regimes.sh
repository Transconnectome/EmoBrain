#!/bin/bash
# Ridge under 3 subject regimes: within / pooled / LOSO.
# Disambiguates whether ISC(0.23) < ridge(0.29) is signal-limited or label-anchored.
#
# CPU only, runs in a few minutes.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/ridge_subject_regimes.sh
#
# Pair. project/scripts/ridge_subject_regimes.py

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/ridge_subject_regimes.py"
