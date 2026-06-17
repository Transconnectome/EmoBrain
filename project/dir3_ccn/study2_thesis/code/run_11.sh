#!/bin/bash
#SBATCH -A m4641
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 00:10:00
#SBATCH --job-name=ch2_figs
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/main/code/logs/ch2_figs_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/main/code/logs/ch2_figs_%j.err
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

set -euo pipefail

mkdir -p /pscratch/sd/s/sjmoon/EmoFM/main/code/logs

PYTHON="/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3"
SCRIPT="/pscratch/sd/s/sjmoon/EmoFM/main/code/11_ch2_figures.py"

echo "Running: ${SCRIPT}"
echo "Start time: $(date)"
"${PYTHON}" "${SCRIPT}"
echo "End time: $(date)"
