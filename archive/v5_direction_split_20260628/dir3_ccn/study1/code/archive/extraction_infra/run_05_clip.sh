#!/bin/bash
#SBATCH --job-name=EmoFM_clip
#SBATCH --account=m4727_g
#SBATCH --qos=shared
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus-per-task=1
#SBATCH --constraint=gpu
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/logs/05_clip_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/logs/05_clip_%j.err

mkdir -p /pscratch/sd/s/sjmoon/EmoFM/logs

cd /pscratch/sd/s/sjmoon/EmoFM
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3 05_extract_clip_embeddings.py
