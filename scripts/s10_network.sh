#!/bin/bash
# S10 6-4a 묶음만으로 학습한 모델과 1-3 [사전](src/s10_network.py). GPU 없음, 몇 분. 13묶음 × A-1, C-1이 모두 있어야 최종 표를 낸다. 규칙은 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s10_network.sh <S6 작업 TSV 절대 경로> <출력 폴더 절대 경로> <동결 커밋> --network-bh-family by_model|pooled [--partial-check]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
JOBS="${1:?S6 작업 TSV}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?설계 동결 커밋}"; shift 3
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
"$PY" s10_network.py --jobs "$JOBS" --out "$OUT" --design-freeze "$FREEZE" "$@"
