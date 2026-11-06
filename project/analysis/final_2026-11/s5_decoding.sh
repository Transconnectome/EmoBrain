#!/bin/bash
#SBATCH --job-name=s5_decoding
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=16
#SBATCH --time=08:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/logs/s5_decoding_%j.log
# S5 층별 feature decoding. GPU 작업이다. 설계 동결 뒤에만 돈다. 끝난 fold는 건너뛴다. 사용: bash s5_decoding.sh <참가자 01~05> <동결 커밋>
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s5_decoding.py --participant "${1:?참가자}" --design-freeze "${2:?설계 동결 커밋}" --device cuda
