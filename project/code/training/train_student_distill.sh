#!/bin/bash
# Track B step 3 launcher (train_student_distill). Uses the Qwen env, sets
# HF_HOME, tees to project/output/<config>.log. GPU node required; user runs this.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/train_student_distill.sh <config.yaml>
set -uo pipefail
ROOT=/pscratch/sd/s/sjmoon/EmoBrain
export HF_HOME=/pscratch/sd/s/sjmoon/hf_cache
CFG="${1:?usage: train_student_distill.sh <config.yaml>}"
NAME=$(basename "$CFG" .yaml)
LOG="$ROOT/project/output/${NAME}.log"
mkdir -p "$ROOT/project/output"
cd "$ROOT"
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python -u \
    project/code/training/train_student_distill.py --config "$CFG" 2>&1 | tee "$LOG"
echo "[launcher] exit=${PIPESTATUS[0]}  log=$LOG"
