#!/bin/bash
# Unified frozen probe (Tier 1 ROI mean + Tier 2 BFM, V/A binary).
# 7 feature x 2 task x 2 mode x 2 head x 3 seed = ~1680 row.
# 단일 GPU sequential ~8-10h. overnight 적합.
# Linear 만 빠르게 보고 싶으면 --skip_mlp 추가.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --out_csv /pscratch/sd/s/sjmoon/FEELIN/results/phase1/unified_probe.csv \
    --summary_csv /pscratch/sd/s/sjmoon/FEELIN/results/phase1/unified_probe_summary.csv
