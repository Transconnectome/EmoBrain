#!/bin/bash
#SBATCH --job-name=s5_baselines
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=16
#SBATCH --time=12:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/logs/s5_baselines_%j.log
# S5 기준선. GPU 작업이다. 설계 동결 뒤에만 돈다. 끝난 결과는 건너뛴다.
# 사용: bash s5_baselines.sh <ridge|soft_bce|signal|zone|h2020> <참가자> <동결 커밋>, 또는 bash s5_baselines.sh video "" <동결 커밋>
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s5_baselines.py --task "${1:?과제}" --participant "${2:-}" --design-freeze "${3:?설계 동결 커밋}" --device cuda
