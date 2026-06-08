#!/bin/bash
# ROI Cat34 re-measurement at threshold 0.10 (was 0.15).
# Tier 1 baseline (Schaefer400 + Tian S3 50, time-mean) for Cat34_multilabel + Cat34_soft.
# Linear probe only. Estimated ~30-45 min on CPU.
#SBATCH --job-name=feel_cat34_roi_t010
#SBATCH --output=/pscratch/sd/s/sjmoon/FEELIN/project/shared/output/slurm/cat34_baseline/cat34_roi_t010_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/FEELIN/project/shared/output/slurm/cat34_baseline/cat34_roi_t010_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=01:30:00
#SBATCH --account=m4641
#SBATCH --qos=regular
#SBATCH --constraint=cpu

set -e
cd /pscratch/sd/s/sjmoon/FEELIN

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python /pscratch/sd/s/sjmoon/FEELIN/project/shared/code/probes/run_unified_probe.py \
    --features ROI_Schaefer400Tian50 \
    --tasks Cat34_multilabel,Cat34_soft \
    --folds 1,2,3,4,5 \
    --seeds 0 \
    --skip_mlp \
    --out_csv /pscratch/sd/s/sjmoon/FEELIN/project/shared/results/background/phase1/cat34_probe_ROI_linear_t010.csv \
    --summary_csv /pscratch/sd/s/sjmoon/FEELIN/project/shared/results/background/phase1/cat34_probe_ROI_linear_t010_summary.csv
