#!/bin/bash
# Local smoke test for D1 BrainVLM Path A.
# Verifies dataset -> patchify -> heads -> multi-task loss flow, NO backbone load.
# Run on login node (no GPU needed). ~2 min.
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
DIR1=${REPO}/project/dir1_brainvlm
SHARED=${REPO}/project/shared

source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

OUT=${DIR1}/output/smoke_$(date +%Y%m%d_%H%M%S)
mkdir -p "${OUT}"

cd "${REPO}"
python -m project.dir1_brainvlm.code.train.train_pilot \
    --out-dir "${OUT}" \
    --smoke 2>&1 | tee "${OUT}/smoke.log"

echo "[smoke] OK. output at ${OUT}"
