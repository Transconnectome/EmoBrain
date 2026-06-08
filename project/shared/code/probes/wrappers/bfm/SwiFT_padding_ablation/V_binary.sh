#!/bin/bash
# Scientific question: Valence extreme (Q4 vs Q1) binary classification 에서 frozen embedding 의 emotion-valence discriminability.
# Model: SwiFT_padding_ablation (config_set=swift_padding_ablation).  Task: V_binary.
# 5 fold × 1 seed × 2 head × (mode if applicable).  ~30-60min on 1 GPU.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --config_set swift_padding_ablation \
    --features SwiFT_NewE96 \
    --tasks V_binary \
    --out_csv results/phase1/swift_padding_ablation_V_binary.csv \
    --summary_csv results/phase1/swift_padding_ablation_V_binary_summary.csv
