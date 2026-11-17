#!/bin/bash
# S10 MC 회상 분석(src/s10_imagery.py). GPU 없음. 6-3 전이 모델(A-1, C-1, seed 3개)에 회상 반응을 넣는다. login node에서 수십 분(어림). 질문과 판정은 01 6-3과 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s10_imagery.sh <s6_brain_final_for_mc> <s8_mc> <회상 반응 폴더> <vision_over_caption_index.tsv> <출력 폴더 절대 경로> <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=16 MKL_NUM_THREADS=16
cd "$ROOT/src"
"$PY" s10_imagery.py --final "${1:?final_for_mc}" --mc-dir "${2:?s8_mc}" --imagery-dir "${3:?회상 반응}" --vc-index "${4:?V/C 지수}" --out "${5:?출력 폴더}" --design-freeze "${6:?동결 커밋}"
