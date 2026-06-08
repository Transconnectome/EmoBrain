#!/bin/bash
# Phase 1 의 모든 probe sequential 실행 (fallback. 보통 wrapper 들을 GPU 별로 병렬 실행).
# 예상 시간: 4-6h on 1 GPU.
set -e
SCRIPT_DIR=/pscratch/sd/s/sjmoon/FEELIN/project/shared/code/probes/wrappers
for w in "$SCRIPT_DIR"/bfm/*.sh "$SCRIPT_DIR"/video/*.sh; do
  echo ""
  echo "========================================================================"
  echo "[$(date +%H:%M:%S)] Running: $w"
  echo "========================================================================"
  bash "$w"
done
echo ""
echo "[$(date +%H:%M:%S)] All Phase 1 probes done."
