#!/bin/bash
# S10 D-4의 기준선: encoder 없이 D-4 정서 head와 같은 행(짝마다 held fold 영상)으로 학습한 ridge(src/s10_pair_ridge.py). CPU, 로그인 노드, 참가자당 몇 분.
# 사용(레포 최상위): bash scripts/s10_pair_ridge.sh <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
FREEZE="${1:?설계 동결 커밋}"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
OUT="$OUT_ROOT/s10_stats/D4_pair_ridge"
for s in 01 02 03 04 05; do
  "$PY" s10_pair_ridge.py fit --participant "$s" --out "$OUT" --design-freeze "$FREEZE" --threads 8
done
"$PY" s10_pair_ridge.py summarize --out "$OUT" --s6-final "$OUT_ROOT/s6_brain_final" --d4-root "$OUT_ROOT/s6_brain_grid_main" --control "$OUT_ROOT/s9_untrained_encoder"
