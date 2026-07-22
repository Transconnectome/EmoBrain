#!/bin/bash
#SBATCH --job-name=CCN_04_rsa
#SBATCH --account=m4727_g
#SBATCH --qos=shared
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --constraint=cpu
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoFM/CCN/logs/04_rsa_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoFM/CCN/logs/04_rsa_%j.err

cd /pscratch/sd/s/sjmoon/EmoFM/CCN
/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python3 04_crossspace_rsa.py
