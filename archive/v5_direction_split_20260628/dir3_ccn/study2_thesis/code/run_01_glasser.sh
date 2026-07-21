#!/bin/bash
#SBATCH -A m4641
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 12:00:00
#SBATCH --job-name=glasser_parcel
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/main/code/logs/glasser_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/main/code/logs/glasser_%j.err
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G

set -euo pipefail

mkdir -p /pscratch/sd/s/sjmoon/EmoFM/main/code/logs

# brain-jepa env has nilearn
PYTHON="/global/homes/s/sjmoon/.conda/envs/brain-jepa/bin/python"
SCRIPT="/pscratch/sd/s/sjmoon/EmoFM/main/code/01_glasser_parcellation.py"

echo "Running: ${SCRIPT}"
echo "Start time: $(date)"
"${PYTHON}" "${SCRIPT}"
echo "End time: $(date)"
