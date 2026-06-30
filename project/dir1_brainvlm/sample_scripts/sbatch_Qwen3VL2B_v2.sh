#!/bin/bash
#SBATCH -A m4641
#SBATCH -C gpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH --gpus-per-node=1
#SBATCH -t 16:00:00
#SBATCH -J v2_Qwen3VL2B
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/logs/%x_%j.err
#
# Qwen3-VL-2B v2 (binary + regression sequential).
# 예상 시간 = 10-14 hr. 16 hr 한도.
# 사용. sbatch /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/sbatch_Qwen3VL2B_v2.sh

set -euo pipefail
bash /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/sample_scripts/RUN_Qwen3VL2B_v2.sh
