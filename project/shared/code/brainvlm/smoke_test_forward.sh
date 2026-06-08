#!/bin/bash
# Smoke test: single Horikawa fMRI → BrainVLM PatchEmbed forward (random init). ~30s. No GPU needed.
set -e
cd /pscratch/sd/s/sjmoon/FEELIN
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python code/brainvlm/smoke_test_forward.py
