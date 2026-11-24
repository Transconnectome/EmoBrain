#!/bin/bash
# S10 회상 질문 3의 예측 변수(정서마다 Vision 대 Caption 지수, 01 6-3). CPU, 로그인 노드, 1초. 레포 최상위에서 실행한다.
# 고정한 s10_stats/imagery_prereg/vision_over_caption_index.tsv가 있으면 덮어쓰지 않고 바이트 단위로 같은지만 확인한다.
# 사용: bash scripts/s10_imagery_prereg.sh [출력 폴더 절대 경로]
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
"$PY_CPU" s10_imagery_prereg.py --stats "$OUT_ROOT/s10_stats/beyond_scene" ${1:+--out "$1"}
