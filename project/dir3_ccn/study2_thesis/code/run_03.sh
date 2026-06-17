#!/bin/bash
#SBATCH -A m4641
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 02:00:00
#SBATCH --job-name=ch1c_roi
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/main/code/logs/ch1c_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/main/code/logs/ch1c_%j.err
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail

mkdir -p /pscratch/sd/s/sjmoon/EmoFM/main/code/logs

PYTHON="/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3"
SCRIPT="/pscratch/sd/s/sjmoon/EmoFM/main/code/03_ch1c_roi_decoding.py"

echo "Running: ${SCRIPT}"
echo "Start time: $(date)"
"${PYTHON}" "${SCRIPT}"
echo "End time: $(date)"
