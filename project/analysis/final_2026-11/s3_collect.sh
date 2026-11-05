#!/bin/bash
# S3 조각 모으기와 확인. 가벼운 계산이라 로그인 노드에서 돌려도 된다. 사용: bash s3_collect.sh vjepa2 videomae timesformer clip lowlevel deberta
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
cd /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/final_2026-11
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python s3_collect.py "$@"
