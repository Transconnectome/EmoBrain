#!/bin/bash
# No-LLM cheap fusion baseline + floor / leakage controls.
# CPU-fine, uses a GPU if visible. Env has sklearn/scipy/torch/pandas.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/cheap_fusion_and_floor.sh
set -uo pipefail
cd /pscratch/sd/s/sjmoon/EmoBrain
PY=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
export PYTHONUNBUFFERED=1
LOG=project/output/cheap_fusion_and_floor.log
mkdir -p project/output
"$PY" project/scripts/cheap_fusion_and_floor.py 2>&1 | tee "$LOG"
