#!/bin/bash
# Padding ablation probe: 5 subjects POOLED into single train/val/test.
# Tests "universal emotion code" hypothesis (cross-subject shared representation).
# train ~ 8740 samples per (init,pad,task) cell. Requires sub-02..05 .pt extracted.
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/analysis/padding_ablation_probe.py \
    --subjects sub-01,sub-02,sub-03,sub-04,sub-05 \
    --mode pooled \
    --mlp_preset swift \
    --out_csv  results/padding_ablation/allsubj_pooled_swift_probe.csv \
    --summary_csv results/padding_ablation/allsubj_pooled_swift_summary.csv
