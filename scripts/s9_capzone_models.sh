#!/bin/bash
#SBATCH --job-name=s9_capzone_models
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=12:00:00
#SBATCH --output=outputs/logs/s9_capzone_models_%j.log
# S9 Dec-바(01 6-2b) C-1, D-3, D-4. 규칙은 src/s9_capzone_models.py 머리말. cabc1f7 위에 이 파일만 더한 run worktree의 최상위에서 실행한다.
# 분할 하나에 encoder 2, fold 밖 encoder 2 넷, C-1, D-3, D-4 head(약 5시간). 끝난 단계는 건너뛴다.
# 사용: bash scripts/s9_capzone_models.sh <분할 ex) capzone_block1_fold1_excluded> <run_config_capzone.json> <s6_brain_capzone> <s6_brain_final>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export OMP_NUM_THREADS=8
"$PY" s9_capzone_models.py --plan "${1:?분할}" --config "${2:?설정}" --s6-out "${3:?S6 결과 폴더}" --hk-final "${4:?HK 최종 폴더}" --design-freeze cabc1f7 --device cuda
