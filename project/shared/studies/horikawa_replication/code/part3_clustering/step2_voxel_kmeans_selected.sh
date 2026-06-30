#!/bin/bash
#SBATCH -A m4641
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 01:00:00
#SBATCH -J hor_p3_kmeans_selected
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/logs/%x_%j.err
#
# part3 step2. Voxel-level k-means K=15/27/50 per subject, SELECTED voxel only.
# Uses part2 step1 의 selected_idx -> paper-faithful (Horikawa Fig 6 voxel restriction).
# Input. results/voxel_patterns/sub-XX.npy (part1 step1) + results/voxel_selection/sub-XX_selected_idx.npy (part2 step1)
# Output. results/per_subject/voxel_selected__sub-XX/kmeans_K{15,27,50}/labels.csv
# CPU only. ~5-15 min (selected voxel count usually 5-10% of whole-brain).
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
STUDY="${REPO}/project/shared/studies/horikawa_replication"
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

mkdir -p "${STUDY}/results/per_subject" "${STUDY}/logs"
cd "${STUDY}/code"
PYTHONPATH="${STUDY}/code" python -m part3_clustering.step2_voxel_kmeans_selected 2>&1 | tee "${STUDY}/logs/_voxel_cluster_selected.log"
echo "[part3 step2 done]"
