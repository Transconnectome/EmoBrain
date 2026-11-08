#!/bin/bash
# Compute Q1 / Q4 split for V/A binary classification task.
# Fit q25 / q75 on the train fold, assign labels to all stim.
# CPU only, ~10 sec.
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
SHARED=${REPO}/project/shared

source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

cd "${REPO}"
python -m project.shared.code.tools.va_quartile_split \
    --va-csv      "${SHARED}/data/va_continuous_z.csv" \
    --manifest-csv "${SHARED}/data/horikawa_5fold.csv" \
    --fold 1 \
    --out-csv     "${SHARED}/data/va_continuous_z.csv"

echo "[done] V/A quartile labels written to ${SHARED}/data/va_continuous_z.csv"
