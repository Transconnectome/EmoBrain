#!/bin/bash
set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate
python3 "${REPO_ROOT}/project/scripts/import_corrected_brain_jepa.py" "$@"
