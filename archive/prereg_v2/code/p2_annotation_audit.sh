#!/bin/bash
# Phase 2 / A2-1 to A2-4 annotation audit. Read-only; under a minute.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
"$PY" "$CODE/p2_annotation_audit.py" 2>&1 | tee "$LOGS/p2_annotation_audit.$(date -u +%Y%m%dT%H%M%SZ).log"
