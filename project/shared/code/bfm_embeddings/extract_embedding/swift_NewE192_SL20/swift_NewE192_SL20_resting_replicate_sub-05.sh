#!/bin/bash
# EmoBrain SwiFT swift_NewE192_SL20 (resting / replicate / sub-05)
# Internal model_name: NewUAH_newE192  |  Output tag: NewE192_SL20
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain
mkdir -p output/logs

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/bfm_embeddings/_lib/swift.py \
    --model_name NewUAH_newE192 \
    --output_tag NewE192_SL20 \
    --init resting \
    --padding replicate \
    --subject sub-05 \
    --seed 0 \
    --batch_size 4 \
    --num_workers 2 \
    --out_root /pscratch/sd/s/sjmoon/EmoBrain/project/shared/output/embeddings
