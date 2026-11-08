#!/bin/bash
# V-JEPA 2 와 사람 캡션이 각각 잡아낸 것: 감정별 분할 그림, 저수준 특징 비교, 장면 개념 73개 예측 그림 (자극 수준, CPU 수 분).
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/feature_content_map.py
/pscratch/sd/s/sjmoon/swift_PTL2/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/feature_content_figures.py
