#!/bin/bash
# Phase 0 / A1-1 dataset inventory. Read-only over the data; writes only into
# prereg_v2/manifests. Runs on a login node in about a minute.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
"$PY" "$CODE/p0_inventory.py" 2>&1 | tee "$LOGS/p0_inventory.$(date -u +%Y%m%dT%H%M%SZ).log"
