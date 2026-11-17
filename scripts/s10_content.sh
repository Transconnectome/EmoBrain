#!/bin/bash
# S10 정서마다 뇌 decoder가 기대는 장면 내용(src/s10_content.py). GPU 없음. 저장된 시험 예측만 읽는다. login node에서 몇 분. 기술 분석, 판정 없음.
# 사용(레포 최상위): bash scripts/s10_content.sh <s6_brain_final> <final_2026-11 폴더> <출력 폴더 절대 경로> <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=8
cd "$ROOT/src"
"$PY" s10_content.py --s6-dir "${1:?S6 최종}" --net-root "${2:?묶음 학습 폴더의 위}" --out "${3:?출력 폴더}" --design-freeze "${4:?동결 커밋}"
