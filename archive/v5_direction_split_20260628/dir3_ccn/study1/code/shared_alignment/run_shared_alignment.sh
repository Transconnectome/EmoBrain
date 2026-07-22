#!/bin/bash
#SBATCH --job-name=ccn_shared
#SBATCH --account=m4641
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=03:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn/study1/logs/shared_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn/study1/logs/shared_%j.err

set -euo pipefail

ROOT="/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn"
PYTHON="/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python"

MODEL="${1:-vjepa2_pretrained}"

cd "$ROOT/study1/code/shared_alignment"
"$PYTHON" -u run_shared_alignment.py --model "$MODEL"

echo "Shared alignment done for $MODEL."
