#!/bin/bash
#SBATCH --job-name=s4_ridge
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/logs/s4_ridge_%j.log
# S4 뇌 없는 ridge. D12와 정서어 제거판. 설계 동결 뒤에만 돈다. 사용: bash s4_ridge.sh <d12|noemo> <동결 커밋>
set -euo pipefail
TASK="${1:?과제}"; FREEZE="${2:?설계 동결 커밋}"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s4_ridge.py --task "$TASK" --design-freeze "$FREEZE" --device cuda
