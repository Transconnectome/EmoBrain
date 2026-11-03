#!/bin/bash
# 채도·밝기 조작 빠른 확인판, 영상·이미지 모델 일곱 개 (영상 79개 × 조작 9개). GPU 1장 약 20~40분.
# MODELS 로 줄일 수 있음. siglip2_2fps 는 본 추출이 merge 된 뒤에 넣는다.
set -euo pipefail
export HF_HOME=/pscratch/sd/s/sjmoon/.cache/huggingface HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
mkdir -p /pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/perturbation
/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/perlmutter/perturb_quick_models.py \
  --models "${MODELS:-vjepa2_win,videomae_win,timesformer,xclip,clip_2fps,dinov2_2fps,siglip2_2fps}" --device "${DEVICE:-cuda}" \
  2>&1 | tee /pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/perturbation/quick_models.log
