#!/bin/bash
# Plot loss curve from HF Trainer state. Usage:
#   bash plot_loss_curve.sh <output_dir>
# 예시:
#   bash plot_loss_curve.sh /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/output/horikawa_emotion_cat34_top1_SMOKE
set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "USAGE: bash plot_loss_curve.sh <output_dir>"
    exit 1
fi

PYTHON=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
SELF_DIR="$(dirname "$(readlink -f "$0")")"

"$PYTHON" -u "$SELF_DIR/plot_loss_curve.py" --output-dir "$1"
