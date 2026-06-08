#!/bin/bash
# BrainVLM training launch.
#
# Mode 1 (small sanity check): --smoke (50 train + 10 val, 1 epoch, ~10 min)
# Mode 2 (full fold 1 training): --epochs 3, no smoke, no eval (eval has upstream bug)
#
# Default = Mode 2 (full training).
# To run sanity check first:
#   bash code/brainvlm/train_brainvlm.sh smoke
#
# To run full:
#   bash code/brainvlm/train_brainvlm.sh full
set -e
cd /pscratch/sd/s/sjmoon/FEELIN

MODE=${1:-full}
LOG=/pscratch/sd/s/sjmoon/FEELIN/project/dir1_brainvlm/output/brainvlm_ckpt/${MODE}/train.log
mkdir -p $(dirname $LOG)

PY=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python

case $MODE in
  smoke)
    OUT=/pscratch/sd/s/sjmoon/FEELIN/project/dir1_brainvlm/output/brainvlm_ckpt/fold1_VA_smoke
    $PY code/brainvlm/train_brainvlm.py \
        --fold 1 \
        --smoke \
        --skip_eval \
        --output_dir $OUT \
        2>&1 | tee $LOG
    ;;
  full)
    OUT=/pscratch/sd/s/sjmoon/FEELIN/project/dir1_brainvlm/output/brainvlm_ckpt/fold1_VA_full
    $PY code/brainvlm/train_brainvlm.py \
        --fold 1 \
        --epochs 3 \
        --skip_eval \
        --output_dir $OUT \
        2>&1 | tee $LOG
    ;;
  *)
    echo "Unknown mode: $MODE. Use: smoke or full"
    exit 1
    ;;
esac

echo ""
echo "===== BrainVLM training done ($MODE) ====="
echo "Checkpoint: $OUT/final_model/"
echo "Log: $LOG"
