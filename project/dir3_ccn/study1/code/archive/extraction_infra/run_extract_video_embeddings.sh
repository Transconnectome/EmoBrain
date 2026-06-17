#!/bin/bash
#SBATCH --job-name=EmoFM_vjepa2_extract
#SBATCH --account=m4727_g
#SBATCH --qos=shared
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --gpus-per-task=1
#SBATCH --constraint=gpu
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/logs/extract_vjepa2_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/logs/extract_vjepa2_%j.err

mkdir -p /pscratch/sd/s/sjmoon/EmoFM/logs

cd /pscratch/sd/s/sjmoon/EmoFM
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3 extract_video_embeddings.py
