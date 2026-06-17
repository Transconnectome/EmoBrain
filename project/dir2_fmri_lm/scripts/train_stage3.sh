#!/bin/bash
#SBATCH -A m4641
#SBATCH -C gpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH --gpus-per-node=4
#SBATCH -t 12:00:00
#SBATCH -J fmrilm_stage3
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/output/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/output/logs/%x_%j.err
#
# D2 Stage 3. fMRI-LM 의 train_instruction.py wrapper.
# 인자 default 는 submodule 의 scripts/launch_train_instruction.sh 와 동일.
# Variant.
#   train_instruction.py            single-Q/A   (default)
#   train_instruction_mq.py         multi-Q/A
#   train_instruction_open_ended.py open-ended
# TRAIN_SCRIPT 환경변수로 변경.
#
# DO NOT sbatch without user approval.
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
DIR2=${REPO}/project/dir2_fmri_lm
FMRILM=${REPO}/external/repos/fMRI-LM

source /pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/activate

PRETRAINED_CKPT=${PRETRAINED_CKPT:-checkpoints/pretrain/UKB-robust/fc_ica_text0.1_f2t1_Qwen3-0.6B_lora_r1_a2_drop.1_qk_0415_143500/deepspeed_checkpoint_best_f2t/merged_checkpoint.pt}
CFG_PATH=${CFG_PATH:-configs/vit_base_p160.yaml}
LM_NAME=${LM_NAME:-Qwen/Qwen3-0.6B}
QUANTIZER=${QUANTIZER:-vq}
TRAIN_SCRIPT=${TRAIN_SCRIPT:-train_instruction.py}

OUT=${DIR2}/output/stage3_$(date +%Y%m%d_%H%M%S)
mkdir -p "${OUT}" "${DIR2}/output/logs"

cd "${FMRILM}"

export NUM_GPUS=${SLURM_GPUS_PER_NODE:-$(nvidia-smi --list-gpus | wc -l)}
export MASTER_PORT=$((RANDOM % (19000 - 11000 + 1) + 11000))
export MASTER_ADDR=localhost
export COUNT_NODE=1
export TOKENIZERS_PARALLELISM=false

accelerate launch \
    --num_processes=$((${NUM_GPUS} * ${COUNT_NODE})) --num_machines=${COUNT_NODE} \
    --main_process_ip=${MASTER_ADDR} --main_process_port=${MASTER_PORT} \
    --mixed_precision=bf16 \
    ${TRAIN_SCRIPT} \
    --ckpt_dir=${OUT}/ckpt \
    --lm_name=${LM_NAME} \
    --wandb_group=pretrained \
    --cfg_path=${CFG_PATH} \
    --gradient_accumulation_steps=8 \
    --epochs=30 \
    --quantizer=${QUANTIZER} \
    --add_src_info \
    --save_ckpt \
    --use_random_prompt \
    --use_allowed_tokens \
    --add_desc \
    --pretrained_ckpt=${PRETRAINED_CKPT}

echo "[done] Stage 3 output at ${OUT}"
