#!/bin/bash
# S10 2-2 바꿔 끼우기, 1-1, 1-2 (나)(src/s10_swap.py). GPU 없음. login node CPU에서 seed당 몇 분(짝 연결 묶음 bootstrap 10,000회). 규칙은 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s10_swap.sh <S9 swap 폴더 절대 경로> <출력 폴더 절대 경로> <동결 커밋> [그 밖의 옵션]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
SWAP="${1:?S9 swap 폴더}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?설계 동결 커밋}"; shift 3
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
"$PY" s10_swap.py --swap-dir "$SWAP" --out "$OUT" --design-freeze "$FREEZE" "$@"
