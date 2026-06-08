#!/bin/bash
# Phase 2 brain-only I_supervised, task V_binary.
# Trained on BJ frozen features. Test = brain only (no video at inference).
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python project/dir2_multimodal/code/legacy_phase2/brain_only/train_brain_supervised.py --task V_binary
