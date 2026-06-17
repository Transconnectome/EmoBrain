#!/bin/bash
#SBATCH --account=m4641
#SBATCH --qos=cpu
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=00:10:00
#SBATCH --job-name=fig_aligned
#SBATCH --output=/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/study1/logs/fig_aligned_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/study1/logs/fig_aligned_%j.err

# Regenerate CCN camera-ready figures with "Brain-aligned" terminology.
# Writes figure1_ccn.pdf / figure2_ccn.pdf into both study1/results/figures/
# and the ccn2026_template/ folder (so camera_ready.tex picks them up directly).

set -e
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate
cd /pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/study1/code
python generate_figures_aligned.py
echo "Figures regenerated with aligned labels."
