#!/bin/bash
# NeuroSTORM frozen probe: Arousal extreme binary. Padding=zero (main grid default).
# 2 init × 1 task × 2 mode × 2 head × 5 fold × 1 seed.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --config_set main \
    --features NeuroSTORM \
    --tasks A_binary \
    --out_csv results/phase1/bfm_probe_NeuroSTORM_A_binary.csv \
    --summary_csv results/phase1/bfm_probe_NeuroSTORM_A_binary_summary.csv
