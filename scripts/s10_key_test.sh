#!/bin/bash
# S10 핵심 시험 첫 판(06 4절). 6-4d 저장값만 쓴다. CPU, 로그인 노드, 1분 안쪽. 레포 최상위에서 실행한다.
# 사용: bash scripts/s10_key_test.sh
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
"$PY_CPU" s10_key_test.py --stats "$OUT_ROOT/s10_stats/beyond_scene" --out "$OUT_ROOT/s10_stats/key_test_v1"
