#!/bin/bash
# Chance Cat34 re-measurement at threshold 0.10 (was 0.15).
# Cat34_multilabel + Cat34_soft. Trivial runtime (~30 sec).
#SBATCH --job-name=feel_cat34_chance_t010
#SBATCH --output=/pscratch/sd/s/sjmoon/FEELIN/output/slurm/cat34_baseline/cat34_chance_t010_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/FEELIN/output/slurm/cat34_baseline/cat34_chance_t010_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:15:00
#SBATCH --account=m4641
#SBATCH --qos=regular
#SBATCH --constraint=cpu

set -e
cd /pscratch/sd/s/sjmoon/FEELIN

/pscratch/sd/s/sjmoon/swift_PTL2/bin/python /pscratch/sd/s/sjmoon/FEELIN/code/probes/run_chance_cat34.py \
    --out_csv /pscratch/sd/s/sjmoon/FEELIN/results/phase1/chance_cat34_t010.csv \
    --summary_csv /pscratch/sd/s/sjmoon/FEELIN/results/phase1/chance_cat34_t010_summary.csv
