#!/bin/bash
# S3 캡션을 물체, 물체 + 속성 수준으로 나눈 Caption feature(06 14절 4번). 레포 최상위에서 실행한다.
#   bash scripts/s3_caption_levels.sh prep   : export(CPU)와 parse(spaCy 환경 EMOBRAIN_SPACY_PYTHON, 기본 /pscratch/sd/s/sjmoon/envs/nlp_spacy). 수 분
#   bash scripts/s3_caption_levels.sh embed  : DeBERTa-large 임베딩(GPU 한 장, 수 분). GPU가 빈 로그인 노드에서
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
WORK="$OUT_ROOT/s3_features/caption_levels_work"
SPACY_PY="${EMOBRAIN_SPACY_PYTHON:-/pscratch/sd/s/sjmoon/envs/nlp_spacy/bin/python}"
export HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
case "${1:?prep 또는 embed}" in
  prep)  "$PY_CPU" s3_caption_levels.py export --out "$WORK"; "$SPACY_PY" s3_caption_levels.py parse --out "$WORK" ;;
  embed) "$PY" s3_caption_levels.py embed --out "$WORK" --device cuda ;;
esac
