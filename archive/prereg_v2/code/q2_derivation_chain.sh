#!/bin/bash
# Preprocessing census q2. Derived ROI files against the q1 recomputation.
# Requires q1. Reads 21,960 csv.gz and the five .pt files; a few minutes.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
export OMP_NUM_THREADS=1
"$PY" "$CODE/q2_derivation_chain.py" 2>&1 | tee "$LOGS/q2_derivation_chain.$(date -u +%Y%m%dT%H%M%SZ).log"
