#!/bin/bash
#SBATCH --job-name=s6_prelim_oof
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=24:00:00
#SBATCH --array=1-6
#SBATCH --output=outputs/logs/s6_prelim_oof_fold%a_%A.log
# 11/9 D 묶음 예비 실행(fold 밖 encoder 2판). 11/8 예비 실행과 같은 설정(configs/s6/run_config_prelim_20261108.json: d 64, 입력층 weight decay 0.01,
# learning rate 1e-4, seed 0, 옛 멈춤 기준)으로 A-1, encoder 2, fold 밖 encoder 2 넷, D-4(짝), D-1, D-2, D-3(학습 행은 fold 밖 v̂₂, ĉ₂), D-3 짝을 돌린다.
# D-2의 Stimulus 예측 평정은 11/8 예비 실행의 A-2, C-2가 쓴 옛 Stimulus 실행(superseded)을 쓴다. 예비 실행끼리 비교하려는 것이다.
# 결과는 s6_brain_prelim_oof에 따로 둔다. 11/9 이전 방식(이미 본 영상판)은 s6_brain_prelim_sep, s6_brain_prelim_d34에 있다.
# 사용(레포 최상위에서): sbatch scripts/s6_prelim_oof_20261109.sh <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
FREEZE="${1:?동결 커밋}"
K="${SLURM_ARRAY_TASK_ID:?fold 번호}"
export OMP_NUM_THREADS=8
export S6_OUT=$OUT_ROOT/s6_brain_prelim_oof
export S4_OUT=$OUT_ROOT/s4_no_brain/superseded/lr_1e-2_20261108
"$PY" s6_train.py --plan "outer_fold${K}" --conditions brain_only,feature_encoder,brain_frozen_feature_encoder,brain_decoded_sep,brain_decoded_sep_distill,brain_features_only,brain_features_only_paired --config $ROOT/configs/s6/run_config_prelim_20261108.json --design-freeze "$FREEZE" --device cuda
