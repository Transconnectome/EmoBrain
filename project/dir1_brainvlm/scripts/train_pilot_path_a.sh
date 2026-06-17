#!/bin/bash
#SBATCH -A m4641
#SBATCH -C gpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH --gpus-per-node=1
#SBATCH -t 06:00:00
#SBATCH -J d1_path_a_pilot
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/output/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/output/logs/%x_%j.err
# D1 Path A pilot. Fold 1, 5 subj pooled, LoRA on Qwen3-VL.
# DO NOT sbatch without user approval ([[feedback-slurm-submit-permission]]).
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
DIR1=${REPO}/project/dir1_brainvlm
SHARED=${REPO}/project/shared

source /pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/activate

OUT=${DIR1}/output/pilot_fold1_$(date +%Y%m%d_%H%M%S)
mkdir -p "${OUT}" "${DIR1}/output/logs"

cd "${REPO}"
python -m project.dir1_brainvlm.code.train.train_pilot \
    --manifest      "${SHARED}/data/horikawa_5fold.csv" \
    --roi-dir       "${SHARED}/data/roi_timeseries_schaefer400tian50" \
    --captions      "${SHARED}/data/stimulus_features/qwen_vl_captions.jsonl" \
    --va-targets    "${SHARED}/data/va_continuous_z.csv" \
    --cat34-targets "${SHARED}/data/cat34_soft_distribution.csv" \
    --fold 1 \
    --out-dir "${OUT}" \
    --batch-size 8 --lr 1e-4 --epochs 5

echo "[done] pilot output at ${OUT}"
