#!/bin/bash
#SBATCH --job-name=s3_vision
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=16
#SBATCH --time=06:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/logs/s3_vision_%x_%j.log
# S3 시각 특징. GPU 작업이다. 사용: sbatch s3_vision.sh vjepa2 (또는 videomae, timesformer, clip). 끊기면 같은 명령으로 이어서 뽑는다. 코드를 고쳤으면 그 모델의 parts를 지워야 한다(사양이 다르면 멈춘다).
set -euo pipefail
MODEL="${1:?모델 이름}"
export HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16 TOKENIZERS_PARALLELISM=false
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s3_vision.py --model "$MODEL" --device cuda
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s3_collect.py "$MODEL"
