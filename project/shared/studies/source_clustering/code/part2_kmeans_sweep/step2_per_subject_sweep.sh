#!/bin/bash
#SBATCH -A m4641
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 02:00:00
#SBATCH -J src_p2_ps_sweep
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/source_clustering/logs/%x_%j.out
#SBATCH -e /pscratch/sd/s/sjmoon/EmoBrain/project/shared/studies/source_clustering/logs/%x_%j.err
#
# part2 step2. per-subject clustering sweep.
# 3 brain sources (roi_mean, brain_jepa, swift) x 5 subj x 4 algo x 49 K.
# CPU only. ~15-30 min.
set -euo pipefail

REPO=/pscratch/sd/s/sjmoon/EmoBrain
STUDY="${REPO}/project/shared/studies/source_clustering"
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

mkdir -p "${STUDY}/results" "${STUDY}/logs"
cd "${STUDY}/code"
PYTHONPATH="${STUDY}/code" python -m part2_kmeans_sweep.step2_per_subject_sweep 2>&1 | tee "${STUDY}/logs/_sweep_ps.log"
echo "[part2 step2 done]"
