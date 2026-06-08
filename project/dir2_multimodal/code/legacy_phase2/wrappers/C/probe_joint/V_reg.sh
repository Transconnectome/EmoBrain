#!/bin/bash
# Phase 2 Arch C Stage 2: linear probe on joint features for V_reg
# Requires stage1_align.sh 완료 후 aligner_fold*_seed*.pt 존재해야 함.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python project/dir2_multimodal/code/legacy_phase2/probe_contrastive.py --task V_reg --probe_input joint
