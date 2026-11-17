#!/bin/bash
# Stage 0 emotion-space decoding noise ceiling (critic-revised).
# CPU-only (ridge + kernel ridge on 5 subjects). Run on a login/interactive
# shell; no sbatch. Pairs with project/scripts/stage0_decoding_ceiling.py.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/stage0_decoding_ceiling.sh

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/stage0_decoding_ceiling.py"
