#!/bin/bash
#SBATCH --job-name=s4_feature_model
#SBATCH --account=m5187_g
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=16
#SBATCH --time=12:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/project/output/final_2026-11/logs/s4_feature_model_%j.log
# S4 특징 모델. GPU 작업이다. 설계 동결 뒤에만 돈다. 끝난 과제는 건너뛰므로 끊기면 같은 명령으로 잇는다.
# 사용: bash s4_feature_model.sh <tvs|k1a|noemo|zone|hkfinal> <동결 커밋> [나눔 i/n]
set -euo pipefail
TASK="${1:?과제}"; FREEZE="${2:?설계 동결 커밋}"; PART="${3:-0/1}"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s4_feature_model.py --task "$TASK" --design-freeze "$FREEZE" --part "$PART" --device cuda
