#!/bin/bash
# Scientific question: 각 task 의 feature-free chance level 은? (DummyClassifier stratified / most_frequent,
# DummyRegressor mean / median). 이게 모든 BFM/Video/ROI 결과의 absolute floor 가 됨.
# 6 task x (2 head for cls / 1-2 head for reg) x 5 fold x (3 seed for stratified, 1 for deterministic).  ~1 min.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_chance_baseline.py \
    --out_csv results/phase1/chance_baseline.csv \
    --summary_csv results/phase1/chance_baseline_summary.csv
