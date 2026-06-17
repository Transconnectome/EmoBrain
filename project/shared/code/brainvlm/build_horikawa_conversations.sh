#!/bin/bash
# Build Horikawa conversation JSONL for BrainVLM training/inference.
# Requires: convert_horikawa_fmri.sh 가 먼저 돌아야 (fMRI .pt 파일 생성).
# ~30s on CPU.
set -e
cd /pscratch/sd/s/sjmoon/EmoBrain
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python \
    code/brainvlm/build_horikawa_conversations.py "$@"
