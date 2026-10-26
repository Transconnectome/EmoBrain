#!/bin/bash
#SBATCH --job-name=emo_s1_ladder
#SBATCH --nodelist=node4
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=8:00:00
#SBATCH --array=0-5
#SBATCH --output=/storage/bigdata/EmoBrain_response/stage1/logs/%x_%A_%a.out
#SBATCH --error=/storage/bigdata/EmoBrain_response/stage1/logs/%x_%A_%a.err
# 1단계 비교 사다리. 배열 0 = 내용 특징 → 정서 (영상 단위), 1~5 = 피험자별 뇌 → 내용, 뇌 → 내용 → 정서, 뇌+내용 → 정서.
# 결과는 stage1/03_stimulus/, stage1/04_brain_features/ 에만 씀. 특징은 /storage/bigdata/EmoBrain_response/features/ 에 넣으면 자동 추가.
set -euo pipefail
export PYTHONPATH=/storage/bigdata/Horikawa/preprocessing_code_v2/pylib PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4} MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4} OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4}
PY=/usr/anaconda3/bin/python3; CODE=/storage/bigdata/EmoBrain_response/code/stage1/content_ladder.py
i=${SLURM_ARRAY_TASK_ID:-0}
if [ $i -eq 0 ]; then $PY -u $CODE --stimulus; else $PY -u $CODE --sub $(printf %02d $i); fi
