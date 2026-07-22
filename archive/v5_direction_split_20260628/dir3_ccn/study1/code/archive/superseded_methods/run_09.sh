#!/bin/bash
#SBATCH --job-name=CCN_09_raw_umap
#SBATCH --account=m4727_g
#SBATCH --qos=shared
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --constraint=cpu
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/CCN/logs/09_raw_umap_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/CCN/logs/09_raw_umap_%j.err

cd /pscratch/sd/s/sjmoon/EmoFM/CCN
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3 09_raw_umap.py
