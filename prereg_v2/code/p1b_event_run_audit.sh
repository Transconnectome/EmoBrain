#!/bin/bash
# Phase 1 / A1-4 event and run audit. Parses the per-presentation sidecars
# under EmoViS/data/raw/step7_voxel. Read-only; about two minutes.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
"$PY" "$CODE/p1b_event_run_audit.py" 2>&1 | tee "$LOGS/p1b_event_run_audit.$(date -u +%Y%m%dT%H%M%SZ).log"
