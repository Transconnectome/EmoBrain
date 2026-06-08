#!/bin/bash
# Scientific question: Qwen-VL 이 생성한 caption 의 text embedding 으로 6 emotion task 예측?
# Language-grounded video understanding 의 emotion 표상 능력.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_video_probe.py \
    --features Qwen-VL_caption \
    --out_csv results/phase1/video_probe_Qwen-VL_caption.csv \
    --summary_csv results/phase1/video_probe_Qwen-VL_caption_summary.csv
