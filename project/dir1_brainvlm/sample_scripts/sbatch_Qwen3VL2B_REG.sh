#!/bin/bash
#SBATCH -A m4641
#SBATCH -C gpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH --gpus-per-node=1
#SBATCH -t 12:00:00
#SBATCH -J REG_Qwen3VL2B
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/logs/%x_%j.err
#
# Qwen3-VL-2B + direct regression head ("Option B"). VA regression 단독.
# 예상 시간 = 4-6 hr (token output 대비 generation 없음 → 빠름). 12 hr 한도.
# 사용. sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/sbatch_Qwen3VL2B_REG.sh

set -euo pipefail
bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/UMBRELLA_ROI_Horikawa_Emotion_VA_regression_Qwen3VL2B_REG.sh
