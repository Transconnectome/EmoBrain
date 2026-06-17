#!/bin/bash
#SBATCH -A m4641
#SBATCH -C gpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH --gpus-per-node=4
#SBATCH -t 24:00:00
#SBATCH -J fmrilm_stage2
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/output/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/output/logs/%x_%j.err
#
# D2 Stage 2. fMRI-LM 의 train_pretrain_paired.py wrapper.
# 인자 default 는 submodule 의 scripts/launch_train_pretrain_paired_deepspeed.sh 와 동일.
# 모델/quantizer/LoRA 설정 변경은 사용자 의도 없이 하지 않음.
#
# DO NOT sbatch without user approval.
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
DIR2=${REPO}/project/dir2_fmri_lm
FMRILM=${REPO}/external/repos/fMRI-LM

source /pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/activate

TOKENIZER_PATH=${TOKENIZER_PATH:-checkpoints/tokenizer/UKB_robust/VQ_Align-ViT_base-p160/ckpt-best.pt}
DATASET_DIR=${DATASET_DIR:-data/UKB/fmri/TianS3/}
DESC_TYPE=${DESC_TYPE:-fc,ica}
CFG_PATH=${CFG_PATH:-configs/vit_base_p160.yaml}
LM_NAME=${LM_NAME:-Qwen/Qwen3-0.6B}
QUANTIZER=${QUANTIZER:-vq}

OUT=${DIR2}/output/stage2_$(date +%Y%m%d_%H%M%S)
mkdir -p "${OUT}" "${DIR2}/output/logs"

cd "${FMRILM}"

export NUM_GPUS=${SLURM_GPUS_PER_NODE:-$(nvidia-smi --list-gpus | wc -l)}
export MASTER_PORT=$((RANDOM % (19000 - 11000 + 1) + 11000))
export MASTER_ADDR=localhost
export COUNT_NODE=1
export TOKENIZERS_PARALLELISM=false
export DS_SKIP_CUDA_CHECK=1

accelerate launch \
    --num_processes=$((${NUM_GPUS} * ${COUNT_NODE})) --num_machines=${COUNT_NODE} \
    --main_process_ip=${MASTER_ADDR} --main_process_port=${MASTER_PORT} \
    --mixed_precision=bf16 \
    train_pretrain_paired.py \
    --tokenizer_path=${TOKENIZER_PATH} \
    --fmri_batch_size=4 \
    --gradient_accumulation_steps=8 \
    --epochs=30 \
    --desc_type=${DESC_TYPE} \
    --dataset_dir=${DATASET_DIR} \
    --cfg_path=${CFG_PATH} \
    --lm_name=${LM_NAME} \
    --text_only_weight=0.1 \
    --quantizer=${QUANTIZER} \
    --ckpt_postfix=lora_r1_a2_drop.1_qk \
    --deepspeed \
    --zero_stage=2 \
    --save_ckpt \
    --lora_target_modules=q_proj,k_proj \
    --lora_r=1 \
    --lora_alpha=2 \
    --lora_dropout=0.1 \
    --ckpt_dir=${OUT}/ckpt

echo "[done] Stage 2 output at ${OUT}"
