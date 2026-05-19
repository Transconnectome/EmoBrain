#!/bin/bash
# Schaefer 17n400p + Tian S3 50 = 450 ROI mean BOLD feature 추출 (5 subjects).
# CPU 만 사용. 5분 미만 예상.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/extract_roi_features.py \
    --subjects sub-01,sub-02,sub-03,sub-04,sub-05 \
    --out_tag roi_schaefer400tian50_mean
