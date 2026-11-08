#!/bin/bash
# Track B step 2 launcher (cache_soft_labels). Uses the Qwen env, sets HF_HOME,
# tees to project/output/<config>.cache.log. GPU node required; user runs this.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/cache_soft_labels.sh <config.yaml>
set -uo pipefail
ROOT=/pscratch/sd/s/sjmoon/EmoBrain
export HF_HOME=/pscratch/sd/s/sjmoon/hf_cache
CFG="${1:?usage: cache_soft_labels.sh <config.yaml>}"
NAME=$(basename "$CFG" .yaml)
LOG="$ROOT/project/output/${NAME}.cache.log"
mkdir -p "$ROOT/project/output"
cd "$ROOT"
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python -u \
    project/code/training/cache_soft_labels.py --config "$CFG" 2>&1 | tee "$LOG"
echo "[launcher] exit=${PIPESTATUS[0]}  log=$LOG"
