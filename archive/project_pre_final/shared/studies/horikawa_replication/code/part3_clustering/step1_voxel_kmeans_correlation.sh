#!/bin/bash
#SBATCH -A m4641
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 01:00:00
#SBATCH -J hor_p3_kmeans_whole
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/logs/%x_%j.err
#
# part3 step1. Voxel-level k-means K=15/27/50 per subject.
# Paper-style. correlation distance via L2-normalized PCA proxy.
# Input. results/voxel_patterns/sub-XX.npy (from part1 step1)
# Output. results/per_subject/voxel__sub-XX/kmeans_K{15,27,50}/labels.csv
# CPU only. ~10-30 min (depends on voxel count + K).
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
STUDY="${REPO}/project/shared/studies/horikawa_replication"
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

mkdir -p "${STUDY}/results/per_subject" "${STUDY}/logs"
cd "${STUDY}/code"
PYTHONPATH="${STUDY}/code" python -m part3_clustering.step1_voxel_kmeans_correlation 2>&1 | tee "${STUDY}/logs/_voxel_cluster.log"
echo "[part3 step1 done]"
