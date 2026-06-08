#!/bin/bash
# BFM Cat34 re-measurement at threshold 0.10 (was 0.15).
# 3 BFM (Brain-JEPA, NeuroSTORM, SwiFT_NewE96) x 2 init (resting, scratch)
# x 2 task (Cat34_multilabel, Cat34_soft) x 5 fold x 1 seed.
# Linear probe only (matches the original Cat34 phase 1 launch with --skip_mlp).
# Estimated ~60-90 min on CPU.
#SBATCH --job-name=feel_cat34_bfm_t010
#SBATCH --output=/pscratch/sd/s/sjmoon/FEELIN/output/slurm/cat34_baseline/cat34_bfm_t010_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/FEELIN/output/slurm/cat34_baseline/cat34_bfm_t010_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=02:30:00
#SBATCH --account=m4641
#SBATCH --qos=regular
#SBATCH --constraint=cpu

set -e
cd /pscratch/sd/s/sjmoon/FEELIN

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python -u /pscratch/sd/s/sjmoon/FEELIN/code/probes/run_unified_probe.py \
    --tasks Cat34_multilabel,Cat34_soft \
    --features Brain-JEPA,SwiFT_NewE96,NeuroSTORM \
    --folds 1,2,3,4,5 \
    --seeds 0 \
    --skip_mlp \
    --out_csv /pscratch/sd/s/sjmoon/FEELIN/results/phase1/cat34_probe_linear_t010.csv \
    --summary_csv /pscratch/sd/s/sjmoon/FEELIN/results/phase1/cat34_probe_linear_t010_summary.csv
