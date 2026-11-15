#!/bin/bash
# S10 경로 평가(K1)와 14개 차원 표(B4, K1a)(src/s10_k1.py). GPU 없음. login node CPU에서 1분 안팎(영상 단위 bootstrap 10,000회). 규칙은 파이썬 파일 머리말.
# S4 결과 폴더는 S9와 같은 기본값(<output_root>/s4_no_brain)이다.
# 사용(레포 최상위): bash scripts/s10_k1.sh <S9 경로 평가 폴더> <S6 결과 폴더> <S5 ridge 폴더> <출력 폴더> <동결 커밋> [--partial-check] [--overwrite]. 경로는 모두 절대 경로
set -euo pipefail
source "$(dirname "$0")/_env.sh"
S9="${1:?S9 경로 평가 폴더}"; S6="${2:?S6 결과 폴더}"; RIDGE="${3:?S5 ridge 폴더}"; OUT="${4:?출력 폴더}"; FREEZE="${5:?설계 동결 커밋}"; shift 5
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
"$PY" s10_k1.py --path-eval-dir "$S9" --s6-dir "$S6" --s5-ridge-dir "$RIDGE" --out "$OUT" --design-freeze "$FREEZE" "$@"
