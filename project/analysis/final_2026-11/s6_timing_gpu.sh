#!/bin/bash
#SBATCH --job-name=s6_timing_gpu
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=16
#SBATCH --time=00:15:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/logs/s6_timing_gpu_%j.log
# S6 뇌 모델 학습 한 step의 GPU 시간과 메모리. 합성 난수만 쓰고 실제 뇌 반응과 정답을 읽지 않는다. S7의 측정이 아니라 일정 어림용이다.
# 새 할당은 sbatch s6_timing_gpu.sh, GPU가 있는 노드에서 직접 돌릴 때는 bash s6_timing_gpu.sh
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 S6_TIMING_DEVICE=cuda
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s6_tests.py --timing
