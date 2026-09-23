#!/bin/bash
# Phase 1. Magnitude of the repeat structure. Read-only; about a minute.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
"$PY" "$CODE/p1c_repeat_reliability.py" 2>&1 | tee "$LOGS/p1c_repeat_reliability.$(date -u +%Y%m%dT%H%M%SZ).log"
