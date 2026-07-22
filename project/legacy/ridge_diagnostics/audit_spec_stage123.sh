#!/bin/bash
# Audit spec build steps 1-3 against implementation_spec_20260702 Acceptance.
# CPU-only, read-only (writes one JSON report). No sbatch.
#
# Usage.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/audit_spec_stage123.sh

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/scripts/audit_spec_stage123.py"
