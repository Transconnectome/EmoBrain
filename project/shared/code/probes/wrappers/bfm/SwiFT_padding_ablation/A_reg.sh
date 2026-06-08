#!/bin/bash
# Scientific question: Arousal continuous regression: frozen embedding 이 A intensity 의 gradient 를 잡는가.
# Model: SwiFT_padding_ablation (config_set=swift_padding_ablation).  Task: A_reg.
# 5 fold × 1 seed × 2 head × (mode if applicable).  ~30-60min on 1 GPU.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --config_set swift_padding_ablation \
    --features SwiFT_NewE96 \
    --tasks A_reg \
    --out_csv results/phase1/swift_padding_ablation_A_reg.csv \
    --summary_csv results/phase1/swift_padding_ablation_A_reg_summary.csv
