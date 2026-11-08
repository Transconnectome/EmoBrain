#!/bin/bash
#SBATCH --job-name=s3_text
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=16
#SBATCH --time=02:00:00
#SBATCH --output=outputs/logs/s3_text_%j.log
# S3 캡션 특징. DeBERTa, 정서어 제거 DeBERTa(SI), MPNet. 끊기면 처음부터 다시 돌린다. 사용: sbatch s3_text.sh
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16 TOKENIZERS_PARALLELISM=false
PY="$PY"
$PY s3_text.py --model deberta --device cuda
$PY s3_text.py --model deberta --no-emotion-words --device cuda
$PY s3_text.py --model mpnet --device cuda
$PY s3_collect.py deberta mpnet
