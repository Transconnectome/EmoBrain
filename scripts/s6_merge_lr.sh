#!/bin/bash
# S6 두 실행(learning rate 1e-3 본 실행, 1e-4 실행)을 조건과 fold마다 검증 r로 합친다. GPU 없음, 몇 초. 규칙은 scripts/s6_merge_lr.py 머리말.
# 사용(레포 최상위): bash scripts/s6_merge_lr.sh <본 실행 폴더 절대 경로> <1e-4 실행 폴더 절대 경로> <합친 폴더 절대 경로> [--folds 1-6]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
MAIN="${1:?본 실행 폴더}"; SECOND="${2:?1e-4 실행 폴더}"; OUT="${3:?합친 폴더}"; shift 3
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1
"$PY" "$ROOT/scripts/s6_merge_lr.py" --main "$MAIN" --second "$SECOND" --out "$OUT" "$@"
