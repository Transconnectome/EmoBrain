#!/bin/bash
# S9 바꿔 끼우기의 Stimulus Model 기준선(src/s9_stimulus_swap.py). GPU 없음, 학습 없음, 몇 분. 이어서 s10_swap으로 통계를 낸다. 규칙은 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s9_stimulus_swap.sh <합친 S6 폴더 절대 경로> <출력 폴더 절대 경로> <동결 커밋> [--brain-swap-dir <뇌 모델 S9 swap 폴더>] [--s4-dir <S4 결과 폴더>] [--overwrite]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
S6="${1:?합친 S6 폴더}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?동결 커밋}"; shift 3
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
cd "$ROOT/src"
"$PY" s9_stimulus_swap.py --s6-dir "$S6" --out "$OUT" --design-freeze "$FREEZE" "$@"
