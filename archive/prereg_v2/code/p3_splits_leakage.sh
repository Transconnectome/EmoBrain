#!/bin/bash
# Phase 3 / A3-1, A3-2, A3-4 splits and leakage tests.
# Requires p0 and p1 manifests. Read-only over the data; about a minute.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
"$PY" "$CODE/p3_splits_leakage.py" 2>&1 | tee "$LOGS/p3_splits_leakage.$(date -u +%Y%m%dT%H%M%SZ).log"
