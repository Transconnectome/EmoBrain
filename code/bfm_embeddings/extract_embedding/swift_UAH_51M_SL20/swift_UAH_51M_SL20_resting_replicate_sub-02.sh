#!/bin/bash
# FEELIN SwiFT swift_UAH_51M_SL20 (resting / replicate / sub-02)
# Internal model_name: UAH_P2_51M  |  Output tag: UAH_51M_SL20
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
mkdir -p output/logs

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/bfm_embeddings/_lib/swift.py \
    --model_name UAH_P2_51M \
    --output_tag UAH_51M_SL20 \
    --init resting \
    --padding replicate \
    --subject sub-02 \
    --seed 0 \
    --batch_size 4 \
    --num_workers 2 \
    --out_root /pscratch/sd/s/sjmoon/FEELIN/output/embeddings
