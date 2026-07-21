#!/bin/bash
#SBATCH --job-name=EmoFM_download_vjepa2
#SBATCH --account=m4727_g
#SBATCH --qos=shared
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus-per-task=1
#SBATCH --constraint=gpu
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/logs/01_download_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/logs/01_download_%j.err

mkdir -p /pscratch/sd/s/sjmoon/EmoFM/logs

cd /pscratch/sd/s/sjmoon/EmoFM
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3 01_download_vjepa2.py
