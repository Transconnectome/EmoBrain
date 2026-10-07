#!/bin/bash
# Phase 3 negative control. Shows whether the leakage assertion can fail.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
"$PY" "$CODE/p3b_leakage_negative_control.py" 2>&1 | tee "$LOGS/p3b_leakage_negative_control.$(date -u +%Y%m%dT%H%M%SZ).log"
