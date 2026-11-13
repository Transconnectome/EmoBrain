#!/bin/bash
#SBATCH --job-name=s9_saved_models
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=06:00:00
#SBATCH --output=outputs/logs/s9_saved_models_%j.log
# S9 저장된 모델로 하는 분석. 다시 학습하지 않는다. swap은 C-1의 바꿔 끼우기(2-2, 1-1, 1-2), perturb는 A-1과 C-1의 네트워크 13묶음과 ROI 370개 입력 교란(6-4b와 ROI판). GPU 작업이다.
# 설계 동결 뒤에만 돈다. 끝난 fold는 건너뛴다. 새 할당은 sbatch s9_saved_models.sh <swap|perturb> <S6 결과 폴더> <동결 커밋> [fold 목록 ex) 1,2],
# login node나 Slurm으로 할당받은 compute node 안에서 직접 돌릴 때는 bash로 같은 인자를 준다
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=8
"$PY" s9_saved_models.py --task "${1:?swap 또는 perturb}" --s6-dir "${2:?S6 결과 폴더}" --design-freeze "${3:?설계 동결 커밋}" ${4:+--folds "$4"} --device cuda
