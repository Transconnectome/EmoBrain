#!/bin/bash
# Scientific question: SwiFT NewE96 (resting + scratch init) 의 frozen embedding 이 6 emotion task 를 어떻게 capture 하는가?
# 2 init x 6 task x 2 mode x 2 head x 1 seed.  ~1-2h on 1 GPU.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --features SwiFT_NewE96 \
    --out_csv results/phase1/bfm_probe_SwiFT_NewE96.csv \
    --summary_csv results/phase1/bfm_probe_SwiFT_NewE96_summary.csv
