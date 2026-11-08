#!/bin/bash
#SBATCH --job-name=s5_baselines
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=12:00:00
# 시간 제한 12시간은 측정값이 아니다. h2020은 CPU 8 thread 상한 추정이 약 22시간이고 GPU 시간은 재지 않았다. S7에서 재서 고친다.
#SBATCH --output=outputs/logs/s5_baselines_%j.log
# S5 기준선. GPU 작업이다. 설계 동결 뒤에만 돈다. 끝난 결과는 건너뛴다.
# 인자: <ridge|soft_bce|signal|zone|h2020> <참가자> <동결 커밋>, 또는 video "" <동결 커밋>. 새 할당은 sbatch, GPU가 있는 노드에서 직접 돌릴 때는 bash로 같은 인자를 준다
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=8
"$PY" s5_baselines.py --task "${1:?과제}" --participant "${2:-}" --design-freeze "${3:?설계 동결 커밋}" --device cuda
