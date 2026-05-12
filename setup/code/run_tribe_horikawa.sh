#!/bin/bash
set -euo pipefail

ROOT=/pscratch/sd/s/sjmoon/FEELIN
PYTHON=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python

mkdir -p "${ROOT}/setup/logs"
mkdir -p "${ROOT}/setup/results/tribe_horikawa"
mkdir -p "${ROOT}/setup/results/tribe_cache"

export MPLCONFIGDIR=/tmp/matplotlib-feelin

cd "${ROOT}"

LOG="${ROOT}/setup/logs/tribe_horikawa_$(date +%Y%m%d_%H%M%S).log"
echo "Logging to ${LOG}"

"${PYTHON}" setup/code/run_tribe_horikawa.py \
  --all \
  --skip-heatmaps \
  --device auto \
  --cache-folder "${ROOT}/setup/results/tribe_cache" \
  --out-dir "${ROOT}/setup/results/tribe_horikawa" \
  "$@" 2>&1 | tee -a "${LOG}"
