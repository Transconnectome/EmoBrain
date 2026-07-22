#!/bin/bash
#SBATCH --job-name=bjepa_audit
#SBATCH --account=m4641
#SBATCH --constraint=cpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:10:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation/logs/audit_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation/logs/audit_%j.err

set -euo pipefail

ROOT="/pscratch/sd/s/sjmoon/EmoBrain/external/Brain-JEPA_short_window_validation"
PYTHON="/pscratch/sd/s/sjmoon/brain-jepa-env/bin/python"
mkdir -p "$ROOT/logs"
cd "$ROOT/checkpoint_audit"
"$PYTHON" -u run_checkpoint_audit.py
