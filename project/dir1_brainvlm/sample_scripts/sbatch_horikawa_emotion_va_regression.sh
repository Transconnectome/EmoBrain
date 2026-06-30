#!/bin/bash
#SBATCH -A m4641
#SBATCH -C gpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH --gpus-per-node=1
#SBATCH -t 24:00:00
#SBATCH -J horikawa_va_regression
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm/logs/%x_%j.err
#
# Sbatch wrapper. Horikawa Emotion VA_regression 본 학습 (50 epoch, 전체 데이터).
# 본 학습 entry script (interactive bash 형식) 을 sbatch 환경에서 실행.
# 사용 = sbatch sbatch_horikawa_emotion_va_regression.sh
#
# 시간 한도. 24 hr. epoch 1 당 약 10-20 min 추정 (8740 train sample, batch 4 + grad_accum 16, A100 80GB) → 50 epoch ≈ 10-15 hr.
# 본 학습 시작 전 반드시 SMOKE 통과 후 실행.

set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
D1=${REPO}/project/dir1_brainvlm

bash ${D1}/sample_scripts/UMBRELLA_ROI_Horikawa_Emotion_VA_regression_icl_3subj_3stim.sh
