#!/bin/bash
# FEELIN SwiFT swift_NewE96_SL20 (resting / mean / sub-05)
# Internal model_name: NewUAH_newE96  |  Output tag: NewE96_SL20
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
mkdir -p output/logs

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/bfm_embeddings/_lib/swift.py \
    --model_name NewUAH_newE96 \
    --output_tag NewE96_SL20 \
    --init resting \
    --padding mean \
    --subject sub-05 \
    --seed 0 \
    --batch_size 4 \
    --num_workers 2 \
    --out_root /pscratch/sd/s/sjmoon/FEELIN/output/embeddings
