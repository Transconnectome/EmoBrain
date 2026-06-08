#!/bin/bash
# Scientific question: CLIP (pretrained + scratch) video model 의 stim feature 만으로
# 6 emotion task 를 어디까지 예측하는가? Brain conditioning 의 added value reference baseline.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_video_probe.py \
    --features CLIP_pretrained,CLIP_scratch \
    --out_csv results/phase1/video_probe_CLIP.csv \
    --summary_csv results/phase1/video_probe_CLIP_summary.csv
