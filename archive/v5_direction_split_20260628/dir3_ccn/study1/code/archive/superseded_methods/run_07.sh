#!/bin/bash
#SBATCH --job-name=CCN_07_raw_rsa_cka
#SBATCH --account=m4727_g
#SBATCH --qos=shared
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --constraint=cpu
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/CCN/logs/07_raw_rsa_cka_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/CCN/logs/07_raw_rsa_cka_%j.err

mkdir -p /pscratch/sd/s/sjmoon/EmoFM/CCN/logs
cd /pscratch/sd/s/sjmoon/EmoFM/CCN
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3 07_raw_rsm_rsa_cka.py
