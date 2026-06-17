#!/bin/bash
#SBATCH -A m4641
#SBATCH -C gpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH --gpus-per-node=4
#SBATCH -t 12:00:00
#SBATCH -J fmrilm_stage1
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/output/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/dir2_fmri_lm/output/logs/%x_%j.err
#
# D2 Stage 1. fMRI-LM 의 train_quantizer_contr.py wrapper.
# 인자 default 는 submodule 의 scripts/launch_train_quantizer_contr.sh 와 동일.
# 모델/loss/quantizer 변경은 사용자 의도 없이 하지 않음.
#
# 사용법.
#   환경변수로 dataset / desc / cfg override 가능.
#   기본은 official launch script 그대로.
#
# DO NOT sbatch without user approval.
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
DIR2=${REPO}/project/dir2_fmri_lm
FMRILM=${REPO}/external/repos/fMRI-LM

source /pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/activate

DATASET_DIR=${DATASET_DIR:-data/UKB/fmri/TianS3/,data/ABCD/fmri/TianS3/}
DESC_TYPE=${DESC_TYPE:-fc,ica}
CFG_PATH=${CFG_PATH:-configs/vit_small_gpt2_p160.yaml}
QUANTIZER=${QUANTIZER:-vq}

OUT=${DIR2}/output/stage1_$(date +%Y%m%d_%H%M%S)
mkdir -p "${OUT}" "${DIR2}/output/logs"

cd "${FMRILM}"

if [ -z "${CUDA_VISIBLE_DEVICES:-}" ]; then
    export NUM_GPUS=$(nvidia-smi --list-gpus | wc -l)
else
    export NUM_GPUS=$(echo $CUDA_VISIBLE_DEVICES | tr ',' '\n' | wc -l)
fi
export MASTER_PORT=$((RANDOM % (19000 - 11000 + 1) + 11000))
export MASTER_ADDR=localhost
export COUNT_NODE=1

accelerate launch \
    --num_processes=${NUM_GPUS} --num_machines=${COUNT_NODE} \
    --main_process_ip=${MASTER_ADDR} --main_process_port=${MASTER_PORT} \
    --mixed_precision=fp16 \
    train_quantizer_contr.py \
    --batch_size=12 \
    --epochs=50 \
    --dataset_dir=${DATASET_DIR} \
    --quantizer=${QUANTIZER} \
    --cfg_path=${CFG_PATH} \
    --contr_loss=soft_siglip \
    --fmri_pool_method=cls \
    --text_pool_method=last \
    --contr_weight=1.0 \
    --desc_type=${DESC_TYPE} \
    --domain_confuse_weight=0.5 \
    --ckpt_dir=${OUT}/ckpt

echo "[done] Stage 1 output at ${OUT}"
