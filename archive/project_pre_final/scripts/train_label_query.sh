#!/bin/bash
# LLM-free label-query decoder: brain-only + 3-modal, head-to-head vs ridge/LLM.
# Tiny model (~3.8M params), CPU-fine, uses a GPU if visible.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/train_label_query.sh
set -uo pipefail
cd /pscratch/sd/s/sjmoon/EmoBrain
PY=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
export PYTHONUNBUFFERED=1
LOG=project/output/label_query_decoder.log
mkdir -p project/output
"$PY" project/scripts/train_label_query.py 2>&1 | tee "$LOG"
