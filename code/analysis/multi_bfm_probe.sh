#!/bin/bash
# Multi-BFM probe: Brain-JEPA + NeuroSTORM only (SwiFT NewE96 already done).
# Padding = mean (= spatial-only control, all 20 frames = avg of T real frames).
# Expected: ~288 rows (2 models x previous 432/3), ~4-5h on single GPU.
# Combine with existing allsubj_pooled_swift_probe.csv + allsubj_persubj_swift_probe.csv
# for full 3-BFM comparison.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/analysis/multi_bfm_probe.py \
    --out_csv /pscratch/sd/s/sjmoon/FEELIN/results/background/main_grid_3bfm/probe_full.csv \
    --summary_csv /pscratch/sd/s/sjmoon/FEELIN/results/background/main_grid_3bfm/probe_summary.csv
