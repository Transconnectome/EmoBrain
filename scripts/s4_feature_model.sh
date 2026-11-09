#!/bin/bash
#SBATCH --job-name=s4_feature_model
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=12:00:00
#SBATCH --output=outputs/logs/s4_feature_model_%j.log
# S4 Stimulus Model. GPU 작업이다. 설계 동결 뒤에만 돈다. 끝난 과제는 건너뛰므로 끊기면 같은 명령으로 잇는다.
# 사용: bash s4_feature_model.sh <stimulus|k1a|noemo|zone|baseline> <동결 커밋> [나눔 i/n]
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
TASK="${1:?과제}"; FREEZE="${2:?설계 동결 커밋}"; PART="${3:-0/1}"
export OMP_NUM_THREADS=4
"$PY" s4_feature_model.py --task "$TASK" --design-freeze "$FREEZE" --part "$PART" --device cuda
