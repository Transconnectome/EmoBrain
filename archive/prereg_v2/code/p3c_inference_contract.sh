#!/bin/bash
# Phase 3 / A3-4 inference contract and Phase 0 / A0-2 environment lock.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
"$PY" "$CODE/p3c_inference_contract.py" 2>&1 | tee "$LOGS/p3c_inference_contract.$(date -u +%Y%m%dT%H%M%SZ).log"
