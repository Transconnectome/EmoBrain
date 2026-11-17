#!/bin/bash
# Qwen3-VL training launcher. Uses the Qwen env (transformers 4.57 + peft) the
# smoke confirmed, sets HF_HOME, and tees all output to project/output/<config>.log
# so the run is inspectable without pasting stdout. GPU node required.
#
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/code/training/run_qwen3vl.sh <config.yaml>
set -uo pipefail
ROOT=/pscratch/sd/s/sjmoon/EmoBrain
export HF_HOME=/pscratch/sd/s/sjmoon/hf_cache
CFG="${1:?usage: run_qwen3vl.sh <config.yaml>}"
NAME=$(basename "$CFG" .yaml)
LOG="$ROOT/project/output/${NAME}.log"
mkdir -p "$ROOT/project/output"
cd "$ROOT"
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python -u \
    project/code/training/trainer.py --config "$CFG" 2>&1 | tee "$LOG"
echo "[launcher] exit=${PIPESTATUS[0]}  log=$LOG"
