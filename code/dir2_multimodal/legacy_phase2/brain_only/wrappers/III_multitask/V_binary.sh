#!/bin/bash
# Phase 2 brain-only III_multitask, task V_binary.
# Trained on BJ frozen features. Test = brain only (no video at inference).
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python code/dir2_multimodal/legacy_phase2/brain_only/train_brain_multitask.py --task V_binary
