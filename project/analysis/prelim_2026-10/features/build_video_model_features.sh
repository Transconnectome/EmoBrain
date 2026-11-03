#!/bin/bash
#SBATCH -A m5187_g -C gpu -q regular -N 1 --gpus-per-node=4 -t 04:00:00 -J video_models
#SBATCH -o /pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/video_models/slurm_%j.out
# 영상·이미지 모델 특징을 같은 시간 정보로 다시 뽑기 (build_video_model_features.py).
#   MODEL=vjepa2_win bash build_video_model_features.sh generate     GPU 1장. 다른 모델: videomae_win timesformer xclip clip_2fps dinov2_2fps siglip2_2fps
#   MODEL=vjepa2_win bash build_video_model_features.sh merge        CPU
#   여러 노드로 나누기: SHARD=0 NSHARDS=2 MODEL=... bash ... generate (노드마다 SHARD 를 다르게)
#   조작 실험: MODEL=clip_2fps bash build_video_model_features.sh perturb    영상 240개 × 조작 12종 (PERTURBS 로 줄일 수 있음), 끝나면 합침
# 캐시에 없는 xclip·siglip2_2fps 는 처음 실행 때 내려받는다 (각 약 1.5 GB). timesformer 는 전처리 설정 파일만 받는다.
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
CODE=/pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/features/build_video_model_features.py
LOG=/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/logs/video_models
export HF_HOME=/pscratch/sd/s/sjmoon/.cache/huggingface
mkdir -p "$LOG"
: "${MODEL:?MODEL 을 정하세요}"
case "$MODEL" in xclip|siglip2_2fps|timesformer) ;; *) export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 ;; esac
case "${1:-}" in
  generate) "$PY" "$CODE" generate --model "$MODEL" --shard "${SHARD:-0}" --nshards "${NSHARDS:-1}" --device "${DEVICE:-cuda}" \
              2>&1 | tee -a "$LOG/${MODEL}_shard${SHARD:-0}of${NSHARDS:-1}.log" ;;
  merge) "$PY" "$CODE" merge --model "$MODEL" 2>&1 | tee "$LOG/${MODEL}_merge.log" ;;
  perturb)
    for p in ${PERTURBS:-bright_0.6 bright_1.4 sat_0 sat_0.5 sat_1.5 contrast_0.6 contrast_1.4 hue_90 blur_3 reverse shuffle freeze}; do
      "$PY" "$CODE" generate --model "$MODEL" --perturb "$p" --device "${DEVICE:-cuda}" 2>&1 | tee -a "$LOG/${MODEL}__perturb.log"
      "$PY" "$CODE" merge --model "$MODEL" --perturb "$p" 2>&1 | tee -a "$LOG/${MODEL}__perturb.log"
    done ;;
  *) echo "사용: MODEL=<이름> bash $0 generate|merge|perturb"; exit 1 ;;
esac
