#!/bin/bash
#SBATCH -A m4641
#SBATCH -C cpu
#SBATCH -q regular
#SBATCH -N 1
#SBATCH -t 01:00:00
#SBATCH --job-name=ccn_cca100_fast
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/CCN2026/logs/exp21b_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/CCN2026/logs/exp21b_%j.err
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G

set -euo pipefail

mkdir -p /pscratch/sd/s/sjmoon/EmoFM/CCN2026/logs

PYTHON_BIN="/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3"
SCRIPT_PATH="/pscratch/sd/s/sjmoon/EmoFM/CCN2026/21b_cca_100_noperm.py"

echo "Running: ${SCRIPT_PATH}"
echo "Start time: $(date)"
"${PYTHON_BIN}" "${SCRIPT_PATH}"
echo "End time: $(date)"
