#!/bin/bash
#SBATCH --job-name=s9_untrained_encoder
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=06:00:00
#SBATCH --output=outputs/logs/s9_untrained_encoder_%j.log
# S9 D-4 대조(학습하지 않은 encoder 2를 고정). 규칙은 src/s9_untrained_encoder.py 머리말. HK 주 비교를 학습한 1bca774 위에 이 파일만 더한 run worktree의 최상위에서 실행한다.
# login node에서는 bash로, 할당을 쓸 때는 sbatch로 같은 인자를 준다. 바깥 fold 하나에 짝 넷(짝마다 수 분)과 자료 준비.
# 사용: bash scripts/s9_untrained_encoder.sh train <outer_fold 번호들, 쉼표> <run_config_grid_main.json> <s6_brain_grid_main> <출력 폴더>
#       bash scripts/s9_untrained_encoder.sh summarize <s6_brain_grid_main> <출력 폴더>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=8
case "${1:?train 또는 summarize}" in
  train)
    for k in ${2//,/ }; do
      "$PY" s9_untrained_encoder.py train --plan "outer_fold$k" --config "${3:?설정}" --s6-root "${4:?S6 주 비교 폴더}" --out "${5:?출력 폴더}" --design-freeze 1bca774 --device cuda
    done ;;
  summarize)
    "$PY" s9_untrained_encoder.py summarize --s6-root "${2:?S6 주 비교 폴더}" --out "${3:?출력 폴더}" ;;
esac
