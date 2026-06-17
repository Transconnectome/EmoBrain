#!/bin/bash
# Phase 2: Architecture D, task A_binary
# Brain BJ zero + Video CLIP pretrained, 5-fold × seeds (D=1, A/B=3).
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python project/dir2_multimodal/code/legacy_phase2/train_supervised.py --arch D --task A_binary
