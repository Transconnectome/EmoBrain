#!/bin/bash
# S10 2-1 feature decoding 대 순열 기준(src/s10_feature_decoding.py). GPU 없음. login node CPU에서 참가자당 몇 분(순열 10,000회를 --threads로 나눔). 규칙은 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s10_feature_decoding.sh <S5 decoding 폴더 절대 경로> <출력 폴더 절대 경로> <동결 커밋> [--s6-dir <S6 결과 폴더>] [그 밖의 옵션]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
S5="${1:?S5 decoding 폴더}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?설계 동결 커밋}"; shift 3
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
"$PY" s10_feature_decoding.py --s5-dir "$S5" --out "$OUT" --design-freeze "$FREEZE" "$@"
