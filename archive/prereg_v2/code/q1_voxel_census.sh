#!/bin/bash
#SBATCH -A m5187
#SBATCH -q shared
#SBATCH -C cpu
#SBATCH -c 32
#SBATCH --mem=48G
#SBATCH -t 01:00:00
#SBATCH -J q1_voxel_census
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs/q1_voxel_census.%j.out
# Preprocessing census q1. Reads all 11,285 step7 segments (70 GB gz) and all
# 66,755 filtered frames. Read-only. Runs under plain bash on a login node
# within the per-user cgroup (32 CPU, 32 GB) with 16 workers, or via sbatch.
# Pass --max-runs N --tag smoke for a smoke test.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/code
LOGS=/pscratch/sd/s/sjmoon/EmoBrain/prereg_v2/logs
mkdir -p "$LOGS"
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
"$PY" "$CODE/q1_voxel_census.py" "$@" 2>&1 | tee "$LOGS/q1_voxel_census.$(date -u +%Y%m%dT%H%M%SZ).log"
