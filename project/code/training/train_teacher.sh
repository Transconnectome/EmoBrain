#!/bin/bash
# Track B step 1 launcher (train_teacher). Uses the Qwen env (transformers 4.57 +
# peft) the smoke confirmed, sets HF_HOME for offline Qwen3-VL, tees to
# project/output/<config>.log. GPU node required; user runs this.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/train_teacher.sh <config.yaml>
set -uo pipefail
ROOT=/pscratch/sd/s/sjmoon/EmoBrain
export HF_HOME=/pscratch/sd/s/sjmoon/hf_cache
CFG="${1:?usage: train_teacher.sh <config.yaml>}"
NAME=$(basename "$CFG" .yaml)
LOG="$ROOT/project/output/${NAME}.teacher.log"
mkdir -p "$ROOT/project/output"
cd "$ROOT"
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python -u \
    project/code/training/train_teacher.py --config "$CFG" 2>&1 | tee "$LOG"
echo "[launcher] exit=${PIPESTATUS[0]}  log=$LOG"
