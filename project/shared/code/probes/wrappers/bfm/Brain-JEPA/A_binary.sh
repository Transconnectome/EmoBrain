#!/bin/bash
# Scientific question: Arousal extreme (Q4 vs Q1) binary classification 에서 frozen embedding 의 emotion-arousal discriminability.
# Model: Brain-JEPA (config_set=main).  Task: A_binary.
# 5 fold × 1 seed × 2 head × (mode if applicable).  ~30-60min on 1 GPU.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --config_set main \
    --features Brain-JEPA \
    --tasks A_binary \
    --out_csv results/phase1/bfm_probe_Brain-JEPA_A_binary.csv \
    --summary_csv results/phase1/bfm_probe_Brain-JEPA_A_binary_summary.csv
