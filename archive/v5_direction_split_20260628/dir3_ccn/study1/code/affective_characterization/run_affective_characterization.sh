#!/bin/bash
#SBATCH --job-name=ccn_affect
#SBATCH --account=m4641
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=02:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn/study1/logs/affect_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn/study1/logs/affect_%j.err

set -euo pipefail

ROOT="/pscratch/sd/s/sjmoon/EmoBrain/archive/v5_direction_split_20260628/dir3_ccn"
PYTHON="/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python"

MODEL="${1:-vjepa2_pretrained}"

cd "$ROOT/study1/code/affective_characterization"
"$PYTHON" -u run_affective_characterization.py --model "$MODEL"

echo "Affective characterization done for $MODEL."
