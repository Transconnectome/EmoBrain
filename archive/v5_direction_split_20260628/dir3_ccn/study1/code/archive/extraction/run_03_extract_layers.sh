#!/bin/bash
#SBATCH --job-name=emofm_layers
#SBATCH --account=m4616
#SBATCH --qos=regular
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/logs/extract_layers_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/logs/extract_layers_%j.err

mkdir -p /pscratch/sd/s/sjmoon/EmoFM/logs

source ~/.bashrc
conda activate brain-jepa-env 2>/dev/null || true

python3 /pscratch/sd/s/sjmoon/EmoFM/03_extract_layer_embeddings.py
