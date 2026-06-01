#!/bin/bash
# Phase 2 brain-only IV_subject_aware, task A_binary.
# Trained on BJ frozen features. Test = brain only (no video at inference).
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python code/phase2/brain_only/train_brain_subject_aware.py --task A_binary
