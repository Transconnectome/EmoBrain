#!/bin/bash
set -euo pipefail

cd /pscratch/sd/s/sjmoon/SwiFT_v2

module load python
module load cpe/23.03
conda activate /global/common/software/m4750/swift_PTL2

export MASTER_ADDR=$(/bin/hostname -s)
export MASTER_PORT=29600

CKPT_PATH=/pscratch/sd/j/jubchoi/Newdata_Phase3_MR0p6/UAH_P2_51M_MR_0p6_L1e-4/best.pt
IMAGE_PATH=/pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs
SPLIT_FILE=/pscratch/sd/s/sjmoon/EmoDe/Foundation_baseline/SwiFT_v2/data/splits/Horikawa/pretraining/split_fixed_0_all.txt

python project/main_embedding_extraction.py \
  --accelerator gpu --max_epochs 60 --precision 32 --num_nodes 1 --devices 1 --strategy deepspeed_stage_1 \
  --loggername neptune --classifier_module v6 --dataset_name Horikawa --image_path ${IMAGE_PATH} --num_workers 8 \
  --project_name seokjin14/SwiFT-EMBEDDING \
  --c_multiplier 2 --last_layer_full_MSA True --clf_head_version v1 --downstream_task arousal --train_split 0.7 --val_split 0.15 --grad_clip --use_scheduler --gamma 0.5 --cycle 0.5 --use_MuTransfer \
  --extract_embeddings --test_only --test_ckpt_path ${CKPT_PATH} --load_ds_ckpt_manually --eval_batch_size 1 --embedding_save_dir /pscratch/sd/s/sjmoon/FEELIN/setup/results/fresh_embeddings/horikawa/swift_v2/raw --split_file_path ${SPLIT_FILE} \
  --batch_size 16 --dataset_split_num 0 --seed 1 --learning_rate 7e-5 --model simmim_swin4d_ver9 --depth 2 2 18 2 --num_heads 6 12 24 48 \
  --embed_dim 96 --first_window_size 4 4 4 4 --window_size 4 4 4 20 --sequence_length 20 --img_size 96 96 96 20 --use_mim --patch_size 6 6 6 2 --mask_patch_size 6 6 6 2 --mask_ratio 0.8 --input_scaling_method znorm_minback

/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python /pscratch/sd/s/sjmoon/SwiFT_v2/downstream_optuna/pooling_extracted_embeddings.py \
  --input_dir /pscratch/sd/s/sjmoon/FEELIN/setup/results/fresh_embeddings/horikawa/swift_v2/raw \
  --output_dir /pscratch/sd/s/sjmoon/FEELIN/setup/results/fresh_embeddings/horikawa/swift_v2/pooled \
  --flat_structure \
  --max_jobs 8
