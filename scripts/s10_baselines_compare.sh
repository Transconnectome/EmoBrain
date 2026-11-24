#!/bin/bash
# S10 HK 뇌 모델 대 단순 모델, 선행 정서 decoder 비교(src/s10_baselines_compare.py). GPU 없음, 몇 분. 레포 최상위에서 실행한다.
# 사용: bash scripts/s10_baselines_compare.sh
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
"$PY" s10_baselines_compare.py --s6-dir "$OUT_ROOT/s6_brain_final" --s5-dir "$OUT_ROOT/s5_ridge" --out "$OUT_ROOT/s10_stats/2-3_baselines"
