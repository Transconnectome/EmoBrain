#!/bin/bash
#SBATCH --job-name=s6_prelim
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=24:00:00
#SBATCH --array=1-6
#SBATCH --output=outputs/logs/s6_prelim_fold%a_%A.log
# 11/8 발표용 예비 실행. 바깥 fold 하나를 GPU 하나로 돌린다(array 1~6). 설정은 configs/s6/run_config_prelim_20261108.json
# (d 64, 입력층 weight decay 0.01, learning rate 1e-4, seed 0. λ, r, α는 G9 그대로). 결과는 본 실행과 섞이지 않게 s6_brain_prelim에 둔다.
# 사용(레포 최상위에서): sbatch scripts/s6_prelim_20261108.sh <동결 커밋>. Slurm으로 할당받은 compute node 안에서 fold 하나만 직접 돌릴 때는 SLURM_ARRAY_TASK_ID=<k> bash scripts/s6_prelim_20261108.sh <커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
FREEZE="${1:?동결 커밋}"
K="${SLURM_ARRAY_TASK_ID:?fold 번호}"
CONDITIONS="brain_only,brain_only_featdec,brain_decoded,brain_decoded_additive,brain_only_distill,brain_decoded_distill,multimodal,brain_only_repr_frozen,brain_only_repr_trained"  # 조건 1~7과 더하기 head, Multimodal Model(11/8 석진 님이 6, 7을 더함)
export OMP_NUM_THREADS=8
export S6_OUT=$OUT_ROOT/s6_brain_prelim
"$PY" s6_train.py --plan "outer_fold${K}" --conditions "$CONDITIONS" --config $ROOT/configs/s6/run_config_prelim_20261108.json --design-freeze "$FREEZE" --device cuda
