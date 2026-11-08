#!/bin/bash
#SBATCH --job-name=s6_prelim
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=16:00:00
#SBATCH --array=1-6
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/logs/s6_prelim_fold%a_%A.log
# 11/8 발표용 예비 실행. 바깥 fold 하나를 GPU 하나로 돌린다(array 1~6). 설정은 manifests/s6/run_config_prelim_20261108.json
# (d 64, 입력층 weight decay 0.01, learning rate 1e-4, seed 0. λ, r, α는 G9 그대로). 결과는 본 실행과 섞이지 않게 s6_brain_prelim에 둔다.
# 사용: sbatch s6_prelim_20261108.sh <동결 커밋>. GPU가 있는 노드에서 fold 하나만 직접 돌릴 때는 SLURM_ARRAY_TASK_ID=<k> bash s6_prelim_20261108.sh <커밋>
set -euo pipefail
FREEZE="${1:?동결 커밋}"
K="${SLURM_ARRAY_TASK_ID:?fold 번호}"
CONDITIONS="brain_only,brain_only_featdec,brain_decoded,brain_decoded_additive,brain_only_distill,brain_decoded_distill"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8
export S6_OUT=/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/s6_brain_prelim
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s6_train.py --plan "outer_fold${K}" --conditions "$CONDITIONS" --config /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11/manifests/s6/run_config_prelim_20261108.json --design-freeze "$FREEZE" --device cuda
