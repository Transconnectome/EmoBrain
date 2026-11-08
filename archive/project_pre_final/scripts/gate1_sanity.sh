#!/bin/bash
# Phase 0 / Gate 1 — same-dataset sanity: does the brain-only label-query decoder
# clear linear ridge (0.294) on the same roi_mean input? Also runs the query
# ablation (semantic-residual / semantic-frozen / free). Small model, GPU if visible.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/gate1_sanity.sh
set -uo pipefail
cd /pscratch/sd/s/sjmoon/EmoBrain
export PYTHONUNBUFFERED=1
LOG=project/output/gate1_sanity.log
mkdir -p project/output
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python \
    project/scripts/gate1_sanity.py 2>&1 | tee "$LOG"
echo "[launcher] exit=${PIPESTATUS[0]}  log=$LOG"
