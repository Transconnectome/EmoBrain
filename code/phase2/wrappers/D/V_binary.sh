#!/bin/bash
# Phase 2: Architecture D, task V_binary
# Brain BJ zero + Video CLIP pretrained, 5-fold × seeds (D=1, A/B=3).
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/phase2/train_supervised.py --arch D --task V_binary
