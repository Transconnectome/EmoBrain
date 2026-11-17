#!/bin/bash
# 뇌 → 특징 디코딩 지표 (차원별 r·R², 영상별 프로필 상관, 두 영상 식별, 100개 중 top-1·top-5). 저장된 OOF 예측만 읽음, CPU 몇 분.
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/feature_decoding_metrics.py
