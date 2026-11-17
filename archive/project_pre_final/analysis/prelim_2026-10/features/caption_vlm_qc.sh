#!/bin/bash
# VLM 생성 캡션 점검 (검색 순위 + 단어 대조). CPU 몇 분. 확인 그림은 IDS="457,1004" bash caption_vlm_qc.sh sheets
# 새 캡션 점검: CAPTIONS=<captions.json> FEATURE=<임베딩 이름> OUT=<출력> COMPARE=<v1 captions.json> 로 바꾼다
set -euo pipefail
PY=/pscratch/sd/s/sjmoon/brainvlm_qwen_env/bin/python
CAPTIONS=${CAPTIONS:-/pscratch/sd/s/sjmoon/EmoViS/study1/results/00_embeddings/caption/captions.json}
BUNDLE=/pscratch/sd/s/sjmoon/transfer/emobrain_stimulus_features_20261025
FEAT=/pscratch/sd/s/sjmoon/transfer/emobrain_lab_features_20261026
VIDEOS=/pscratch/sd/s/sjmoon/EmoViS/data/raw/CowenEmotionVideos
OUT=${OUT:-/pscratch/sd/s/sjmoon/EmoBrain/project/output/prelim_2026-10/11_caption_qc}
FEATURE=${FEATURE:-caption_vlm_mpnet}
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
CMD=${1:-score}
if [ "$CMD" = sheets ]; then EXTRA=(--ids "$IDS"); [ -n "${COMPARE:-}" ] && EXTRA+=(--compare "$COMPARE"); else EXTRA=(--feature "$FEATURE"); fi
"$PY" /pscratch/sd/s/sjmoon/EmoBrain/project/analysis/prelim_2026-10/features/caption_vlm_qc.py "$CMD" \
  --captions "$CAPTIONS" --bundle "$BUNDLE" --feat "$FEAT" --videos "$VIDEOS" --out "$OUT" "${EXTRA[@]}"
