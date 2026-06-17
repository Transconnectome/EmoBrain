#!/bin/bash
# Direction 2 pilot training. Brain-JEPA scratch + V-JEPA2 + SigLIP + GRL.
# Fold 1, 40 epoch, 1 seed. Same hyper-parameters as the resting pilot for
# a fair comparison.
#SBATCH --job-name=emobrain_d2_pilot_scratch
#SBATCH --output=/pscratch/sd/s/sjmoon/FEELIN/project/shared/output/logs/d2_pilot_scratch_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/FEELIN/project/shared/output/logs/d2_pilot_scratch_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --time=01:00:00
#SBATCH --account=m4641
#SBATCH --qos=regular
#SBATCH --constraint=gpu

set -euo pipefail

VENV=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
SCRIPT=/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/code/alignment_pilot/code/train/train_align.py
OUT=/pscratch/sd/s/sjmoon/FEELIN/project/dir3_ccn/code/alignment_pilot/output/pilot_scratch_fold1

mkdir -p "$OUT" /pscratch/sd/s/sjmoon/FEELIN/project/shared/output/logs

"$VENV" -u "$SCRIPT" \
    --brain_variant scratch \
    --fold 1 \
    --out_dir "$OUT" \
    --epoch 40 \
    --batch 256 \
    --lr 1e-4 \
    --weight_decay 1e-4 \
    --lambda_adv 0.1 \
    --adv_warmup_epoch 5 \
    --seed 0
