#!/bin/bash
# Scientific question: SwiFT NewE96 의 cyclic_replicate padding 이 last-frame replicate / mean / zero / spatial_only 대비 Arousal continuous regression 에 도움 되나?
# 1 padding (cyclic_replicate) × 2 init × 1 task × 2 mode × 2 head × 5 fold × 1 seed = 80 fit.  ~30-60min on 1 GPU.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/probes/run_unified_probe.py \
    --config_set swift_padding_cyclic_only \
    --features SwiFT_NewE96 \
    --tasks A_reg \
    --out_csv results/phase1/swift_padding_cyclic_only_A_reg.csv \
    --summary_csv results/phase1/swift_padding_cyclic_only_A_reg_summary.csv
