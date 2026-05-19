#!/bin/bash
# FEELIN NeuroSTORM (scratch / mean / sub-03)
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
mkdir -p output/logs

module load gcc-native/12 2>/dev/null || true
source /pscratch/sd/s/sjmoon/neurostorm_env/bin/activate

python code/bfm_embeddings/_lib/neurostorm.py \
    --init scratch \
    --padding mean \
    --subject sub-03 \
    --seed 0 \
    --batch_size 8 \
    --num_workers 2 \
    --out_root /pscratch/sd/s/sjmoon/FEELIN/output/embeddings
