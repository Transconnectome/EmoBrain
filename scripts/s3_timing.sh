#!/bin/bash
#SBATCH --job-name=s3_timing
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=16
#SBATCH --time=00:30:00
#SBATCH --output=outputs/logs/s3_timing_%j.log
# S3 본 추출 전 시간 측정. 무작위 영상 30개(seed 20261106)와 가장 긴 영상(879번, 90초)을 시각 모델 넷으로 뽑아 영상당 시간과 GPU 메모리를 잰다.
# 결과는 본 특징 폴더가 아니라 s3_timing에 저장되므로 본 추출과 섞이지 않는다. 뇌 반응과 정서 정답은 읽지 않는다. 사용: sbatch s3_timing.sh
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
OUT=$OUT_ROOT/s3_timing
IDS=12,40,130,187,200,496,536,680,771,828,845,867,879,1152,1191,1215,1307,1312,1335,1350,1369,1413,1533,1547,1648,1652,1682,1744,1814,1919,2089
export S3_OUT="$OUT" HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16 TOKENIZERS_PARALLELISM=false
mkdir -p "$OUT"
nvidia-smi --query-gpu=timestamp,memory.used --format=csv,noheader -l 5 > "$OUT/gpu_memory.csv" &
GPU_LOG=$!
trap 'kill $GPU_LOG 2>/dev/null || true' EXIT
for MODEL in vjepa2 videomae timesformer clip; do
    echo "시작 $MODEL $(date +%s)"
    "$PY" s3_vision.py --model "$MODEL" --ids "$IDS" --device cuda
    echo "끝 $MODEL $(date +%s)"
done
