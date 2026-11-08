#!/bin/bash
#SBATCH --job-name=s4_ridge
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH --output=outputs/logs/s4_ridge_%j.log
# S4 뇌 없는 ridge. D12와 정서어 제거판. 설계 동결 뒤에만 돈다. 사용: bash s4_ridge.sh <d12|noemo> <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
TASK="${1:?과제}"; FREEZE="${2:?설계 동결 커밋}"
export OMP_NUM_THREADS=8
"$PY" s4_ridge.py --task "$TASK" --design-freeze "$FREEZE" --device cuda
