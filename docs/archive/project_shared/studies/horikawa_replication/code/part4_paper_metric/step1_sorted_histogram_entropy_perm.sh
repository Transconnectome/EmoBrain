#!/bin/bash
#SBATCH -A m4641
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 01:00:00
#SBATCH -J hor_p4_paper_metric
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/logs/%x_%j.err
#
# part4 step1. Paper-style metric (Horikawa Fig 6 D/E):
#   - top 5% high-score samples per emotion across K clusters
#   - sorted-histogram + entropy + permutation null (100k)
# Apply to K in {15, 27, 50} for every per-subject voxel cluster setting under
#   results/per_subject/voxel__sub-XX/kmeans_K{15,27,50}/labels.csv
# CPU only. ~10-20 min (perm test scales with K).
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
STUDY="${REPO}/project/shared/studies/horikawa_replication"
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

mkdir -p "${STUDY}/results" "${STUDY}/logs"
cd "${STUDY}/code"
PYTHONPATH="${STUDY}/code" python -m part4_paper_metric.step1_sorted_histogram_entropy_perm --include-per-subject 2>&1 | tee "${STUDY}/logs/_paper_metric.log"
echo "[part4 step1 done]"
