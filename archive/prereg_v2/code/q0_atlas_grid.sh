#!/bin/bash
# Preprocessing census q0. Atlas on the fMRI grid. Seconds.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
"$PY" "$CODE/q0_atlas_grid.py" 2>&1 | tee "$LOGS/q0_atlas_grid.$(date -u +%Y%m%dT%H%M%SZ).log"
