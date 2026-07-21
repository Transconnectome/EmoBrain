#!/bin/bash
# Phase 2 Direction 2: Brain → dinov2_pretrained encoding
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python project/dir2_multimodal/code/legacy_phase2/encoding_brain_to_video.py --video dinov2_pretrained
