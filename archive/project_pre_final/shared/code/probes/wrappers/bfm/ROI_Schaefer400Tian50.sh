#!/bin/bash
# Scientific question: ROI Schaefer 400 + Tian S3 50 의 mean BOLD feature 가 6 emotion task 의 floor 를 어디까지 잡는가?
# 4 task (linear) + 4 task (MLP) on 1 feature x 2 mode x 1 seed.  ~30 min on 1 GPU.
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --features ROI_Schaefer400Tian50 \
    --out_csv results/phase1/bfm_probe_ROI_Schaefer400Tian50.csv \
    --summary_csv results/phase1/bfm_probe_ROI_Schaefer400Tian50_summary.csv
