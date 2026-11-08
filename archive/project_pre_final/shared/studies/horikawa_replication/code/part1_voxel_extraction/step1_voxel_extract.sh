#!/bin/bash
#SBATCH -A m4641
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 04:00:00
#SBATCH -J hor_p1_voxel_extract
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/horikawa_replication/logs/%x_%j.err
#
# part1 step1. Extract per-subject per-stim voxel mean pattern.
# Input. /pscratch/sd/s/sjmoon/Horikawa_embedding/horikawa_filtered_MNI_to_TRs/img/sub-XX_stimulus_N/frame_T.pt
# Output. results/voxel_patterns/sub-XX.npy  shape (2185, N_voxel_masked)
# 5 subj x 2185 stim x ~5 TR frames. CPU + I/O bound. ~1-3 hr.
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
STUDY="${REPO}/project/shared/studies/horikawa_replication"
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

mkdir -p "${STUDY}/results/voxel_patterns" "${STUDY}/logs"
cd "${STUDY}/code"
PYTHONPATH="${STUDY}/code" python -m part1_voxel_extraction.step1_voxel_extract 2>&1 | tee "${STUDY}/logs/_voxel_extract.log"
echo "[part1 step1 done]"
