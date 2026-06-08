#!/bin/bash
# Phase 1 Cat34 probes (multilabel + soft) on Brain-JEPA + SwiFT NewE96 + NeuroSTORM.
# Best canonical setting: zero padding (matches main grid), linear + MLP heads,
# pooled + per_subject modes, 5 folds, 3 seeds (MLP).
set -e
cd /pscratch/sd/s/sjmoon/FEELIN

LOG=/pscratch/sd/s/sjmoon/FEELIN/project/shared/output/slurm/cat34_phase1.log
mkdir -p $(dirname $LOG)

# Linear only first (~70 min). MLP adds ~6 hr if needed.
# Override --skip_mlp to add MLP back.
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python -u code/probes/run_unified_probe.py \
    --tasks Cat34_multilabel,Cat34_soft \
    --features Brain-JEPA,SwiFT_NewE96,NeuroSTORM \
    --folds 1,2,3,4,5 \
    --seeds 0 \
    --skip_mlp \
    --out_csv /pscratch/sd/s/sjmoon/FEELIN/project/shared/results/background/phase1/cat34_probe_linear.csv \
    2>&1 | tee $LOG
