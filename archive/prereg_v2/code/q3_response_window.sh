#!/bin/bash
# Preprocessing census q3. Label-blind comparison of response windows.
# Requires q1 (qc/roi_runs). A few minutes.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
export OMP_NUM_THREADS=8
"$PY" "$CODE/q3_response_window.py" 2>&1 | tee "$LOGS/q3_response_window.$(date -u +%Y%m%dT%H%M%SZ).log"
