#!/bin/bash
# S10 6-3 MC 시청 전이(src/s10_mc.py). GPU 없음, 몇 초. 두 조건 × seed 3개 × MC 6명이 모두 있어야 최종 표를 낸다. 규칙은 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s10_mc.sh <S8 결과 폴더 절대 경로> <출력 폴더 절대 경로> <동결 커밋> [--constant-prediction-scope unit|all] [--partial-check] [--allow-check-run]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
MC="${1:?S8 결과 폴더}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?설계 동결 커밋}"; shift 3
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=4
"$PY" s10_mc.py --mc-dir "$MC" --out "$OUT" --design-freeze "$FREEZE" "$@"
