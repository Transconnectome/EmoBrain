#!/bin/bash
# Verify BrainVLM env (no GPU needed for most checks). ~1-2 min.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python code/brainvlm/verify_env.py
