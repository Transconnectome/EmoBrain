#!/bin/bash
set -euo pipefail

source /pscratch/sd/s/sjmoon/brain-jepa-env/bin/activate
cd /pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/Brain-JEPA

python run_embedding_extraction_horikawa.py \
  --data_root_dir /pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_preprocess_JEPA_ROI \
  --output_dir /pscratch/sd/s/sjmoon/NetFeeliX/setup/results/fresh_embeddings/horikawa/brain_jepa \
  --mni_data_root /pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img \
  --finetune /pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/Brain-JEPA/pretrained_models/jepa-ep300.pth \
  --model_name vit_base \
  --crop_size 450,20 \
  --patch_size 16 \
  --attn_mode normal \
  --add_w mapping \
  --batch_size 64 \
  --num_workers 8 \
  --device cuda
