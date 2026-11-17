#!/bin/bash
# Pack Horikawa per-stim frames → BrainVLM-format 4D tensor per (subject, stim).
# 5 subj × 2185 stim = 10925 .pt files (~150KB each ≈ 1.6GB total).
# ~30-60 min on CPU.
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python \
    code/brainvlm/convert_horikawa_fmri.py "$@"
