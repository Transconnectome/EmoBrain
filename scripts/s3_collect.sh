#!/bin/bash
# S3 조각 모으기와 확인. 가벼운 계산이라 로그인 노드에서 돌려도 된다. 사용: bash s3_collect.sh vjepa2 videomae timesformer clip lowlevel deberta
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export PYTHONDONTWRITEBYTECODE=1
"$PY" s3_collect.py "$@"
