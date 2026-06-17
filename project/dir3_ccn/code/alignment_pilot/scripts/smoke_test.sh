#!/bin/bash
# Local smoke test for the Direction 2 train_align pipeline.
# Runs on CPU with 50 samples + 1 epoch. No SLURM submission.
# Verifies the model + loss + data path are wired correctly.
set -euo pipefail

VENV=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
SCRIPT=/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/code/alignment_pilot/code/train/train_align.py
OUT=/tmp/dir2_smoke_$$

mkdir -p "$OUT"

"$VENV" "$SCRIPT" \
    --brain_variant resting \
    --fold 1 \
    --out_dir "$OUT" \
    --smoke

echo "===smoke test output:"
ls -la "$OUT"
head -50 "$OUT/history.json" 2>/dev/null || true
