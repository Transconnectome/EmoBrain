#!/bin/bash
#SBATCH --job-name=emo_s1_lc
#SBATCH --nodelist=node4
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=12:00:00
#SBATCH --array=1-5
#SBATCH --output=/storage/bigdata/EmoBrain_response/stage1/logs/%x_%A_%a.out
#SBATCH --error=/storage/bigdata/EmoBrain_response/stage1/logs/%x_%A_%a.err
# 학습 곡선 (피험자별). 학습 영상 150~1500개 × 반복 4 + 전체. 결과는 stage1/05_learning_curve/ 에만 씀.
set -euo pipefail
export PYTHONPATH=/storage/bigdata/Horikawa/preprocessing_code_v2/pylib PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4} MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4} OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4}
/usr/anaconda3/bin/python3 -u /storage/bigdata/EmoBrain_response/code/stage1/learning_curve.py --sub $(printf %02d ${SLURM_ARRAY_TASK_ID:-1})
