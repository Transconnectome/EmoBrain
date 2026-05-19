#!/bin/bash
# FEELIN SwiFT swift_UAH_806M_SL20 (scratch / replicate / sub-03)
# Internal model_name: UAH_P3_806M  |  Output tag: UAH_806M_SL20
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
mkdir -p output/logs

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/bfm_embeddings/_lib/swift.py \
    --model_name UAH_P3_806M \
    --output_tag UAH_806M_SL20 \
    --init scratch \
    --padding replicate \
    --subject sub-03 \
    --seed 0 \
    --batch_size 4 \
    --num_workers 2 \
    --out_root /pscratch/sd/s/sjmoon/FEELIN/output/embeddings
