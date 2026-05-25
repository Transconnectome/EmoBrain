#!/bin/bash
# Scientific question: Brain-JEPA (resting + scratch) frozen embedding 의 6 emotion task capture 능력은?
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --features Brain-JEPA \
    --out_csv results/phase1/bfm_probe_Brain-JEPA.csv \
    --summary_csv results/phase1/bfm_probe_Brain-JEPA_summary.csv
