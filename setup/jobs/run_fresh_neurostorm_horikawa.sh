#!/bin/bash
set -euo pipefail

source /pscratch/sd/s/sjmoon/neurostorm_env/bin/activate
cd /pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/NeuroSTORM

python run_embedding_extraction_horikawa.py \
  --data_root /pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs \
  --output_dir /pscratch/sd/s/sjmoon/NetFeeliX/setup/results/fresh_embeddings/horikawa/neurostorm \
  --ckpt_path /pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/NeuroSTORM/output/neurostorm/pt_neurostorm_mae_ratio0.5.ckpt \
  --embed_dim 36 \
  --batch_size 16 \
  --num_workers 8 \
  --device cuda
