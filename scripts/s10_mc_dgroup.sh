#!/bin/bash
# S10 6-3 MC 전이 확장: D-3, D-4를 A-1, C-1(seed 0)과 비교. CPU, 로그인 노드, 1분 안쪽. s10_performance가 torch를 불러서 $PY(s10_mc.sh와 같음)로 돈다. 레포 최상위에서 실행한다.
# 사용: bash scripts/s10_mc_dgroup.sh
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
"$PY" s10_mc_dgroup.py --mc-dir "$OUT_ROOT/s8_mc" --out "$OUT_ROOT/s10_stats/6-3_mc_dgroup"
# 11/18 B-1을 더한 판(C-1 − B-1, B-1 − A-1). B-1의 MC 전이 6명이 다 끝났을 때만
if [ "$(ls "$OUT_ROOT"/s8_mc/brain_only_featdec/seed0/mc-0{1,2,3,4,5,6}/done.json 2>/dev/null | wc -l)" -eq 6 ]; then
  "$PY" s10_mc_dgroup.py --mc-dir "$OUT_ROOT/s8_mc" --out "$OUT_ROOT/s10_stats/6-3_mc_b1" --with-b1
fi
