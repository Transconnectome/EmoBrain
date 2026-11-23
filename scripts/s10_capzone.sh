#!/bin/bash
# S10 Dec-바 요약(src/s10_capzone.py): 캡션 구역 제외 분할에서 A-1, C-1, D-3, D-4를 6-2와 같은 규칙으로 요약. GPU 없음, 로그인 노드 CPU.
# 사용(레포 최상위): bash scripts/s10_capzone.sh <동결 커밋> [그 밖의 옵션, ex) --n-boot 200 --overwrite]
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
FREEZE="${1:?설계 동결 커밋}"; shift
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
"$PY" s10_capzone.py --capzone-dir "$OUT_ROOT/s6_brain_capzone" --out "$OUT_ROOT/s10_stats/capzone_models" --design-freeze "$FREEZE" "$@"
