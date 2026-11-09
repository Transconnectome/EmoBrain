#!/bin/bash
#SBATCH --job-name=s6_main
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=48:00:00
#SBATCH --array=1-6
#SBATCH --output=outputs/logs/s6_main_fold%a_%A.log
# S6 본실험의 기본 run 분할(바깥 fold 1~6). fold 하나를 GPU 하나로 돌린다. 설정은 configs/s6/run_config.json.
# 조건: A~E 묶음 11개(A-1, A-2, B-1, C-1, C-2, D-1, D-2, D-3, D-4, E-고정, E-학습), C-1의 더하기 head와 손실 흐름 허용판, encoder 2, Multimodal Model, 대조군 셋, 평균 pooling판(01 5-A, 7-L).
# 시간 상한에 걸리면 같은 명령으로 다시 내면 끝난 학습은 건너뛰고 잇는다. 처음 보는 장면, 네트워크, MC는 따로 낸다.
# 사용(레포 최상위에서): sbatch scripts/s6_main.sh <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
FREEZE="${1:?동결 커밋}"
K="${SLURM_ARRAY_TASK_ID:?fold 번호}"
CONDITIONS="brain_only,brain_only_featdec,brain_decoded,brain_decoded_additive,brain_decoded_grad,brain_only_distill,brain_decoded_distill,feature_encoder,brain_frozen_feature_encoder,brain_decoded_sep,brain_decoded_sep_distill,brain_features_only,brain_features_only_paired,multimodal,brain_only_repr_frozen,brain_only_repr_trained,control_label_smoothing,control_stimulus_shuffle,control_feature_shuffle,brain_only_pool,brain_decoded_pool"
export OMP_NUM_THREADS=8
"$PY" s6_train.py --plan "outer_fold${K}" --conditions "$CONDITIONS" --config "$ROOT/configs/s6/run_config.json" --design-freeze "$FREEZE" --device cuda
