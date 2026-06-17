#!/bin/bash
# Padding ablation probe: 5 subjects PER-SUBJECT (5 separate models, mean ± std).
# Tests "subject-level generalization" of representation.
# train ~ 1748 samples per subject. Requires sub-02..05 .pt extracted.
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/analysis/padding_ablation_probe.py \
    --subjects sub-01,sub-02,sub-03,sub-04,sub-05 \
    --mode per_subject \
    --mlp_preset swift \
    --out_csv  results/padding_ablation/allsubj_persubj_swift_probe.csv \
    --summary_csv results/padding_ablation/allsubj_persubj_swift_summary.csv
