#!/bin/bash
#SBATCH --job-name=exp30_emo_enc
#SBATCH --account=m4641
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=01:30:00
#SBATCH --output=/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/study1/logs/exp30_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/study1/logs/exp30_%j.err

set -e
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

cd /pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/study1/code
python -u 30_emotion_encoding_subspace.py

echo "Exp 30 done."
