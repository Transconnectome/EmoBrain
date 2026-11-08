#!/bin/bash
#SBATCH --job-name=emo_reliab_grp
#SBATCH --nodelist=node4
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=0:30:00
#SBATCH --output=/storage/bigdata/EmoBrain_response/prelim/logs/%x_%j.out
#SBATCH --error=/storage/bigdata/EmoBrain_response/prelim/logs/%x_%j.err
# 0-8 피험자 간 일치도 (영역 단위). 피험자별 job(run_brain_reliability.sbatch)이 끝난 뒤 실행.
set -euo pipefail
export PYTHONPATH=/storage/bigdata/Horikawa/preprocessing_code_v2/pylib PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1
for DS in horikawa mindcaptioning; do
  /usr/anaconda3/bin/python3 -u /storage/bigdata/EmoBrain_response/code/prelim/brain_reliability.py --group --dataset $DS
done
