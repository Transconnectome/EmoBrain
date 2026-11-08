#!/bin/bash
# Scientific question: NeuroSTORM (resting + scratch) frozen embedding 의 6 emotion task capture 능력은?
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --features NeuroSTORM \
    --out_csv results/phase1/bfm_probe_NeuroSTORM.csv \
    --summary_csv results/phase1/bfm_probe_NeuroSTORM_summary.csv
