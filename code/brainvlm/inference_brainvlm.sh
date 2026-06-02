#!/bin/bash
# BrainVLM inference on fold 1 test set.
# Generates V/A predictions for all 5 subj × 437 test stim = 2,185 total.
# Wall time estimate: ~30-60 min (1 GPU, greedy decoding, max 128 new tokens).
#
# Usage:
#   bash code/brainvlm/inference_brainvlm.sh             # full test fold (2,185 samples)
#   bash code/brainvlm/inference_brainvlm.sh smoke       # 10 samples / subj (50 total)
set -e
cd /pscratch/sd/s/sjmoon/FEELIN

MODE=${1:-full}
CKPT=/pscratch/sd/s/sjmoon/FEELIN/output/brainvlm_ckpt/fold1_VA_full/final_model
OUT_DIR=/pscratch/sd/s/sjmoon/FEELIN/results/brainvlm
mkdir -p $OUT_DIR $OUT_DIR/logs

PY=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python

case $MODE in
  smoke)
    OUT=$OUT_DIR/fold1_test_preds_smoke.csv
    LOG=$OUT_DIR/logs/inference_smoke.log
    $PY -u code/brainvlm/inference_brainvlm.py \
        --fold 1 --ckpt $CKPT --out_csv $OUT --limit 10 \
        2>&1 | tee $LOG
    ;;
  full)
    OUT=$OUT_DIR/fold1_test_preds.csv
    LOG=$OUT_DIR/logs/inference_full.log
    $PY -u code/brainvlm/inference_brainvlm.py \
        --fold 1 --ckpt $CKPT --out_csv $OUT \
        2>&1 | tee $LOG
    ;;
  *)
    echo "Unknown mode: $MODE. Use: smoke | full"
    exit 1
    ;;
esac

echo ""
echo "===== BrainVLM inference done ($MODE) ====="
echo "Predictions CSV: $OUT"
echo "Metrics CSV:     ${OUT%.csv}_metrics.csv"
echo "Log:             $LOG"
