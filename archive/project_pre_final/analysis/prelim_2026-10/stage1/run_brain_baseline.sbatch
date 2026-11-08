#!/bin/bash
#SBATCH --job-name=emo_s1_brain
#SBATCH --nodelist=node4
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=8:00:00
#SBATCH --array=1-5
#SBATCH --output=/storage/bigdata/EmoBrain_response/stage1/logs/%x_%A_%a.out
#SBATCH --error=/storage/bigdata/EmoBrain_response/stage1/logs/%x_%A_%a.err
# 1단계 핵심 3: Horikawa 뇌 단독 기준선 (피험자별). 배열 번호 = 피험자. 결과는 stage1/02_brain/ 에만 씀.
set -euo pipefail
export PYTHONPATH=/storage/bigdata/Horikawa/preprocessing_code_v2/pylib PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4} MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4} OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4}
PY=/usr/anaconda3/bin/python3; CODE=/storage/bigdata/EmoBrain_response/code/stage1/brain_baseline.py
$PY -u $CODE --self-test
$PY -u $CODE --sub $(printf %02d ${SLURM_ARRAY_TASK_ID:-1})
