#!/bin/bash
# S10 정서별 모델 비교(src/s10_per_emotion.py). GPU 없음. 저장된 시험 예측만 읽는다. login node에서 몇 분. 질문과 판정은 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s10_per_emotion.sh <S6 최종 결과 폴더> <s8_mc 폴더> <vision_over_caption_index.tsv> <출력 폴더 절대 경로> <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=16 MKL_NUM_THREADS=16
cd "$ROOT/src"
"$PY" s10_per_emotion.py --s6-dir "${1:?S6 결과 폴더}" --mc-dir "${2:?s8_mc 폴더}" --vc-index "${3:?V/C 지수 파일}" --out "${4:?출력 폴더}" --design-freeze "${5:?동결 커밋}"
