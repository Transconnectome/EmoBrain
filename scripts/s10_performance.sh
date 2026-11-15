#!/bin/bash
# S10 주 지표, 보조 지표, 2-3 비교, 0행 전제 검정(src/s10_performance.py)과 그림(src/s10_figures.py). GPU 없음, login node CPU에서 몇 분. 규칙은 두 파일의 머리말.
# 사용(레포 최상위): bash scripts/s10_performance.sh <S6 결과 폴더 절대 경로> <출력 폴더 절대 경로> <동결 커밋> [그 밖의 옵션]
# --dk-mean과 같은 내용 쌍 처리의 본 설정은 11/15 석진 님이 정했다(s10_performance.py 머리말)
set -euo pipefail
source "$(dirname "$0")/_env.sh"
S6="${1:?S6 결과 폴더}"; OUT="${2:?출력 폴더}"; FREEZE="${3:?설계 동결 커밋}"; shift 3
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
"$PY" s10_performance.py --s6-dir "$S6" --out "$OUT" --design-freeze "$FREEZE" "$@"
"$PY_CPU" s10_figures.py --out "$OUT"  # matplotlib이 있는 CPU Python(configs/env.sh의 EMOBRAIN_PYTHON_CPU)
