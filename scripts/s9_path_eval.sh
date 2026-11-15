#!/bin/bash
# S9 경로 평가(K1)와 14개 차원판(K1a)의 예측(src/s9_path_eval.py). 고정한 Stimulus Model head에 ridge와 C-1 decoded features를 넣는다. GPU 없음, 학습 없음.
# login node CPU에서 몇 분(입력 sha256과 head 계산). 규칙은 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s9_path_eval.sh <S4 결과 폴더 절대 경로> <S5 decoding 폴더 절대 경로> <S6 결과 폴더 절대 경로> <출력 폴더 절대 경로> <동결 커밋> [--partial-check] [--overwrite]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
S4="${1:?S4 결과 폴더}"; S5="${2:?S5 decoding 폴더}"; S6="${3:?S6 결과 폴더}"; OUT="${4:?출력 폴더}"; FREEZE="${5:?설계 동결 커밋}"; shift 5
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
"$PY" s9_path_eval.py --s4-dir "$S4" --s5-dir "$S5" --s6-dir "$S6" --out "$OUT" --design-freeze "$FREEZE" "$@"
