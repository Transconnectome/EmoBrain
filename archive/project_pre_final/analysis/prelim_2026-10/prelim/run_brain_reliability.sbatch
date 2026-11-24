#!/bin/bash
#SBATCH --job-name=emo_reliab
#SBATCH --nodelist=node4
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=1:00:00
#SBATCH --array=1-11
#SBATCH --output=/storage/bigdata/EmoBrain_response/prelim/logs/%x_%A_%a.out
#SBATCH --error=/storage/bigdata/EmoBrain_response/prelim/logs/%x_%A_%a.err
# 0-8 뇌 반응 안정성 (피험자별): 469개 영역 평균 반응 저장 + 피험자 안 반복 신뢰도. 읽기 전용, 결과는 prelim/ 에만 씀.
# 배열 1~5 = Horikawa sub-01~05, 6~11 = MindCaptioning sub-01~06.
set -euo pipefail
export PYTHONPATH=/storage/bigdata/Horikawa/preprocessing_code_v2/pylib PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2
i=${SLURM_ARRAY_TASK_ID:-1}
if [ $i -le 5 ]; then DS=horikawa; S=$(printf %02d $i); else DS=mindcaptioning; S=$(printf %02d $((i-5))); fi
/usr/anaconda3/bin/python3 -u /storage/bigdata/EmoBrain_response/code/prelim/brain_reliability.py --subject --dataset $DS --sub $S
