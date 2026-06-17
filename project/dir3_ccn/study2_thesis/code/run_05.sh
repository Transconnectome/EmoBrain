#!/bin/bash
#SBATCH -A m4641
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 01:00:00
#SBATCH --job-name=ch1d_pg
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/main/code/logs/ch1d_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/main/code/logs/ch1d_%j.err
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail

mkdir -p /pscratch/sd/s/sjmoon/EmoFM/main/code/logs

PYTHON="/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3"
SCRIPT="/pscratch/sd/s/sjmoon/EmoFM/main/code/05_ch1d_principal_gradient.py"

echo "Running: ${SCRIPT}"
echo "Start time: $(date)"
"${PYTHON}" "${SCRIPT}"
echo "End time: $(date)"
