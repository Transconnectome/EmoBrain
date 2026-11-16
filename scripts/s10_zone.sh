#!/bin/bash
# S10 6-2 내용 구역 제외(src/s10_zone.py). GPU 없음, 1분 안팎. 60개 분할 × 두 조건이 모두 있어야 최종 표를 낸다. 규칙은 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s10_zone.sh <S6 구역 결과 폴더 절대 경로> <출력 폴더 절대 경로> <동결 커밋> [--constant-prediction-scope participant|all] [--partial-check]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
ZONE="${1:?S6 구역 결과 폴더}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?설계 동결 커밋}"; shift 3
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
"$PY" s10_zone.py --zone-dir "$ZONE" --out "$OUT" --design-freeze "$FREEZE" "$@"
