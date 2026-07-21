#!/bin/bash
#SBATCH -A m4641
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 02:00:00
#SBATCH --job-name=ch1_nc
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/main/code/logs/ch1_nc_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/main/code/logs/ch1_nc_%j.err
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail

mkdir -p /pscratch/sd/s/sjmoon/EmoFM/main/code/logs

PYTHON="/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3"
SCRIPT="/pscratch/sd/s/sjmoon/EmoFM/main/code/04_ch1_noise_ceiling.py"

echo "Running: ${SCRIPT}"
echo "Start time: $(date)"
"${PYTHON}" "${SCRIPT}"
echo "End time: $(date)"
