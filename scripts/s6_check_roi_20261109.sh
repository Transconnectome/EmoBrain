#!/bin/bash
#SBATCH --job-name=s6_check_roi
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=06:00:00
#SBATCH --array=1-6
#SBATCH --output=outputs/logs/s6_check_roi_fold%a_%A.log
# 11/9 입력층 점검. A-1(Brain → Emotion)만, 예비 실행과 같은 설정에서 입력층만 ROI 평균(roi_mean) 또는 ROI 8칸 평균(roi_cells)으로 바꿔 바깥 fold 하나를 GPU 하나로 돌린다(array 1~6).
# roi_cells는 칸 번호 파일이 먼저 있어야 한다(bash scripts/s2_roi_cells.sh). 설정은 configs/s6/run_config_check_<변형>_20261109.json
# 사용(레포 최상위에서): sbatch scripts/s6_check_roi_20261109.sh <동결 커밋> <roi_mean|roi_cells>. login node나 compute node에서 fold 하나만: SLURM_ARRAY_TASK_ID=<k> bash scripts/s6_check_roi_20261109.sh <커밋> <변형>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
FREEZE="${1:?동결 커밋}"
VARIANT="${2:?roi_mean 또는 roi_cells}"
case "$VARIANT" in roi_mean|roi_cells) ;; *) echo "변형은 roi_mean 또는 roi_cells" >&2; exit 1;; esac
K="${SLURM_ARRAY_TASK_ID:?fold 번호}"
export OMP_NUM_THREADS=8
export S6_OUT=$OUT_ROOT/s6_check_${VARIANT}
"$PY" s6_train.py --plan "outer_fold${K}" --conditions brain_only --config $ROOT/configs/s6/run_config_check_${VARIANT}_20261109.json --design-freeze "$FREEZE" --device cuda
