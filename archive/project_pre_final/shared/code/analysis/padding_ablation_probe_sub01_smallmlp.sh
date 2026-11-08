#!/bin/bash
# Padding ablation probe: sub-01 only, SmallMLP (shrunken head test).
# Tests whether smaller MLP (0.7M params vs 9.4M) fixes overfit on n~900.
# Sub-01 only; reuses existing 6 .pt files. Linear results identical to swift baseline.
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/analysis/padding_ablation_probe.py \
    --subjects sub-01 \
    --mode single \
    --mlp_preset small \
    --out_csv  results/padding_ablation/sub01_smallmlp_probe.csv \
    --summary_csv results/padding_ablation/sub01_smallmlp_summary.csv
