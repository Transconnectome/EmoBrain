#!/bin/bash
# Preprocessing census q3b. Presentation order versus content and annotation.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
"$PY" "$CODE/q3b_order_design_audit.py" 2>&1 | tee "$LOGS/q3b_order_design_audit.$(date -u +%Y%m%dT%H%M%SZ).log"
