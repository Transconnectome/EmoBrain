#!/bin/bash
#SBATCH -A m4641
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 02:00:00
#SBATCH -J hor_p2_voxel_select
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/logs/%x_%j.err
#
# part2 step1. Voxel selection by encoding regression R^2.
# Per-subject voxel-wise ridge: Cat34 -> BOLD voxel, 5-fold CV.
# Voxels passing r^2 >= 0.05 saved.
# Input. results/voxel_patterns/sub-XX.npy (part1 step1 output)
# Output. results/voxel_selection/sub-XX_{r2_map, selected_idx}.npy
# CPU bound. Multi-output ridge -> per subj ~5-15 min (5 fold x ~50k voxel).
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
STUDY="${REPO}/project/shared/studies/horikawa_replication"
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

mkdir -p "${STUDY}/results/voxel_selection" "${STUDY}/logs"
cd "${STUDY}/code"
PYTHONPATH="${STUDY}/code" python -m part2_voxel_selection.step1_encoding_ridge_voxel_select 2>&1 | tee "${STUDY}/logs/_voxel_selection.log"
echo "[part2 step1 done]"
