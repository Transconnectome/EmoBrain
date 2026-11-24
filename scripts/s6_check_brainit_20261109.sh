#!/bin/bash
#SBATCH --job-name=s6_check_brainit
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=06:00:00
#SBATCH --array=1-6
#SBATCH --output=outputs/logs/s6_check_brainit_fold%a_%A.log
# 11/9 입력층 점검. A-1(Brain → Emotion)만, 예비 실행과 같은 설정에서 입력층만 Brain-IT tokenizer로 바꿔 바깥 fold 하나를 GPU 하나로 돌린다(array 1~6).
# 변형: sample(학습 때 voxel 37.5%를 예시마다 뽑음, Brain-IT 원문대로) 또는 nosample(뽑지 않음). 설정은 configs/s6/run_config_check_brainit_<변형>_20261109.json
# 사용(레포 최상위에서): sbatch scripts/s6_check_brainit_20261109.sh <동결 커밋> <sample|nosample>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
FREEZE="${1:?동결 커밋}"
VARIANT="${2:?sample 또는 nosample}"
case "$VARIANT" in sample|nosample) ;; *) echo "변형은 sample 또는 nosample" >&2; exit 1;; esac
K="${SLURM_ARRAY_TASK_ID:?fold 번호}"
export OMP_NUM_THREADS=8
export S6_OUT=$OUT_ROOT/s6_check_brainit_${VARIANT}
"$PY" s6_train.py --plan "outer_fold${K}" --conditions brain_only --config $ROOT/configs/s6/run_config_check_brainit_${VARIANT}_20261109.json --design-freeze "$FREEZE" --device cuda
