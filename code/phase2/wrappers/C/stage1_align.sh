#!/bin/bash
# Phase 2 Arch C Stage 1: contrastive alignment (5 fold × 3 seed = 15 aligner ckpts)
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/phase2/train_contrastive.py
