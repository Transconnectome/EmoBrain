#!/bin/bash
#SBATCH --job-name=s8_mc_transfer
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=12:00:00
#SBATCH --output=outputs/logs/s8_mc_transfer_%j.log
# S8 6-3 MC 시청 전이. HK 최종 모델의 공유 가중치를 고정하고 MC 참가자마다 입력층만 학습한 뒤 시험 72개로 채점한다(GPU). 규칙은 src/s8_mc_transfer.py 머리말.
# login node에서는 bash로, 할당을 쓸 때는 sbatch로 같은 인자를 준다. 끝난 단위(조건, seed, 참가자)는 건너뛴다.
# 사용(레포 최상위): bash scripts/s8_mc_transfer.sh <HK 최종 모델 폴더> <출력 폴더> <동결 커밋> [조건 쉼표] [seed 쉼표] [참가자 쉼표] [분할, 기본 final_for_mc]
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=8
"$PY" s8_mc_transfer.py --final "${1:?HK 최종 모델 폴더}" --out "${2:?출력 폴더}" --design-freeze "${3:?동결 커밋}" \
    --conditions "${4:-brain_only,brain_decoded}" --seeds "${5:-0,1,2}" --participants "${6:-01,02,03,04,05,06}" --plan "${7:-final_for_mc}" --device cuda
