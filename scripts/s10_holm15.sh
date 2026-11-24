#!/bin/bash
# [사전] 15개 Holm 보정(src/s10_holm15.py). GPU 없음, 몇 초. 15개가 다 모이지 않으면 없는 것을 적고 보정 값을 내지 않는다.
# 사용(레포 최상위): bash scripts/s10_holm15.sh <출력 파일 절대 경로> <p 파일 절대 경로>... [--seed 0] [--alpha <값>]
set -euo pipefail
source "$(dirname "$0")/_env.sh"
OUT="${1:?출력 파일}"; shift
INPUTS=(); while [ $# -gt 0 ] && [ "${1:0:2}" != "--" ]; do INPUTS+=("$1"); shift; done
[ ${#INPUTS[@]} -gt 0 ] || { echo "p 파일을 하나 이상 준다" >&2; exit 1; }
"$PY_CPU" s10_holm15.py --inputs "${INPUTS[@]}" --out "$OUT" "$@"
