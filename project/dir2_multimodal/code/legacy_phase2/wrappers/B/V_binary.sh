#!/bin/bash
# Phase 2: Architecture B, task V_binary
# Brain BJ zero + Video CLIP pretrained, 5-fold × seeds (D=1, A/B=3).
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python project/dir2_multimodal/code/legacy_phase2/train_supervised.py --arch B --task V_binary
