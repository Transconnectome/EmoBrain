#!/bin/bash
# Phase 2: Architecture B, task V_reg
# Brain BJ zero + Video CLIP pretrained, 5-fold × seeds (D=1, A/B=3).
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/dir2_multimodal/legacy_phase2/train_supervised.py --arch B --task V_reg
