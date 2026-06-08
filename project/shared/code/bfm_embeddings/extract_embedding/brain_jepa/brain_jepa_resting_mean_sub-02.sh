#!/bin/bash
# FEELIN Brain-JEPA (resting / mean / sub-02)
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
mkdir -p output/logs

source /pscratch/sd/s/sjmoon/brain-jepa-env/bin/activate

python code/bfm_embeddings/_lib/brain_jepa.py \
    --init resting \
    --padding mean \
    --subject sub-02 \
    --seed 0 \
    --batch_size 32 \
    --num_workers 4 \
    --attn_mode normal \
    --out_root /pscratch/sd/s/sjmoon/FEELIN/project/shared/output/embeddings
