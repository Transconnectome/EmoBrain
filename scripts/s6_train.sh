#!/bin/bash
#SBATCH --job-name=s6_train
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=16
#SBATCH --time=24:00:00
#SBATCH --output=outputs/logs/s6_train_%j.log
# S6 뇌 모델 학습. GPU 작업이다. 설계 동결 커밋과 S7에서 정한 설정이 없으면 멈춘다. 끝난 학습은 같은 실행 번호일 때만 건너뛰므로 끊기면 같은 명령으로 잇는다.
# 사용: sbatch s6_train.sh <분할 ex) outer_fold1> <쉼표로 나눈 조건> <설정 JSON의 절대 경로> <동결 커밋>. GPU가 있는 노드에서 직접 돌릴 때는 bash로 같은 인자를 준다
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
PLAN="${1:?분할}"; CONDITIONS="${2:?조건}"; CONFIG="${3:?설정 JSON}"; FREEZE="${4:?설계 동결 커밋}"
export OMP_NUM_THREADS=8
"$PY" s6_train.py --plan "$PLAN" --conditions "$CONDITIONS" --config "$CONFIG" --design-freeze "$FREEZE" --device cuda
