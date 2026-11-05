#!/bin/bash
#SBATCH --job-name=s3_lowlevel
#SBATCH --account=m5361
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --cpus-per-task=256
#SBATCH --time=03:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/logs/s3_lowlevel_%j.log
# S3 저수준 특징(움직임 에너지, RGB 중앙값). CPU 작업이다. 영상을 64조각으로 나눠 함께 돌린다. 사용: sbatch s3_lowlevel.sh
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
PY=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
seq 0 63 | xargs -P 64 -I{} sh -c "$PY s3_lowlevel.py --ids \$(( {} * 2196 / 64 + 1 ))-\$(( ({} + 1) * 2196 / 64 )) > /dev/null"
$PY s3_collect.py lowlevel
