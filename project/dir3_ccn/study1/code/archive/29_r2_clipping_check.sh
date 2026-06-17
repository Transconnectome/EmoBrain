#!/bin/bash
#SBATCH --job-name=exp29_r2_clip
#SBATCH --account=m4641
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=02:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/study1/logs/exp29_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/study1/logs/exp29_%j.err

set -e
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

cd /pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/study1/code
python -u 29_r2_clipping_check.py

echo "Exp 29 done."
