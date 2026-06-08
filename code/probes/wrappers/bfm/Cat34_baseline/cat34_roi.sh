#!/bin/bash
# ROI baseline (Schaefer400 + Tian S3 50, time-mean) for Cat34_multilabel + Cat34_soft.
# Linear probe only (matches the original Cat34 phase 1 launch with --skip_mlp).
# 5 folds x 1 seed. Estimated ~30-45 min on CPU.
#SBATCH --job-name=feel_cat34_roi
#SBATCH --output=/pscratch/sd/s/sjmoon/FEELIN/output/slurm/cat34_baseline/cat34_roi_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/FEELIN/output/slurm/cat34_baseline/cat34_roi_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=01:30:00
#SBATCH --account=m4641
#SBATCH --qos=regular
#SBATCH --constraint=cpu

set -e
cd /pscratch/sd/s/sjmoon/FEELIN

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python /pscratch/sd/s/sjmoon/FEELIN/code/probes/run_unified_probe.py \
    --features ROI_Schaefer400Tian50 \
    --tasks Cat34_multilabel,Cat34_soft \
    --folds 1,2,3,4,5 \
    --seeds 0 \
    --skip_mlp \
    --out_csv /pscratch/sd/s/sjmoon/FEELIN/results/background/phase1/cat34_probe_ROI_linear.csv \
    --summary_csv /pscratch/sd/s/sjmoon/FEELIN/results/background/phase1/cat34_probe_ROI_linear_summary.csv
