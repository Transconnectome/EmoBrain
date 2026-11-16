#!/bin/bash
# S10 구조 비교와 민감도(src/s10_sensitivity.py). 다른 S6 결과 폴더의 두 모델을 같은 시험 행에서 비교한다. GPU 없음, login node CPU에서 몇 분. 규칙은 그 파일의 머리말.
# 사용(레포 최상위): bash scripts/s10_sensitivity.sh <출력 폴더 절대 경로> <동결 커밋> --pair "이름|A 폴더|A 조건|B 폴더|B 조건" [--pair ...] [그 밖의 옵션]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
OUT="${1:?출력 폴더}"; FREEZE="${2:?설계 동결 커밋}"; shift 2
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
"$PY" s10_sensitivity.py --out "$OUT" --design-freeze "$FREEZE" "$@"
