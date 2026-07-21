#!/bin/bash
#SBATCH --job-name=exp30_m2
#SBATCH --account=m4641
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=02:00:00
#SBATCH --output=/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/study1/logs/exp30_%x_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/study1/logs/exp30_%x_%j.err

set -e
source /pscratch/sd/s/sjmoon/tribev2/.venv/bin/activate

MODEL="${1:-vjepa2_pretrained}"

cd /pscratch/sd/s/sjmoon/EmoBrain/project/dir3_ccn/study1/code
python -u 30_m2_emotion_encoding.py --model "$MODEL"

echo "Exp 30 M2 done for $MODEL."
