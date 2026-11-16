#!/bin/bash
#SBATCH --job-name=s5_roi_map
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --output=outputs/logs/s5_roi_map_%j.log
# S5 370개 ROI 지도. ROI마다 그 ROI의 voxel만으로 정서 34개, Vision feature, Caption feature를 ridge로 decoding한다(01 6-4, 11/13). GPU 작업이다.
# 설계 동결 뒤에만 돈다. 끝난 fold는 건너뛴다. 새 할당은 sbatch s5_roi_map.sh <참가자 01~05> <동결 커밋> [fold 목록 ex) 1,2],
# login node나 Slurm으로 할당받은 compute node 안에서 직접 돌릴 때는 bash로 같은 인자를 준다
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=8
"$PY" s5_roi_map.py --participant "${1:?참가자}" --design-freeze "${2:?설계 동결 커밋}" ${3:+--folds "$3"} --device cuda
