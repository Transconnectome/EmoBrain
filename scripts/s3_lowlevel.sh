#!/bin/bash
#SBATCH --job-name=s3_lowlevel
#SBATCH --account=m5361
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --cpus-per-task=256
#SBATCH --time=03:00:00
#SBATCH --output=outputs/logs/s3_lowlevel_%j.log
# S3 저수준 특징(움직임 에너지, RGB 중앙값). CPU 작업이다. 영상을 64조각으로 나눠 함께 돌린다. 끊기면 같은 명령으로 이어서 뽑는다. 사용: sbatch s3_lowlevel.sh
# 로그인 노드에서 bash로 돌릴 때는 CPU 32개, 메모리 30 GB 제한이 있으므로 동시 실행 수를 줄인다. 예: S3_LOWLEVEL_JOBS=10 bash s3_lowlevel.sh
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 TQDM_DISABLE=1
JOBS="${S3_LOWLEVEL_JOBS:-64}"
PY="$PY_CPU"
seq 0 63 | xargs -P "$JOBS" -I{} sh -c "$PY s3_lowlevel.py --ids \$(( {} * 2196 / 64 + 1 ))-\$(( ({} + 1) * 2196 / 64 )) > /dev/null"
$PY s3_collect.py lowlevel
