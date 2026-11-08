#!/bin/bash
# V-JEPA 2·CLIP 층별 캡션 겹침과 정서 예측 기여 (자극 수준, CPU 약 20분).
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/layer_overlap.py
