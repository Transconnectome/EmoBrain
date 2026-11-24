#!/bin/bash
# EmoBrain SwiFT swift_NewE36_SL20 (scratch / replicate / sub-04)
# Internal model_name: NewUAH_newE36  |  Output tag: NewE36_SL20
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain
mkdir -p output/logs

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/bfm_embeddings/_lib/swift.py \
    --model_name NewUAH_newE36 \
    --output_tag NewE36_SL20 \
    --init scratch \
    --padding replicate \
    --subject sub-04 \
    --seed 0 \
    --batch_size 4 \
    --num_workers 2 \
    --out_root /pscratch/sd/s/sjmoon/EmoBrain/project/shared/output/embeddings
