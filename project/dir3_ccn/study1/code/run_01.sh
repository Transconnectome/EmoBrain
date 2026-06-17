#!/bin/bash
#SBATCH --job-name=CCN_01_rsm
#SBATCH --account=m4727_g
#SBATCH --qos=shared
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --constraint=cpu
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/CCN/logs/01_rsm_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/CCN/logs/01_rsm_%j.err

mkdir -p /pscratch/sd/s/sjmoon/EmoFM/CCN/results
cd /pscratch/sd/s/sjmoon/EmoFM/CCN
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3 01_brain_jepa_rsm.py
