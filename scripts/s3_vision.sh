#!/bin/bash
#SBATCH --job-name=s3_vision
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=16
#SBATCH --time=06:00:00
#SBATCH --output=outputs/logs/s3_vision_%x_%j.log
# S3 시각 특징. GPU 작업이다. 사용: sbatch s3_vision.sh vjepa2 (또는 videomae, timesformer, clip). 끊기면 같은 명령으로 이어서 뽑는다. 코드를 고쳤으면 그 모델의 parts를 지워야 한다(사양이 다르면 멈춘다).
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
MODEL="${1:?모델 이름}"
export HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16 TOKENIZERS_PARALLELISM=false
"$PY" s3_vision.py --model "$MODEL" --device cuda
"$PY" s3_collect.py "$MODEL"
