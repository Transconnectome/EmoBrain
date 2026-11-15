#!/bin/bash
# S10 6-4b 네트워크 단위 입력 교란(src/s10_perturb.py). GPU 없음, 몇 초. 6 fold가 모두 있어야 최종 표를 낸다. 규칙은 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s10_perturb.sh <S9 perturb 폴더 절대 경로> <출력 폴더 절대 경로> <동결 커밋> [--s6-dir <S6 결과 폴더>] [--partial-check]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
PERT="${1:?S9 perturb 폴더}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?설계 동결 커밋}"; shift 3
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=4
"$PY" s10_perturb.py --perturb-dir "$PERT" --out "$OUT" --design-freeze "$FREEZE" "$@"
