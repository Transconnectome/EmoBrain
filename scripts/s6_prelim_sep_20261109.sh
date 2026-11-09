#!/bin/bash
#SBATCH --job-name=s6_prelim_sep
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=24:00:00
#SBATCH --array=1-6
#SBATCH --output=outputs/logs/s6_prelim_sep_fold%a_%A.log
# 11/9 D-1, D-2(분리 encoder) 예비 실행. 11/8 예비 실행과 같은 설정(configs/s6/run_config_prelim_20261108.json: d 64, 입력층 weight decay 0.01,
# learning rate 1e-4, seed 0, 옛 멈춤 기준)으로 A-1, encoder 2, D-1, D-2를 돌린다. encoder 2와 D의 d, weight decay는 같은 실행의 A-1 선택을 따르므로 A-1도 함께 돈다.
# D-2의 Stimulus 예측 평정은 11/8 예비 실행의 A-2, C-2가 쓴 옛 Stimulus 실행(learning rate 후보 1e-4~1e-2, superseded)을 그대로 쓴다. 예비 실행끼리 비교하려는 것이다.
# 결과는 s6_brain_prelim_sep에 따로 둔다.
# 사용(레포 최상위에서): sbatch scripts/s6_prelim_sep_20261109.sh <동결 커밋>. login node나 compute node에서 fold 하나만: SLURM_ARRAY_TASK_ID=<k> bash scripts/s6_prelim_sep_20261109.sh <커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
FREEZE="${1:?동결 커밋}"
K="${SLURM_ARRAY_TASK_ID:?fold 번호}"
export OMP_NUM_THREADS=8
export S6_OUT=$OUT_ROOT/s6_brain_prelim_sep
export S4_OUT=$OUT_ROOT/s4_no_brain/superseded/lr_1e-2_20261108
"$PY" s6_train.py --plan "outer_fold${K}" --conditions brain_only,feature_encoder,brain_decoded_sep,brain_decoded_sep_distill --config $ROOT/configs/s6/run_config_prelim_20261108.json --design-freeze "$FREEZE" --device cuda
