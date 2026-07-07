#!/bin/bash
# Fit Cowen34Normalizer on the train split and save mu/std.
#
# Usage (bash on any node, no SLURM required for this quick preprocessing step).
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/labels_fit.sh
#
# Pair. project/scripts/labels_fit.py
#
# Reads.
#   project/shared/data/cowen_horikawa_labels.csv
#   project/shared/data/horikawa_split.csv
#
# Writes.
#   project/shared/data/norm_stats/cowen34_train.pt

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/labels_fit.py"
