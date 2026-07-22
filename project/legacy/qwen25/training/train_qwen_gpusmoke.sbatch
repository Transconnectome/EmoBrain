#!/bin/bash
# GPU SMOKE for the E1 + text-Qwen path (first real-LLM run, tiny).
# Submit AFTER predownload_qwen.sh has cached the model on a login node.
#
# Submit.
#   sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/training/train_qwen_gpusmoke.sbatch
#
# CONFIRM the 3 NERSC-specific lines below (account / QOS / gpus) against your
# known-good Perlmutter GPU header before submitting.
#SBATCH -A m4641_g          # CONFIRM: Perlmutter GPU allocation (project + _g)
#SBATCH -C gpu
#SBATCH -q shared           # CONFIRM: shared = 1-GPU fraction; use debug for a <30min test
#SBATCH --gpus 1
#SBATCH -c 32
#SBATCH -t 00:30:00
#SBATCH -N 1
#SBATCH -J emobrain_e1_qwen
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/output/logs/%x_%j.out

set -euo pipefail

REPO_ROOT=/pscratch/sd/s/sjmoon/EmoBrain
VENV_ACTIVATE=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

# same cache as predownload; force offline (compute node has no internet)
export HF_HOME=/pscratch/sd/s/sjmoon/hf_cache
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

source "${VENV_ACTIVATE}"
python3 "${REPO_ROOT}/project/training/train.py" \
    --config "${REPO_ROOT}/project/configs/trackA_e1_qwen_gpusmoke.yaml"
