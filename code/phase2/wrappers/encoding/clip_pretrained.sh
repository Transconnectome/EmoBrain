#!/bin/bash
# Phase 2 Direction 2: Brain → clip_pretrained encoding
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/phase2/encoding_brain_to_video.py --video clip_pretrained
