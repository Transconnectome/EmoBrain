#!/bin/bash
# Phase 1 / A1-2, A1-3 stimulus and participant crosswalk.
# Requires p0_inventory to have written manifests/file_inventory.tsv.
# Decodes 2196 clips with 8 workers; about 5 minutes on a login node.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
"$PY" "$CODE/p1_stimulus_crosswalk.py" 2>&1 | tee "$LOGS/p1_stimulus_crosswalk.$(date -u +%Y%m%dT%H%M%SZ).log"
