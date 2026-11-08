#!/bin/bash
# 같은 대상(맥락) 안에서 저수준 특징이 정서를 가르는지 (맥락 8개 × 감정 4개, null 200회, CPU 수십 분).
set -euo pipefail
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/within_context_lowlevel.py
