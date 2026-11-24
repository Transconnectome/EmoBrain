#!/bin/bash
# Build semantic emotion-name embeddings (all-mpnet-base-v2) used to initialise the
# decoder's label queries. CPU, seconds. Model is already in the local HF cache.
#   bash /pscratch/sd/s/sjmoon/EmoBrain/project/scripts/build_emotion_query_embeddings.sh
set -uo pipefail
cd /pscratch/sd/s/sjmoon/EmoBrain
export HF_HOME=/pscratch/sd/s/sjmoon/.cache/huggingface
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python \
    project/scripts/build_emotion_query_embeddings.py
