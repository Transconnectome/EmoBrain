#!/bin/bash
# LLM-free label-query (Query2Label) decoder on Horikawa. The decisive
# "is the LLM worth it" test. CPU-fine, uses a GPU if visible.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/label_query_decoder.sh
set -uo pipefail
cd /pscratch/sd/s/sjmoon/EmoBrain
PY=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
export PYTHONUNBUFFERED=1
LOG=project/output/label_query_decoder.log
mkdir -p project/output
"$PY" project/scripts/label_query_decoder.py 2>&1 | tee "$LOG"
