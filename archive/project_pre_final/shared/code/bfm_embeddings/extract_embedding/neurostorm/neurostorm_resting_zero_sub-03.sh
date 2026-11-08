#!/bin/bash
# EmoBrain NeuroSTORM (resting / zero / sub-03)
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain
mkdir -p output/logs

module load gcc-native/12 2>/dev/null || true
source /pscratch/sd/s/sjmoon/neurostorm_env/bin/activate

python code/bfm_embeddings/_lib/neurostorm.py \
    --init resting \
    --padding zero \
    --subject sub-03 \
    --seed 0 \
    --batch_size 8 \
    --num_workers 2 \
    --out_root /pscratch/sd/s/sjmoon/EmoBrain/project/shared/output/embeddings
