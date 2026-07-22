#!/bin/bash
#SBATCH --job-name=CCN_17_av2d
#SBATCH --account=m5187_g
#SBATCH --qos=shared
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --constraint=cpu
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/CCN/logs/17_av2d_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/CCN/logs/17_av2d_%j.err

cd /pscratch/sd/s/sjmoon/EmoFM/CCN
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3 17_av2d_comparison.py
