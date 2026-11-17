#!/bin/bash
# S10 6-3의 ridge 기준선(src/s10_mc_ridge.py). GPU 없음. MC 참가자 6명, 몇 분. 규칙은 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s10_mc_ridge.sh <s8_mc 폴더> <출력 폴더 절대 경로> <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=16 MKL_NUM_THREADS=16
cd "$ROOT/src"
"$PY" s10_mc_ridge.py --mc-dir "${1:?s8_mc 폴더}" --out "${2:?출력 폴더}" --design-freeze "${3:?동결 커밋}" --threads 16
