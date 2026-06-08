#!/bin/bash
#SBATCH --job-name=feel_subject_invariant
#SBATCH --output=/pscratch/sd/s/sjmoon/FEELIN/output/slurm/ssl_pretrain/subject_invariant_%x_%j.out
#SBATCH --error=/pscratch/sd/s/sjmoon/FEELIN/output/slurm/ssl_pretrain/subject_invariant_%x_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus=1
#SBATCH --time=01:00:00
#SBATCH --account=m5187_g
#SBATCH --qos=regular
#SBATCH --constraint=gpu
#
# FEEL Phase 3b Track A. Subject-invariant SSL pretrain on Horikawa.
#
# Usage.
#   # local smoke (1 epoch dry run, no SLURM)
#   bash subject_invariant.sh smoke
#
#   # SLURM full run, default config (linear head, fold 1, 100 epoch)
#   sbatch subject_invariant.sh
#
#   # SLURM ablation (MLP head)
#   sbatch --export=HEAD=mlp subject_invariant.sh
#
#   # SLURM all 5 fold
#   for f in 1 2 3 4 5; do sbatch --export=FOLD=$f subject_invariant.sh; done
#
set -e

FEEL=/pscratch/sd/s/sjmoon/FEELIN
PY=/pscratch/sd/s/sjmoon/tribev2/.venv/bin/python
SCRIPT=$FEEL/code/ssl_pretrain/subject_invariant.py

MODE=${1:-full}

# Defaults (overridable via --export=VAR=value).
BFM=${BFM:-brain_jepa_resting_pad-mean}
HEAD=${HEAD:-linear}
OUT_DIM=${OUT_DIM:-256}
TAU=${TAU:-0.07}
BATCH=${BATCH:-256}
EPOCHS=${EPOCHS:-100}
LR=${LR:-1e-4}
FOLD=${FOLD:-1}
SEED=${SEED:-0}

mkdir -p $FEEL/output/slurm/ssl_pretrain

if [ "$MODE" = "smoke" ]; then
    # Quick local sanity run (1 epoch, no SLURM).
    echo "===== SMOKE TEST ====="
    $PY $SCRIPT \
        --bfm $BFM --head $HEAD --out_dim $OUT_DIM \
        --temperature $TAU --batch_size 64 \
        --epochs 1 --fold $FOLD --seed $SEED --eval_every 1
    exit 0
fi

echo "===== FULL RUN ====="
echo "BFM=$BFM HEAD=$HEAD OUT_DIM=$OUT_DIM TAU=$TAU BATCH=$BATCH EPOCHS=$EPOCHS LR=$LR FOLD=$FOLD SEED=$SEED"

$PY $SCRIPT \
    --bfm $BFM --head $HEAD --out_dim $OUT_DIM \
    --temperature $TAU --batch_size $BATCH \
    --epochs $EPOCHS --lr $LR \
    --fold $FOLD --seed $SEED
