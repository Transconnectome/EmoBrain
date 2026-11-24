#!/bin/bash
# S10 네트워크 교란 모델 확장의 통계와 정서 head 입력 표현 유사도(src/s10_perturb_models.py). GPU 없음. 참가자 5명을 프로세스 5개로, login node에서 수십 분(어림). 질문과 판정은 파이썬 파일 머리말.
# 사용(레포 최상위): bash scripts/s10_perturb_models.sh <s9_perturb_models 출력> <6-4b S9 perturb 폴더> <출력 폴더 절대 경로> <동결 커밋>
set -euo pipefail
HERE="${SLURM_SUBMIT_DIR:+$SLURM_SUBMIT_DIR/scripts}"; source "${HERE:-$(dirname "$0")}/_env.sh"
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=6 OPENBLAS_NUM_THREADS=6 MKL_NUM_THREADS=6
cd "$ROOT/src"
"$PY" s10_perturb_models.py --perturb-dir "${1:?S9 출력}" --s9-dir "${2:?6-4b S9 폴더}" --out "${3:?출력 폴더}" --design-freeze "${4:?동결 커밋}" --workers 5
