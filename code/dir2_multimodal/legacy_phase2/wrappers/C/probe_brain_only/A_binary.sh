#!/bin/bash
# Phase 2 Arch C Stage 2: linear probe on brain_only features for A_binary
# Requires stage1_align.sh 완료 후 aligner_fold*_seed*.pt 존재해야 함.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python code/dir2_multimodal/legacy_phase2/probe_contrastive.py --task A_binary --probe_input brain_only
