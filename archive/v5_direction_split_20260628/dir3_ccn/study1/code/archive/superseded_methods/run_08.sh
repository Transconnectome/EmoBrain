#!/bin/bash
#SBATCH --job-name=CCN_08_raw_ksweep
#SBATCH --account=m4727_g
#SBATCH --qos=shared
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --constraint=cpu
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/CCN/logs/08_raw_ksweep_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/CCN/logs/08_raw_ksweep_%j.err

cd /pscratch/sd/s/sjmoon/EmoFM/CCN
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3 08_raw_k_sweep.py
