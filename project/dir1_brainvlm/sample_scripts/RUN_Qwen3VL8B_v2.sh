#!/bin/bash
# ============================================================================
# Qwen3-VL-8B-Instruct. VA binary + VA regression 의 통합 launcher.
# 한 sh = 한 모델. 내부 에서 binary, regression 순차 실행.
# 단일 launch 명령. bash RUN_Qwen3VL8B_v2.sh
# ============================================================================

set -euo pipefail

D1=/pscratch/sd/s/sjmoon/EmoBrain/project/dir1_brainvlm

echo "=========================================="
echo "[Qwen3-VL-8B v2] VA binary start"
echo "=========================================="
bash ${D1}/sample_scripts/UMBRELLA_ROI_Horikawa_Emotion_VA_binary_Qwen3VL8B_v2.sh

echo "=========================================="
echo "[Qwen3-VL-8B v2] VA regression start"
echo "=========================================="
bash ${D1}/sample_scripts/UMBRELLA_ROI_Horikawa_Emotion_VA_regression_Qwen3VL8B_v2.sh

echo "=========================================="
echo "[Qwen3-VL-8B v2] all done"
echo "=========================================="
