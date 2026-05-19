#!/bin/bash
# Padding ablation probe: sub-01 only, SwiftMLP (current baseline).
# Reproduces the original 72-row CSV (12 cells x 2 heads x 3 seeds).
set -e
cd /pscratch/sd/s/sjmoon/FEELIN

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/analysis/padding_ablation_probe.py \
    --subjects sub-01 \
    --mode single \
    --mlp_preset swift \
    --out_csv  results/padding_ablation/sub01_swift_probe.csv \
    --summary_csv results/padding_ablation/sub01_swift_summary.csv
