#!/bin/bash
# 정서 평정의 네 부분 (시각에만·둘 다·캡션에만·나머지) 을 뇌 영역 묶음 24개 + 뇌 전체마다 디코딩 (피험자 5명, CPU 20분 안팎).
# 사용: bash hierarchy_components.sh --visual "V-JEPA 2 + DINOv2"   (시각 묶음 선택, 기본 "V-JEPA 2"; --stimulus-only 는 자극 수준 분해만)
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/hierarchy_components.py "$@"
